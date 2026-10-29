"""Local isolated PostgreSQL integration. Never connects to the hosted project."""
import subprocess,json,time,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
database=f'fretline_admin_qa_{os.getpid()}_{int(time.time())}'
container='fretline-admin-pg'
checks=[]
def run(sql):
    r=subprocess.run(['docker','exec','-i',container,'psql','-U','postgres','-d',database,'-v','ON_ERROR_STOP=1','-qAt'],input=sql,text=True,capture_output=True)
    if r.returncode:raise RuntimeError(r.stderr)
    checks.extend(s.split('PASS: ',1)[1] for s in r.stderr.splitlines() if 'PASS: ' in s)
    return r.stdout.strip()
subprocess.run(['docker','exec',container,'createdb','-U','postgres',database],check=True)
try:
    run((root/'supabase/tests/bootstrap-local.sql').read_text())
    run((root/'supabase/setup.sql').read_text())
    run((root/'supabase/setup.sql').read_text())
    run((root/'supabase/tests/security.sql').read_text())
    run("update public.guitars set draft=jsonb_set(jsonb_set(draft,'{name}','\"QA preserved model name\"'),'{specs,bodyShape}','\"QA preserved nonnull shape\"') where id='fender-player-ii-stratocaster';")
    before=run("select md5(jsonb_agg(to_jsonb(g) order by id)::text) from public.guitars g;")
    run((root/'supabase/setup.sql').read_text())
    after=run("select md5(jsonb_agg(to_jsonb(g) order by id)::text) from public.guitars g;")
    assert before==after,'Reimport overwrote existing data'
    checks.append('Reimport preserves all rows, entire drafts/publications and existing nonnull edits even when seed has null')
    report={'scope':'real isolated PostgreSQL 17 with Supabase Auth/Storage schema contracts','hostedSupabaseTested':False,'checks':checks,'passed':True,'total':len(checks)}
    (root/'docs/admin-studio/current/database-security-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print('\n'.join('PASS '+s for s in checks));print(f'{len(checks)}/{len(checks)} database checks passed')
finally:
    subprocess.run(['docker','exec',container,'dropdb','-U','postgres',database],check=True)
