import { deploymentProblems } from './lib/deployment.mjs';

const problems = deploymentProblems(process.env);
if (problems.length) {
  console.error('Fretline deployment configuration is incomplete:');
  problems.forEach(message => console.error(`- ${message}`));
  process.exitCode = 1;
} else {
  console.log('PASS: public Supabase configuration; Published catalog selected. No secret values printed.');
  if (!process.env.VITE_SITE_URL) console.warn('QR remains unavailable until VITE_SITE_URL is set to the verified production URL and redeployed.');
  console.log('Configuration check only: no network request, SQL or database change.');
}
