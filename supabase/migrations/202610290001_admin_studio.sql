-- Fretline Admin Studio. Run as project owner in Supabase SQL Editor.
-- Idempotent schema setup. No default account, password or secret is created.
begin;
create table if not exists public.brands (
  id text primary key, name text not null unique, metadata jsonb not null default '{}'
);
create table if not exists public.admin_users (
  user_id uuid primary key references auth.users(id), active boolean not null default true,
  created_at timestamptz not null default now()
);
create table if not exists public.guitars (
  id text primary key check (id ~ '^[a-z0-9]+(-[a-z0-9]+)*$' and length(id) between 3 and 120
    and id not in ('constructor','prototype','__proto__')),
  brand_id text references public.brands(id), draft jsonb not null,
  published jsonb, status text not null default 'draft' check (status in ('draft','published','hidden')),
  revision bigint not null default 1, position integer not null default 100000,
  updated_by uuid references auth.users(id), created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(), published_at timestamptz,
  check (jsonb_typeof(draft)='object' and draft->>'id'=id),
  check (published is null or (jsonb_typeof(published)='object' and published->>'id'=id)),
  check (status <> 'published' or published is not null)
);
create table if not exists public.guitar_specifications (
  guitar_id text primary key references public.guitars(id), specs jsonb not null default '{}',
  source jsonb, updated_at timestamptz not null default now(), check (jsonb_typeof(specs)='object')
);
create table if not exists public.guitar_prices (
  id bigint generated always as identity primary key, guitar_id text not null references public.guitars(id),
  amount numeric(12,2) check (amount is null or amount>0), currency text not null default 'THB' check(currency='THB'),
  source jsonb, checked_on date, changed_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create table if not exists public.guitar_images (
  id uuid primary key default gen_random_uuid(), guitar_id text not null references public.guitars(id),
  storage_path text not null unique, metadata jsonb not null default '{}',
  created_by uuid references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.audit_logs (
  id bigint generated always as identity primary key, actor uuid references auth.users(id),
  guitar_id text references public.guitars(id), action text not null, before_data jsonb, after_data jsonb,
  created_at timestamptz not null default now()
);
create table if not exists public.catalog_state (
  singleton boolean primary key default true check(singleton), ready boolean not null default false
);
insert into public.catalog_state(singleton) values(true) on conflict do nothing;
create index if not exists guitars_status_position on public.guitars(status,position);
create index if not exists guitar_prices_history on public.guitar_prices(guitar_id,id desc);
create index if not exists audit_logs_guitar on public.audit_logs(guitar_id,id desc);

create or replace function public.fretline_is_admin() returns boolean
language sql stable security definer set search_path='' as $$
  select exists(select 1 from public.admin_users where user_id=auth.uid() and active);
$$;

-- Validation is also enforced at the database boundary; client validation is UX only.
create or replace function public.fretline_validate_guitar(d jsonb, for_publish boolean default false)
returns void language plpgsql set search_path='' as $$
declare k text; v jsonb; im jsonb; num numeric;
begin
  if jsonb_typeof(d) is distinct from 'object' or length(d::text)>500000 then raise exception 'Invalid product data'; end if;
  if coalesce(d->>'id','') !~ '^[a-z0-9]+(-[a-z0-9]+)*$' or length(d->>'id') not between 3 and 120
    or d->>'id' in ('constructor','prototype','__proto__') then raise exception 'Invalid product ID'; end if;
  if coalesce(d->>'category','') not in ('electric','acoustic','classical','bass') then raise exception 'Invalid guitar type'; end if;
  if not exists(select 1 from public.brands where name=d->>'brand') then raise exception 'Unknown brand'; end if;
  if jsonb_typeof(d->'specs') is distinct from 'object' or jsonb_typeof(d->'gallery') is distinct from 'array'
    or jsonb_array_length(d->'gallery')>30 then raise exception 'Invalid specifications or gallery'; end if;
  for k,v in select * from jsonb_each(d->'specs') loop
    if v='null'::jsonb then continue; end if;
    if jsonb_typeof(v) not in ('string','number') or length(v::text)>4000 then raise exception 'Invalid specification: %',k; end if;
    if k in ('strings','frets','scale','scaleMm','nutWidthMm','fingerboardRadiusMm','weightKg') then
      if jsonb_typeof(v)<>'number' then raise exception 'Expected numeric specification: %',k; end if;
      num := v::text::numeric;
      if num<0 or (num=0 and k<>'frets') or num>10000 or (k in ('strings','frets') and num<>trunc(num)) then
        raise exception 'Invalid numeric specification: %',k;
      end if;
    end if;
  end loop;
  if coalesce(d->'price','null'::jsonb)<>'null'::jsonb then
    if jsonb_typeof(d->'price')<>'number' then raise exception 'Price must be a number'; end if;
    num := (d->>'price')::numeric;
    if num<=0 or num>9999999999 or num<>round(num,2) then raise exception 'Price must be positive THB'; end if;
    if coalesce(d#>>'{priceSource,currency}','')<>'THB' or coalesce(d#>>'{priceSource,url}','') !~ '^https?://[^ /]+'
      or coalesce(d#>>'{priceSource,verifiedOn}','') !~ '^\d{4}-\d{2}-\d{2}$' then raise exception 'Price requires a source and verification date'; end if;
    perform (d#>>'{priceSource,verifiedOn}')::date;
    if (d#>>'{priceSource,verifiedOn}')::date>current_date then raise exception 'Price verification date is in the future'; end if;
  end if;
  for im in select * from jsonb_array_elements(d->'gallery') loop
    if jsonb_typeof(im)<>'object' then raise exception 'Invalid image'; end if;
    if im ? 'storagePath' then
      if not exists(select 1 from public.guitar_images where guitar_id=d->>'id' and storage_path=im->>'storagePath')
        or not exists(select 1 from storage.objects where bucket_id='guitar-images' and name=im->>'storagePath') then
        raise exception 'Image does not belong to this product'; end if;
    elsif im ? 'legacyIndex' then
      if not exists(select 1 from public.guitars where id=d->>'id' and exists(
        select 1 from jsonb_array_elements(coalesce(published->'gallery','[]')) old
        where old->'legacyIndex'=im->'legacyIndex')) then raise exception 'Unknown original image'; end if;
    else raise exception 'Image must be registered'; end if;
  end loop;
  if for_publish then
    if length(trim(coalesce(d->>'name','')))<1 or length(d->>'name')>250 then raise exception 'Model name is required'; end if;
    if exists(select 1 from jsonb_each(d->'specs') where value<>'null'::jsonb and value<>'""'::jsonb)
      or d->>'price' is not null then
      if coalesce(d#>>'{source,url}','') !~ '^https?://[^ /]+' or coalesce(d#>>'{source,verifiedOn}','') !~ '^\d{4}-\d{2}-\d{2}$'
        then raise exception 'Specifications require a source and verification date'; end if;
      perform (d#>>'{source,verifiedOn}')::date;
      if (d#>>'{source,verifiedOn}')::date>current_date then raise exception 'Specification date is in the future'; end if;
    end if;
  end if;
end;
$$;

create or replace function public.admin_save_guitar(p_data jsonb, p_expected_revision bigint default null)
returns jsonb language plpgsql security definer set search_path='' as $$
declare old public.guitars; saved public.guitars;
begin
  if not public.fretline_is_admin() then raise exception 'Admin access required' using errcode='42501'; end if;
  perform public.fretline_validate_guitar(p_data,false);
  select * into old from public.guitars where id=p_data->>'id' for update;
  if found then
    if p_expected_revision is null or old.revision<>p_expected_revision then raise exception 'CONFLICT: reload the latest product' using errcode='40001'; end if;
    update public.guitars set draft=p_data,brand_id=(select id from public.brands where name=p_data->>'brand'),
      revision=revision+1,updated_at=now(),updated_by=auth.uid() where id=old.id returning * into saved;
  else
    if p_expected_revision is not null then raise exception 'Product no longer exists'; end if;
    insert into public.guitars(id,brand_id,draft,updated_by) values(p_data->>'id',
      (select id from public.brands where name=p_data->>'brand'),p_data,auth.uid()) returning * into saved;
  end if;
  insert into public.guitar_specifications(guitar_id,specs,source) values(saved.id,p_data->'specs',p_data->'source')
    on conflict(guitar_id) do update set specs=excluded.specs,source=excluded.source,updated_at=now();
  if old.id is null or old.draft->'price' is distinct from p_data->'price' or old.draft->'priceSource' is distinct from p_data->'priceSource' then
    insert into public.guitar_prices(guitar_id,amount,source,checked_on,changed_by)
      values(saved.id,(p_data->>'price')::numeric,p_data->'priceSource',(p_data#>>'{priceSource,verifiedOn}')::date,auth.uid());
  end if;
  insert into public.audit_logs(actor,guitar_id,action,before_data,after_data)
    values(auth.uid(),saved.id,'save_draft',old.draft,p_data);
  return to_jsonb(saved);
end;
$$;

create or replace function public.admin_set_publication(p_id text,p_expected_revision bigint,p_action text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare old public.guitars; saved public.guitars;
begin
  if not public.fretline_is_admin() then raise exception 'Admin access required' using errcode='42501'; end if;
  select * into old from public.guitars where id=p_id for update;
  if not found or old.revision<>p_expected_revision then raise exception 'CONFLICT: reload the latest product' using errcode='40001'; end if;
  if p_action='publish' then
    perform public.fretline_validate_guitar(old.draft,true);
    update public.guitars set published=draft,status='published',published_at=now(),revision=revision+1,
      updated_at=now(),updated_by=auth.uid() where id=p_id returning * into saved;
  elsif p_action='hide' then
    update public.guitars set status='hidden',revision=revision+1,updated_at=now(),updated_by=auth.uid()
      where id=p_id returning * into saved;
  else raise exception 'Unknown action'; end if;
  insert into public.audit_logs(actor,guitar_id,action,before_data,after_data)
    values(auth.uid(),p_id,p_action,jsonb_build_object('status',old.status,'published',old.published),
      jsonb_build_object('status',saved.status,'published',saved.published));
  return to_jsonb(saved);
end;
$$;

create or replace function public.get_published_catalog() returns jsonb
language sql stable security definer set search_path='' as $$
  select jsonb_build_object('ready',coalesce((select ready from public.catalog_state where singleton),false),
    'guitars',coalesce((select jsonb_agg(published order by position,id) from public.guitars where status='published'),'[]'::jsonb));
$$;

create or replace function public.fretline_image_is_public(p_path text) returns boolean
language sql stable security definer set search_path='' as $$
  select exists(select 1 from public.guitars g, lateral jsonb_array_elements(g.published->'gallery') im
    where g.status='published' and im->>'storagePath'=p_path);
$$;

create or replace function public.admin_register_image(p_id text,p_path text,p_metadata jsonb)
returns jsonb language plpgsql security definer set search_path='' as $$
declare result public.guitar_images;
begin
  if not public.fretline_is_admin() then raise exception 'Admin access required' using errcode='42501'; end if;
  if split_part(p_path,'/',1)<>p_id or not exists(select 1 from storage.objects where bucket_id='guitar-images' and name=p_path)
    or coalesce(p_metadata->>'rightsConfirmed','false')<>'true' then raise exception 'Invalid image or image rights'; end if;
  insert into public.guitar_images(guitar_id,storage_path,metadata,created_by) values(p_id,p_path,p_metadata,auth.uid()) returning * into result;
  insert into public.audit_logs(actor,guitar_id,action,after_data) values(auth.uid(),p_id,'register_image',to_jsonb(result));
  return to_jsonb(result);
end;
$$;

-- Storage deletion independently refuses any file still referenced by Draft or Published.
create or replace function public.fretline_image_unused(p_path text) returns boolean
language sql stable security definer set search_path='' as $$
  select public.fretline_is_admin() and not exists(select 1 from public.guitars g, lateral jsonb_array_elements(
    coalesce(g.draft->'gallery','[]') || coalesce(g.published->'gallery','[]')) im where im->>'storagePath'=p_path);
$$;
create or replace function public.admin_forget_image(p_path text) returns void
language plpgsql security definer set search_path='' as $$
declare im public.guitar_images;
begin
  if not public.fretline_is_admin() or not public.fretline_image_unused(p_path) then raise exception 'Image is still in use or access denied'; end if;
  select * into im from public.guitar_images where storage_path=p_path;
  -- Serialize with saves/publishing of this product. Unregister first so no new
  -- Draft can reference a file while the Storage API deletes it.
  perform 1 from public.guitars where id=im.guitar_id for update;
  if not public.fretline_image_unused(p_path) then raise exception 'Image is still in use'; end if;
  delete from public.guitar_images where storage_path=p_path;
  if im.id is not null then insert into public.audit_logs(actor,guitar_id,action,before_data) values(auth.uid(),im.guitar_id,'delete_unused_image',to_jsonb(im)); end if;
end;
$$;

alter table public.brands enable row level security;
alter table public.admin_users enable row level security;
alter table public.guitars enable row level security;
alter table public.guitar_specifications enable row level security;
alter table public.guitar_prices enable row level security;
alter table public.guitar_images enable row level security;
alter table public.audit_logs enable row level security;
alter table public.catalog_state enable row level security;
drop policy if exists fretline_admin_self on public.admin_users;
create policy fretline_admin_self on public.admin_users for select to authenticated using(user_id=auth.uid());
do $$ declare tab text; begin
  foreach tab in array array['brands','guitars','guitar_specifications','guitar_prices','guitar_images','audit_logs','catalog_state'] loop
    execute format('drop policy if exists fretline_admin_read on public.%I',tab);
    execute format('create policy fretline_admin_read on public.%I for select to authenticated using(public.fretline_is_admin())',tab);
  end loop;
end $$;
revoke all on public.brands,public.admin_users,public.guitars,public.guitar_specifications,public.guitar_prices,public.guitar_images,public.audit_logs,public.catalog_state from anon,authenticated;
grant select on public.brands,public.admin_users,public.guitars,public.guitar_specifications,public.guitar_prices,public.guitar_images,public.audit_logs,public.catalog_state to authenticated;

revoke all on function public.fretline_validate_guitar(jsonb,boolean) from public,anon,authenticated;
revoke all on function public.admin_save_guitar(jsonb,bigint),public.admin_set_publication(text,bigint,text),public.admin_register_image(text,text,jsonb),public.admin_forget_image(text) from public,anon,authenticated;
grant execute on function public.admin_save_guitar(jsonb,bigint),public.admin_set_publication(text,bigint,text),public.admin_register_image(text,text,jsonb),public.admin_forget_image(text) to authenticated;
revoke all on function public.get_published_catalog(),public.fretline_is_admin(),public.fretline_image_is_public(text),public.fretline_image_unused(text) from public,anon,authenticated;
grant execute on function public.get_published_catalog(),public.fretline_is_admin(),public.fretline_image_is_public(text) to anon,authenticated;
grant execute on function public.fretline_image_unused(text) to authenticated;

insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
  values('guitar-images','guitar-images',false,8388608,array['image/jpeg','image/png','image/webp'])
  on conflict(id) do update set public=false,file_size_limit=8388608,allowed_mime_types=excluded.allowed_mime_types;
drop policy if exists fretline_image_read on storage.objects;
drop policy if exists fretline_image_insert on storage.objects;
drop policy if exists fretline_image_delete on storage.objects;
create policy fretline_image_read on storage.objects for select to anon,authenticated
  using(bucket_id='guitar-images' and (public.fretline_is_admin() or public.fretline_image_is_public(name)));
create policy fretline_image_insert on storage.objects for insert to authenticated
  with check(bucket_id='guitar-images' and public.fretline_is_admin() and exists(
    select 1 from public.guitars where id=split_part(name,'/',1)));
create policy fretline_image_delete on storage.objects for delete to authenticated
  using(bucket_id='guitar-images' and public.fretline_is_admin() and public.fretline_image_unused(name)
    and not exists(select 1 from public.guitar_images where storage_path=name));
-- No UPDATE policy: new uploads have unique paths; published originals cannot be overwritten.
commit;
