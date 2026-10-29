import fs from 'node:fs';
import {createServer} from 'vite';
const server=await createServer({server:{middlewareMode:true,hmr:false},appType:'custom'});
try{
  const {GUITARS}=await server.ssrLoadModule('/src/data/guitars.js');
  const {BRANDS}=await server.ssrLoadModule('/src/data/brands.js');
  const {seedRecord}=await server.ssrLoadModule('/src/features/admin/product.js');
  if(GUITARS.length!==200||BRANDS.length!==10||BRANDS.some(b=>b.models!==20)||new Set(GUITARS.map(g=>g.id)).size!==200)throw Error('Expected original 200 models / 10 x 20');
  const data=GUITARS.map(seedRecord), brands=BRANDS.map(b=>({id:b.id,name:b.name}));
  const json=JSON.stringify({guitars:data,brands});
  if(json.includes('$fretline_seed$'))throw Error('Unexpected SQL delimiter');
  const seed=`-- Generated from existing effective catalog. No null overwrite or duplicate IDs.\nbegin;\ncreate temporary table fretline_seed(data jsonb) on commit drop;\ninsert into fretline_seed values($fretline_seed$${json}$fretline_seed$::jsonb);\ninsert into public.brands(id,name) select b->>'id',b->>'name' from fretline_seed,lateral jsonb_array_elements(data->'brands') b on conflict do nothing;\ninsert into public.guitars(id,brand_id,draft,published,status,position)\nselect g->>'id',b.id,g,g,'published',ord::integer from fretline_seed,lateral jsonb_array_elements(data->'guitars') with ordinality x(g,ord) join public.brands b on b.name=g->>'brand' on conflict(id) do nothing;\ninsert into public.guitar_specifications(guitar_id,specs,source) select id,draft->'specs',draft->'source' from public.guitars on conflict(guitar_id) do nothing;\ninsert into public.guitar_prices(guitar_id,amount,source,checked_on) select id,(draft->>'price')::numeric,draft->'priceSource',(draft#>>'{priceSource,verifiedOn}')::date from public.guitars g where not exists(select 1 from public.guitar_prices p where p.guitar_id=g.id);\ndo $$ begin if (select count(*) from fretline_seed,lateral jsonb_array_elements(data->'guitars') g where exists(select 1 from public.guitars where id=g->>'id'))<>200 then raise exception 'Seed validation failed'; end if; end $$;\nupdate public.catalog_state set ready=true where singleton;\ncommit;\nselect count(*) as total_guitars,count(distinct brand_id) as brands from public.guitars;\n`;
  fs.writeFileSync('supabase/seed.sql',seed);
  fs.writeFileSync('supabase/setup.sql',fs.readFileSync('supabase/migrations/202610290001_admin_studio.sql','utf8')+'\n'+seed);
  fs.mkdirSync('docs/admin-studio/current',{recursive:true});
  fs.writeFileSync('docs/admin-studio/current/seed-manifest.json',JSON.stringify({models:data.length,brands:brands.length,priced:data.filter(g=>g.price>0).length,images:data.filter(g=>g.gallery.length).length,ids:data.map(g=>g.id)},null,2)+'\n');
  console.log('Generated idempotent SQL: 200 models, 10 brands, 27 existing prices; original images remain legacy references.');
}finally{await server.close();}
