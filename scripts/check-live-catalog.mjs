// Optional READ-ONLY public RPC check. Does not execute setup.sql or use admin keys.
import fs from 'node:fs';
import { deploymentProblems } from './lib/deployment.mjs';

const problems = deploymentProblems(process.env);
if (problems.length) {
  console.error('Public Supabase environment is missing or invalid. No request sent; no values printed.');
  process.exitCode = 1;
} else {
  try {
    const response = await fetch(`${process.env.VITE_SUPABASE_URL.trim().replace(/\/$/, '')}/rest/v1/rpc/get_published_catalog`, {
      method: 'POST', redirect: 'error', signal: AbortSignal.timeout(20000),
      headers: { apikey: process.env.VITE_SUPABASE_PUBLISHABLE_KEY.trim(), 'Content-Type': 'application/json' }, body: '{}',
    });
    if (!response.ok) throw new Error('Request failed');
    const snapshot = await response.json();
    if (snapshot.ready !== true || !Array.isArray(snapshot.guitars)) throw new Error('Catalog not ready');
    const guitars = snapshot.guitars, ids = new Set(guitars.map(g => g.id));
    if (ids.size !== guitars.length || guitars.some(g => !g.id || !g.brand || !g.name || (g.price != null && (!Number.isFinite(g.price) || g.price <= 0)))) throw new Error('Invalid catalog');
    const expected = JSON.parse(fs.readFileSync('docs/admin-studio/current/seed-manifest.json', 'utf8')).ids;
    const byBrand = guitars.reduce((counts, g) => { counts[g.brand] = (counts[g.brand] ?? 0) + 1; return counts; }, {});
    const missingOriginals = expected.filter(id => !ids.has(id)).length;
    console.log(JSON.stringify({ readOnly: true, ready: true, published: guitars.length, brands: Object.keys(byBrand).length, byBrand, missingOriginals, priced: guitars.filter(g => g.price > 0).length }, null, 2));
    if (process.argv.includes('--initial') && (guitars.length !== 200 || Object.keys(byBrand).length !== 10 || Object.values(byBrand).some(n => n !== 20) || missingOriginals)) {
      console.error('Initial release verification failed: expected all 200 original models, 10 brands x 20.');
      process.exitCode = 1;
    }
  } catch {
    console.error('Published catalog could not be verified. Check Supabase setup, public configuration and RLS. No raw response or credentials printed; no database changes requested.');
    process.exitCode = 1;
  }
}
