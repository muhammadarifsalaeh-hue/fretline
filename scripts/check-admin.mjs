import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createServer} from 'vite';
const server=await createServer({server:{middlewareMode:true,hmr:false},appType:'custom'});
let passed=0;
const test=(name,fn)=>{fn();passed++;console.log('PASS',name);};
try{
  const {GUITARS}=await server.ssrLoadModule('/src/data/guitars.js');
  const {prepareDraft,validateDraft,seedRecord,blankGuitar}=await server.ssrLoadModule('/src/features/admin/product.js');
  const {validateConnection}=await server.ssrLoadModule('/src/features/admin/config.js');
  const source={url:'https://example.com/model',verifiedOn:'2026-10-29'};
  const data={...blankGuitar('Yamaha'),id:'qa-model',name:'QA model'};
  test('Exactly 200 stable IDs and 10 x 20 remain in static rollback catalog',()=>{assert.equal(GUITARS.length,200);assert.equal(new Set(GUITARS.map(g=>g.id)).size,200);const counts=Object.values(GUITARS.reduce((a,g)=>({...a,[g.brand]:(a[g.brand]??0)+1}),{}));assert.equal(counts.length,10);assert.ok(counts.every(n=>n===20));});
  test('Seed keeps every original record including nulls and image provenance',()=>{for(const g of GUITARS){const d=seedRecord(g);assert.equal(d.id,g.id);assert.deepEqual(d.specs,g.specs);assert.deepEqual(d.priceSource,g.priceSource);assert.deepEqual(d.source,g.source);assert.equal(d.gallery.length,g.gallery.length);d.gallery.forEach((im,i)=>{assert.equal(im.legacyIndex,i);assert.deepEqual(im.attribution,g.gallery[i].attribution);assert.equal(im.src,undefined);});}});
  test('Import never uses an upsert that overwrites existing guitar rows',()=>{const sql=fs.readFileSync('supabase/seed.sql','utf8');assert.ok(sql.includes('on conflict(id) do nothing'));assert.ok(!/do update/i.test(sql));});
  test('Unknown price becomes null, not zero',()=>{assert.equal(prepareDraft({...data,price:''}).price,null);assert.ok(validateDraft({...data,price:0}));assert.equal(validateDraft(prepareDraft(data),true),null);});
  test('Zero, negative, non-finite, unreferenced and future prices fail',()=>{for(const price of [0,-1,Infinity,NaN])assert.ok(validateDraft({...data,price}));assert.ok(validateDraft({...data,price:1000}));assert.ok(validateDraft({...data,price:1000,priceSource:{...source,verifiedOn:'2999-01-01'}}));});
  test('Published specs require evidence; numeric counts remain numeric',()=>{assert.ok(validateDraft(prepareDraft({...data,specs:{strings:'6'}}),true));const d=prepareDraft({...data,source,specs:{strings:'6',frets:'0'},price:1000,priceSource:source});assert.equal(d.specs.strings,6);assert.equal(d.specs.frets,0);assert.equal(validateDraft(d,true),null);assert.ok(d.source.fields.includes('specs.strings'));assert.equal(d.priceSource.currency,'THB');});
  test('Invalid or negative and fractional counts are rejected',()=>{for(const n of [-1,0,1.5,'nonsense'])assert.ok(validateDraft(prepareDraft({...data,specs:{strings:n}})));});
  test('Existing unsupported-by-editor specs, images, profile and source metadata survive edits',()=>{for(const g of GUITARS){const d=prepareDraft(seedRecord(g));for(const [k,v]of Object.entries(g.specs))assert.deepEqual(d.specs[k]??null,v??null);assert.deepEqual(d.gallery,seedRecord(g).gallery);assert.deepEqual(d.profile,g.profile);}});
  test('Service keys, URL credentials and foreign domains cannot become browser config',()=>{assert.equal(validateConnection('https://qa.supabase.co','sb_publishable_test'),null);for(const key of ['sb_secret_test','service_role',''])assert.ok(validateConnection('https://qa.supabase.co',key));for(const url of ['http://qa.supabase.co','https://qa.supabase.co.evil.test','https://user:pass@qa.supabase.co','https://qa.supabase.co/path'])assert.ok(validateConnection(url,'sb_publishable_test'));});
  fs.mkdirSync('docs/admin-studio/current',{recursive:true});fs.writeFileSync('docs/admin-studio/current/unit-results.json',JSON.stringify({passed,total:passed,hostedSupabaseTested:false},null,2)+'\n');
  console.log(`${passed}/${passed} admin data checks passed`);
}finally{await server.close();}
