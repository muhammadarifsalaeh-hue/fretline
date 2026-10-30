import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { createServer } from 'vite';

const baseline=JSON.parse(fs.readFileSync('docs/signature-experience/safety-baseline.json','utf8'));
const hash=value=>crypto.createHash('sha256').update(value).digest('hex');
for (const [path,digest] of Object.entries(baseline.protectedFiles)) {
  assert.equal(hash(fs.readFileSync(path)),digest,`Protected file changed: ${path}`);
}
const routes=[...fs.readFileSync('src/App.jsx','utf8').matchAll(/<Route path="([^"]+)"/g)].map(match=>match[1]);
assert.deepEqual(routes,baseline.routes,'Original route contracts must not change');
const server=await createServer({server:{middlewareMode:true,hmr:false},appType:'custom'});
try {
  const {GUITARS,SAVED_GUITARS_BY_ID}=await server.ssrLoadModule('/src/data/guitars.js');
  const {BRANDS}=await server.ssrLoadModule('/src/data/brands.js');
  const {PRACTICE_CHORDS}=await server.ssrLoadModule('/src/features/practice/data/chords.js');
  const data={guitars:GUITARS,saved:SAVED_GUITARS_BY_ID,brands:BRANDS,chords:PRACTICE_CHORDS};
  assert.equal(hash(JSON.stringify(data,null,2)),baseline.effectiveDataSHA256,'Effective catalog, archived entries, sources, prices, image relations or chords changed');
  console.log(JSON.stringify({passed:true,protectedFiles:Object.keys(baseline.protectedFiles).length,models:GUITARS.length,uniqueIds:new Set(GUITARS.map(g=>g.id)).size,brands:BRANDS.length,chords:PRACTICE_CHORDS.length,allFieldsIdentical:true,routesUnchanged:routes.length,hostedSupabaseVerified:false,sqlExecuted:false},null,2));
} finally {await server.close();}
