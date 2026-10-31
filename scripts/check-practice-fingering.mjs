import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';
const base='218eab5a1b72125b7981b01ebe8aa417dd58fef7';
const hash=v=>crypto.createHash('sha256').update(v).digest('hex');
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:64*1024*1024}).trim();
const allowed=new Set(['src/features/practice/components/GuitarNeckViewer.jsx','src/features/practice/components/viewer.css','src/features/practice/assets/hand-poses.json','scripts/check-hand-runtime.mjs','scripts/check-practice-fingering.mjs','scripts/practice/fit-missing-poses.py','scripts/practice/repair-pose-batch.py','scripts/practice/lift-pose.py','scripts/practice/import-audited-poses.py','scripts/practice/source-pose-context.py']);
const changes=[...git('diff','--name-only',base).split('\n'),...git('ls-files','--others','--exclude-standard').split('\n')].filter(Boolean);
assert.ok(changes.every(f=>allowed.has(f)||f.startsWith('docs/practice-fingering-polish/')),`Unrelated changes: ${changes.filter(f=>!allowed.has(f)&&!f.startsWith('docs/practice-fingering-polish/'))}`);
const path='src/features/practice/assets/hand-poses.json';
const previous=JSON.parse(git('show',`${base}:${path}`)),current=JSON.parse(fs.readFileSync(path));
const report=JSON.parse(fs.readFileSync('docs/practice-fingering-polish/tests/geometry/summary.json'));
const {poses: oldPoses,...oldMetadata}=previous,{poses: newPoses,...newMetadata}=current;assert.deepEqual(newMetadata,oldMetadata);
assert.equal(report.count,42);assert.equal(report.librarySnapshotSha256,hash(fs.readFileSync(path)));assert.equal(report.testSuitePassed,true);assert.deepEqual(report.errors,[]);
const originallyPassed=Object.entries(previous.poses).filter(([,p])=>p.audit.collisionPassed&&p.audit.contactPassed).map(([id])=>id);
for(const id of originallyPassed)assert.deepEqual(current.poses[id],previous.poses[id],`Original passing pose changed: ${id}`);
assert.deepEqual(Object.keys(current.poses).sort(),Object.keys(previous.poses).sort());
const accepted=Object.entries(current.poses).filter(([,p])=>p.audit.collisionPassed&&p.audit.contactPassed).map(([id])=>id).sort();
assert.deepEqual(accepted,report.rows.filter(r=>r.geometricPassed).map(r=>r.id).sort());
for(const id of Object.keys(current.poses).filter(id=>!accepted.includes(id)))assert.deepEqual(current.poses[id],previous.poses[id],`Rejected pose overwritten: ${id}`);
assert.ok(Object.values(current.poses).every(p=>p.status==='needs-review'&&p.reviewed===false&&p.audit.anatomyPassed===false&&p.audit.multiViewReviewed===false));
for(const file of git('ls-tree','-r','--name-only',base,'--','src/features/practice/scene','src/features/practice/data','src/features/practice/assets').split('\n').filter(f=>f&&f!==path)) {
 assert.equal(hash(fs.readFileSync(file)),hash(execFileSync('git',['show',`${base}:${file}`],{maxBuffer:64*1024*1024})),`Protected scene/rig/chord changed: ${file}`);
}
const server=await createServer({logLevel:'error',server:{middlewareMode:true,hmr:false},appType:'custom'});
try{
 const {GUITARS,SAVED_GUITARS_BY_ID}=await server.ssrLoadModule('/src/data/guitars.js');
 const {BRANDS}=await server.ssrLoadModule('/src/data/brands.js');
 const {PRACTICE_CHORDS}=await server.ssrLoadModule('/src/features/practice/data/chords.js');
 const data=hash(JSON.stringify({guitars:GUITARS,saved:SAVED_GUITARS_BY_ID,brands:BRANDS,chords:PRACTICE_CHORDS}));
 assert.equal(data,JSON.parse(fs.readFileSync('docs/universal-guitar-images/baseline.json')).effectiveDataSHA256);
 assert.equal(GUITARS.length,200);assert.equal(new Set(GUITARS.map(g=>g.id)).size,200);assert.equal(BRANDS.length,10);assert.equal(PRACTICE_CHORDS.length,42);
 const counts=Object.fromEntries(BRANDS.map(b=>[b.name,GUITARS.filter(g=>g.brand===b.name).length]));assert.ok(Object.values(counts).every(n=>n===20));
 const result={passed:true,baselineCommit:base,rollbackTag:'backup/fretline-before-practice-fingering-218eab5',allProductAndChordDataIdentical:true,effectiveDataSHA256:data,originalModelAndSceneUnchanged:true,originalSevenPosesUnchanged:true,models:200,brands:10,counts,chords:42,acceptedGeometrically:accepted,verifiedTeachingHands:0,databaseWrites:0,unrelatedChanges:false};
 fs.writeFileSync('docs/practice-fingering-polish/tests/data-safety.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await server.close();}
