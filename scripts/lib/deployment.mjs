import { validateConnection } from '../../src/features/admin/config.js';
import { productionSiteUrl } from '../../src/features/deployment/siteUrl.js';

export function publicCredentialProblems(env) {
  const problems = [];
  for (const [name, value] of Object.entries(env)) {
    if (!name.startsWith('VITE_')) continue;
    let privileged = /sb_secret_|sbp_[A-Za-z0-9]|service_role|-----BEGIN [A-Z ]*PRIVATE KEY-----/.test(String(value));
    try { privileged ||= JSON.parse(Buffer.from(String(value).split('.')[1] ?? '', 'base64url').toString()).role === 'service_role'; } catch { /* not a JWT */ }
    if (/SECRET|PASSWORD|TOKEN|SERVICE_ROLE|DATABASE_URL|CONNECTION_STRING|PRIVATE_KEY/i.test(name) || privileged) problems.push('Remove private credentials from VITE_ variables. Values and variable names are intentionally omitted.');
  }
  return [...new Set(problems)];
}

export function deploymentProblems(env) {
  const problems = publicCredentialProblems(env);
  if (env.VITE_CATALOG_SOURCE !== 'supabase') problems.push('Set VITE_CATALOG_SOURCE to supabase; public deployment must use Published data.');
  if (validateConnection((env.VITE_SUPABASE_URL ?? '').trim(), (env.VITE_SUPABASE_PUBLISHABLE_KEY ?? '').trim())) problems.push('Configure a valid VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY (publishable key only).');
  if (env.VITE_SITE_URL && !productionSiteUrl(env.VITE_SITE_URL)) problems.push('VITE_SITE_URL must be the HTTPS production origin, without a path, query or preview hostname.');
  return problems;
}
