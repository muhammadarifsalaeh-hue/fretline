"""Schedule independent full-mesh chord audits without changing their checker.
Each result binds the same exact runtime JSON; aggregation never invents a pass.
"""
import argparse,concurrent.futures,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--library',type=Path,default=ROOT/'src/features/practice/assets/hand-poses.json');ap.add_argument('--output',type=Path,default=ROOT/'docs/practice-complete-42/tests/geometry');ap.add_argument('--workers',type=int,default=2);args=ap.parse_args();args.library=args.library.resolve();args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True);library=json.loads(args.library.read_text());required={k for k,p in library['poses'].items()if p['audit']['collisionPassed']and p['audit']['contactPassed']};snapshot=sha(args.library);checker=Path(__file__).with_name('check-geometry.py');checker_sha=sha(checker);triangle_sha=sha(ROOT/'scripts/practice/audit-hand-self-collisions.py');music_sha=sha(ROOT/'src/features/practice/data/chords.js')
 def run(key):
  folder=args.output/'individual'/key;folder.mkdir(parents=True,exist_ok=True);file=folder/'summary.json';cached=json.loads(file.read_text())if file.exists()else None
  match=cached and cached['librarySnapshotSha256']==snapshot and cached['checkerSHA256']==checker_sha and cached['originalTriangleCheckerSHA256']==triangle_sha and cached['sourceChordSha256']==music_sha
  if not match:
   with(folder/'audit.log').open('w')as log:subprocess.run(['python',str(checker),'--library',str(args.library),'--chords',key,'--require',key if key in required else'','--output',str(folder)],cwd=ROOT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
  report=json.loads(file.read_text());assert report['count']==len(report['rows'])==1 and report['rows'][0]['id']==key and report['librarySnapshotSha256']==snapshot and report['assetSha256']==library['assetSha256']and report['checkerSHA256']==checker_sha and report['sourceChordSha256']==music_sha and report['originalTriangleCheckerSHA256']==triangle_sha and report['testSuitePassed']and not report['errors'];row=report['rows'][0];assert(folder/row['rawEvidence']).is_file();row=dict(row,rawEvidence=str((folder/row['rawEvidence']).relative_to(args.output)),individualReportSHA256=sha(file));print('FULL-MESH',key,'PASS'if row['geometricPassed']else'REJECTED',flush=True);return report,row
 with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(2,args.workers)))as pool:results=list(pool.map(run,library['poses']))
 template=results[0][0];rows=[r[1]for r in results];assert len(rows)==len({r['id']for r in rows})==42;passed={r['id']for r in rows if r['geometricPassed']};errors=[key+' required runtime hand failed'for key in sorted(required-passed)];assert passed==required,'Runtime must contain only supported/visually reviewed replacements; unexpected passing old flags need review';report=dict(template,count=42,geometricPassed=len(passed),requiredBatch=sorted(required),testSuitePassed=not errors,all42GeometricPassed=len(passed)==42,errors=errors,rows=rows,schedulerSHA256=sha(Path(__file__)),individualAudits=42,parallelism=min(2,args.workers));(args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'geometricPassed':len(passed),'count':42,'all42Complete':len(passed)==42,'errors':errors}));assert not errors
if __name__=='__main__':main()
