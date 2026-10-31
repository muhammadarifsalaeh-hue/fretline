import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';
const base='1f2836b875dc02f667c002093534f592cd1a0141',out='docs/practice-complete-42/tests';
const hash=v=>crypto.createHash('sha256').update(v).digest('hex');
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:64*1024*1024}).trim();
assert.equal(git('branch','--show-current'),'feature/practice-complete-42-poses');
assert.equal(git('rev-parse','master'),'9f7b35d7a0daea8a579976a5534ffb67d90f06a9','Master must remain untouched');
const allowed=new Set(['src/features/practice/assets/hand-poses.json','src/features/practice/scene/pressureContacts.js','src/features/practice/scene/createNeckScene.js','src/features/practice/scene/frettedStrings.js','src/features/practice/scene/handPoseEngine.js','scripts/check-hand-runtime.mjs']);
const changed=[...git('diff','--name-only',base).split('\n'),...git('ls-files','--others','--exclude-standard').split('\n')].filter(Boolean);
assert.ok(changed.every(f=>allowed.has(f)||f.startsWith('docs/practice-complete-42/')),`Unrelated edits: ${changed.filter(f=>!allowed.has(f)&&!f.startsWith('docs/practice-complete-42/'))}`);
const protectedFiles=git('ls-tree','-r','--name-only',base,'--','src','public','supabase','package.json','package-lock.json','scripts/practice/audit-hand-self-collisions.py','scripts/practice/check-hand-geometry.py').split('\n').filter(f=>f&&!allowed.has(f));
for(const file of protectedFiles)assert.equal(hash(fs.readFileSync(file)),hash(execFileSync('git',['show',`${base}:${file}`],{maxBuffer:64*1024*1024})),`Protected source changed: ${file}`);
const path='src/features/practice/assets/hand-poses.json',now=JSON.parse(fs.readFileSync(path)),old=JSON.parse(git('show',`${base}:${path}`));
assert.deepEqual(Object.keys(now.poses),Object.keys(old.poses));
const previous=JSON.parse(fs.readFileSync('docs/practice-fingering-polish/tests/geometry/summary.json'));
const thumbRepairs=new Set(['B7','Gmaj7','Dsus2']);
for(const {id}of previous.rows.filter(r=>r.geometricPassed)){
 assert.deepEqual(now.poses[id].root,old.poses[id].root,`${id} existing root changed`);
 for(const name of Object.keys(old.poses[id].bones))if(!thumbRepairs.has(id)||!name.startsWith('finger1-'))assert.deepEqual(now.poses[id].bones[name],old.poses[id].bones[name],`${id} protected bone ${name}`);
 assert.deepEqual(now.poses[id].pressOffsetsMm,old.poses[id].pressOffsetsMm);
}
const geometry=JSON.parse(fs.readFileSync(`${out}/geometry/summary.json`));assert.equal(geometry.librarySnapshotSha256,hash(fs.readFileSync(path)));
const accepted=Object.entries(now.poses).filter(([,p])=>p.audit.collisionPassed&&p.audit.contactPassed).map(([id])=>id).sort();
assert.deepEqual(accepted,geometry.rows.filter(r=>r.geometricPassed).map(r=>r.id).sort());
assert.ok(Object.values(now.poses).every(p=>p.status==='needs-review'&&p.reviewed===false&&p.audit.anatomyPassed===false),'Do not invent instructor/anatomy certification');
const server=await createServer({logLevel:'error',server:{middlewareMode:true,hmr:false},appType:'custom'});
try{
 const {GUITARS,SAVED_GUITARS_BY_ID}=await server.ssrLoadModule('/src/data/guitars.js');const {BRANDS}=await server.ssrLoadModule('/src/data/brands.js');const {PRACTICE_CHORDS}=await server.ssrLoadModule('/src/features/practice/data/chords.js');
 const effective=hash(JSON.stringify({guitars:GUITARS,saved:SAVED_GUITARS_BY_ID,brands:BRANDS,chords:PRACTICE_CHORDS}));assert.equal(effective,JSON.parse(fs.readFileSync('docs/universal-guitar-images/baseline.json')).effectiveDataSHA256);assert.equal(GUITARS.length,200);assert.equal(new Set(GUITARS.map(g=>g.id)).size,200);assert.equal(BRANDS.length,10);assert.equal(PRACTICE_CHORDS.length,42);
 const counts=Object.fromEntries(BRANDS.map(b=>[b.name,GUITARS.filter(g=>g.brand===b.name).length]));assert.ok(Object.values(counts).every(n=>n===20));
 const report={passed:true,baselineCommit:base,rollbackTag:'backup/practice-before-all42-1f2836b',models:200,brands:10,counts,chords:42,effectiveDataSHA256:effective,allProductAndChordDataIdentical:true,protectedFilesIdentical:protectedFiles.length,sourceModelSHA256:hash(fs.readFileSync('src/features/practice/assets/makehuman-left-arm-sleeved.glb')),poseLibrarySHA256:hash(fs.readFileSync(path)),displayableHands:accepted,verifiedTeachingHands:0,homeCatalogAdminDatabaseAndPracticeUIUnchanged:true,original13FrettingBonesAndRootsIdentical:true,necessaryThumbOnlyRepairs:[...thumbRepairs],databaseWrites:0,changedSourceFiles:changed.filter(f=>!f.startsWith('docs/'))};fs.mkdirSync(out,{recursive:true});fs.writeFileSync(`${out}/data-safety.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
}finally{await server.close();}
