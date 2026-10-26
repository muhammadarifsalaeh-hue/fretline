"""Own the preview server lifecycle so a lost earlier shell cannot invalidate image QA."""
from pathlib import Path
import subprocess,time,urllib.request,os,signal
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/yamaha-import/tests/final';OUT.mkdir(exist_ok=True)
with (OUT/'server.txt').open('w') as log:
 server=subprocess.Popen(['npm','run','dev:yamaha-preview','--','--host','0.0.0.0','--port','5433','--strictPort'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  for _ in range(100):
   if server.poll() is not None:raise RuntimeError('Owned preview server did not start; inspect server.txt')
   try:
    with urllib.request.urlopen('http://127.0.0.1:5433/guitars?brand=Yamaha',timeout=1) as response:
     if response.status==200:break
   except OSError:pass
   time.sleep(.1)
  else:raise RuntimeError('Preview readiness deadline exceeded')
  env=os.environ.copy();env.update(PLAYWRIGHT_BROWSERS_PATH='/tmp/fretline-browser-engines',PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS='1')
  result=subprocess.run(['python','-u','docs/yamaha-import/tests/browser.py','--production','http://127.0.0.1:5432','--preview','http://127.0.0.1:5433','--output',str(OUT)],cwd=ROOT,env=env)
  raise SystemExit(result.returncode)
 finally:
  if server.poll() is None:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
