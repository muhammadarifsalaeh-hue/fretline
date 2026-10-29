import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { verifyAdminAccess, watchAdminAccess } from '../src/features/admin/verifiedAccess.js';
import { productionSiteUrl } from '../src/features/deployment/siteUrl.js';
import { deploymentProblems, publicCredentialProblems } from './lib/deployment.mjs';

// Fixture values, no network, Supabase project or real credentials.
const valid = { VITE_SUPABASE_URL: 'https://qa.supabase.co', VITE_SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_fixture', VITE_CATALOG_SOURCE: 'supabase' };
const client = (user, membership, error) => ({ auth: { getUser: async () => ({data:{user},error}) }, rpc: async () => ({data:membership,error}) });

test('only server-verified user AND boolean membership reveal Admin', async () => {
  assert.equal(await verifyAdminAccess(client({id:'fixture-owner'},true)),true);
  for (const result of [false,null,1,'true',{},[]]) assert.equal(await verifyAdminAccess(client({id:'fixture-user'},result)),false);
  assert.equal(await verifyAdminAccess(client(null,true)),false);
  assert.equal(await verifyAdminAccess(client({id:'fixture-user'},true,new Error('failure'))),false);
  assert.equal(await verifyAdminAccess({auth:{getUser:async()=>{throw new Error('network');}}}),false);
});

test('unverified identity cannot call the membership RPC', async () => {
  const c=client(null,true);c.rpc=()=>{throw new Error('must not call RPC');};
  assert.equal(await verifyAdminAccess(c),false);
});

test('logout invalidates an in-flight positive result; listeners cleaned up', async () => {
  let resolveIdentity, callback, unsubscribed=false;
  const target=new globalThis.EventTarget();target.document=new globalThis.EventTarget();target.document.visibilityState='visible';
  const c={auth:{getUser:()=>new Promise(resolve=>{resolveIdentity=resolve;}),onAuthStateChange:fn=>{callback=fn;return {data:{subscription:{unsubscribe:()=>{unsubscribed=true;}}}};}},rpc:async()=>({data:true})};
  const states=[];const stop=watchAdminAccess(c,value=>states.push(value),target);
  callback('SIGNED_OUT');resolveIdentity({data:{user:{id:'fixture-owner'}}});
  await new Promise(resolve=>setTimeout(resolve,10));
  assert.ok(states.every(value=>value===false));
  stop();assert.equal(unsubscribed,true);
});

test('QR URL never derives from a preview/current origin or accepts credentials', () => {
  for (const value of [undefined,'','http://fretline.vercel.app','https://localhost','https://127.0.0.1','https://user:pass@fretline.vercel.app','https://fretline.vercel.app/admin','https://fretline.vercel.app?token=fixture','https://old-5173.app.github.dev','https://old.github.dev','https://demo.example.com','https://fretline.test','https://foo.ngrok-free.app']) assert.equal(productionSiteUrl(value),null);
  assert.equal(productionSiteUrl('https://fretline-owner-domain.vercel.app/'),'https://fretline-owner-domain.vercel.app');
  assert.equal(productionSiteUrl('https://fretline.co.th'),'https://fretline.co.th');
});

test('Vercel build requires published Supabase data, not a stale static fallback', () => {
  assert.deepEqual(deploymentProblems(valid),[]);
  for (const env of [{},{...valid,VITE_CATALOG_SOURCE:'static'},{...valid,VITE_SUPABASE_URL:''},{...valid,VITE_SUPABASE_PUBLISHABLE_KEY:'sb_secret_fixture'},{...valid,VITE_SITE_URL:'https://old.app.github.dev'}]) assert.ok(deploymentProblems(env).length);
});

test('browser secrets are rejected in every Vite mode without leaking values', () => {
  for (const env of [{VITE_ACCESS_TOKEN:'fixture-private-value'},{VITE_ANY:'sb_secret_fixture'},{VITE_ANY:'sbp_fixture'},{VITE_DB_PASSWORD:'fixture-private-value'},{VITE_ANY:`x.${Buffer.from(JSON.stringify({role:'service_role'})).toString('base64url')}.x`}]) {
    const output=publicCredentialProblems(env);assert.ok(output.length);assert.ok(!JSON.stringify(output).includes('fixture-private-value'));
  }
  assert.deepEqual(publicCredentialProblems({...valid,FRETLINE_SUPABASE_ACCESS_TOKEN:'server-only-fixture'}),[]);
});

test('Vercel routes cover deep links while preserving static paths and cache policy', () => {
  const config=JSON.parse(fs.readFileSync('vercel.json','utf8'));
  const pattern=new RegExp(`^${config.rewrites[0].source}$`);
  for (const path of ['/','/admin','/qr','/guitars/some-id','/brands/fender','/compare','/practice','/find-my-guitar']) assert.ok(pattern.test(path));
  for (const path of ['/assets/app.js','/fonts/fonts.css','/images/hero/acoustic-studio.webp','/licenses/three-MIT.txt','/models/guitar.glb','/favicon.svg']) assert.ok(!pattern.test(path));
  assert.equal(config.outputDirectory,'dist');assert.equal(config.buildCommand,'npm run build:vercel');
  assert.ok(config.headers.some(rule=>rule.headers.some(header=>header.key==='X-Content-Type-Options'&&header.value==='nosniff')));
});
