"""Record explicitly requested manual render inspections; never auto-approve.
Call only after actually inspecting all four bound images of the named poses.
"""
import argparse,hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-complete-42'
ap=argparse.ArgumentParser();ap.add_argument('--chords',required=True);ap.add_argument('--note',required=True);args=ap.parse_args();file=OUT/'tests/visual-review.json';report=json.loads(file.read_text());captures=json.loads((OUT/'tests/captures-final.json').read_text());library_file=ROOT/'.local-preview/practice-complete-42/review-library.json';assert captures['sourceSHA256']==hashlib.sha256(library_file.read_bytes()).hexdigest();lib=json.loads(library_file.read_text());inventory={r['id']:r for r in json.loads((OUT/'tests/candidate-inventory.json').read_text())}
for key in args.chords.split(','):
 p=lib['poses'][key];scene=hashlib.sha256(json.dumps({'root':p['root'],'bones':p['bones'],'pressure':p.get('pressOffsetsMm')},sort_keys=True,separators=(',',':')).encode()).hexdigest();views=[r for r in captures['rows']if r['id']==key];assert len(views)==4 and all(v['sceneSHA256']==scene for v in views);assert inventory[key]['safeGeometryAndSupport']
 for v in views:assert hashlib.sha256((ROOT/v['file']).read_bytes()).hexdigest()==v['imageSHA256']
 row=next(r for r in report['rows']if r['id']==key);row.update(actualFourViewRendersInspected=True,technicalVisualPassed=True,needsFurtherCorrection=False,sceneSHA256=scene,views=views,note=args.note,independentInstructorApproval=False)
report['reviewedAtUTC']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());report['technicalVisualPassed']=sum(r['technicalVisualPassed']for r in report['rows']);file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Manually inspected technical renders:',report['technicalVisualPassed'])
