-- LOCAL TEST ONLY: minimal Supabase auth/storage contracts in isolated PostgreSQL.
do $$begin if not exists(select from pg_roles where rolname='anon') then create role anon nologin; end if;
if not exists(select from pg_roles where rolname='authenticated') then create role authenticated nologin; end if; end$$;
create schema auth;
create schema storage;
create table auth.users(id uuid primary key,email text);
create function auth.uid() returns uuid language sql stable as $$select coalesce(nullif(current_setting('request.jwt.claim.sub',true),''),nullif(current_setting('request.jwt.claims',true),'')::jsonb->>'sub')::uuid$$;
create table storage.buckets(id text primary key,name text,public boolean,file_size_limit bigint,allowed_mime_types text[]);
create table storage.objects(id uuid default gen_random_uuid(),bucket_id text,name text,metadata jsonb default '{}',unique(bucket_id,name));
alter table storage.objects enable row level security;
grant usage on schema public,auth,storage to anon,authenticated;
grant execute on function auth.uid() to anon,authenticated;
grant select,insert,update,delete on storage.objects to anon,authenticated;
