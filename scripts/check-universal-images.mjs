import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';

const folder='docs/universal-guitar-images';
const baseline=JSON.parse(fs.readFileSync(`${folder}/baseline.json`,'utf8'));
const git=(...args)=>execFileSync('git',args,{encoding:'utf8'}).trim();
const sha=(bytes)=>crypto.createHash('sha256').update(bytes).digest('hex');
const protectedRoots=['src/data','src/assets','public','supabase','src/features/practice','src/context','src/utils',
  'src/features/admin/config.js','src/features/admin/product.js','src/features/admin/publicCatalog.js','src/features/admin/errors.js',
  'src/pages/AdminStudioPage.jsx','src/pages/PracticePage.jsx','src/pages/FindMyGuitarPage.jsx','src/pages/ComparePage.jsx',
  'src/components/home','src/hooks/useBrandMarquee.js','src/styles/home-brands.css','src/components/compare/compareRows.js',
  'src/components/quiz/QuizFlow.jsx','package.json','package-lock.json','vite.config.js','src/App.jsx'];
let checked=0;
for(const file of git('ls-tree','-r','--name-only',baseline.baseCommit,'--',...protectedRoots).split('\n').filter(Boolean)) {
  const original=execFileSync('git',['show',`${baseline.baseCommit}:${file}`],{maxBuffer:64*1024*1024});
  assert.equal(sha(fs.readFileSync(file)),sha(original),`Protected data, asset or behavior changed: ${file}`); checked++;
}
const server=await createServer({logLevel:'error',server:{middlewareMode:true,hmr:false},appType:'custom'});
try{
 const {GUITARS,SAVED_GUITARS_BY_ID}=await server.ssrLoadModule('/src/data/guitars.js');
 const {BRANDS}=await server.ssrLoadModule('/src/data/brands.js');
 const {PRACTICE_CHORDS}=await server.ssrLoadModule('/src/features/practice/data/chords.js');
 const effective={guitars:GUITARS,saved:SAVED_GUITARS_BY_ID,brands:BRANDS,chords:PRACTICE_CHORDS};
 assert.equal(sha(JSON.stringify(effective)),baseline.effectiveDataSHA256,'Original catalog facts, images or relations changed');
 assert.equal(GUITARS.length,200);assert.equal(new Set(GUITARS.map(g=>g.id)).size,200);
 assert.equal(BRANDS.length,10);assert.equal(PRACTICE_CHORDS.length,42);
 const counts=Object.fromEntries(BRANDS.map(b=>[b.name,GUITARS.filter(g=>g.brand===b.name).length]));assert.ok(Object.values(counts).every(n=>n===20));
 const report={passed:true,protectedFiles:checked,models:200,brands:10,counts,chords:42,
   modelsWithRegisteredImages:GUITARS.filter(g=>g.gallery?.length>0).length,
   modelsUsingPlaceholder:GUITARS.filter(g=>!g.gallery?.length).length,
   allOriginalDataAndImagesIdentical:true,databaseWrites:false,hostedSupabaseVerified:false};
 fs.mkdirSync(`${folder}/tests`,{recursive:true});fs.writeFileSync(`${folder}/tests/data-safety.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
}finally{await server.close()}
