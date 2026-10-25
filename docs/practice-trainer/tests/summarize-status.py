"""Join independent music, rendered-diagram and hand-lifecycle evidence.

This report never changes application status and never approves anatomy.
Point --reports at the final browser run directory after serial engine runs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--reports', type=Path, default=Path(__file__).parent / 'reports')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
destination = args.output or args.reports / 'chord-status-42.json'
music_path = args.reports / 'chord-audit.json'
music = json.loads(music_path.read_text())
chords = json.loads(subprocess.check_output(['node','--input-type=module','-e',
    "import {PRACTICE_CHORDS} from './src/features/practice/data/chords.js'; console.log(JSON.stringify(PRACTICE_CHORDS));"],cwd=ROOT))
poses_path = ROOT / 'src/features/practice/assets/hand-poses.json'
poses = json.loads(poses_path.read_text()).get('poses',{}) if poses_path.exists() else {}
current_source_sha = hashlib.sha256((ROOT/'src/features/practice/data/chords.js').read_bytes()).hexdigest()
browser = {}
for engine in ['chromium','webkit']:
    paths = sorted(args.reports.glob('**/browser-trainer-'+engine+'*.json'))
    reports = [(path,json.loads(path.read_text())) for path in paths]
    matches = [(path,report,check) for path,report in reports for check in report.get('checks',[])
               if report.get('passed') is True
               and report.get('sourceDataSHA256') == current_source_sha
               and report.get('buildArtifactsUnchangedDuringRun') is True
               and check['case']=='all-42-diagrams' and check.get('passed')]
    # Select current, clean production evidence by time, never by directory
    # spelling (an old "resume" directory would otherwise supersede "final").
    if matches:
        path,report,check = max(matches,key=lambda entry:entry[0].stat().st_mtime_ns)
        clean = not any(report.get(key) for key in ['consoleErrors','runtimeErrors','failedRequests','badResponses'])
        browser[engine] = {'report':str(path),'sourceDataSHA256':report.get('sourceDataSHA256'),
            'browserVersion':report.get('browserVersion'),'normalErrorsClean':clean,
            'rows':{row['full']['chord']:row for row in check['details']['diagrams']}}

records = []
for chord in chords:
    chord_id = chord['id']
    rendered = {}
    actual_hands = {}
    for engine,value in browser.items():
        row = value['rows'].get(chord_id)
        if row:
            rendered[engine] = {'passed':value['normalErrorsClean'],'report':value['report'],
                'fullAndCompact':True,'baseFret':row['full']['baseFret'],'stringNotes':row['full']['stringNotes'],
                'sourceDataSHA256':value['sourceDataSHA256']}
            actual_hands[engine] = row.get('actualHand',{})
    shape_check = next((check for check in music['checks'] if check['name']==chord_id+': independent reference shape and named quality'),{})
    finger_check = next((check for check in music['checks'] if check['name']==chord_id+': playable finger reuse, barre endpoints and clearance'),{})
    pose = poses.get(chord_id,{})
    approved_source = (pose.get('status') == 'verified' and pose.get('reviewed') is True
        and all(pose.get('audit',{}).get(gate) is True
                for gate in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']))
    records.append({'id':chord_id,'family':chord['type'],'voicing':chord['voicing'],'fretsLowToHigh':chord['frets'],
        'fingersLowToHigh':chord['fingers'],'notesLowToHigh':chord['notes'],'baseFret':chord['baseFret'],'barres':chord['barres'],
        'music':{'passed':shape_check.get('passed') is True and finger_check.get('passed') is True,'evidence':str(music_path)},
        'diagram':{'sourceStatus':chord['diagramStatus']['status'],
            'renderedAuditPassed':len(rendered)==2 and all(value['passed'] for value in rendered.values()),'engines':rendered},
        'hand':{'sourceStatus':chord['handPose']['status'],'candidateStatus':pose.get('status','unavailable'),
            'candidateAvailable':bool(pose and pose.get('status')!='unavailable'),'anatomicalApprovalByThisHarness':False,
            'independentSourceApproval':approved_source,
            'reviewed':pose.get('reviewed') is True,'audit':pose.get('audit',{}),'actualRuntime':actual_hands}})

report = {'schemaVersion':1,'scope':'42 independent music/diagram records; separate source hand approval and browser runtime evidence',
    'sourceDataSHA256':current_source_sha,
    'count':len(records),'summary':{'musicPassed':sum(row['music']['passed'] for row in records),
        'renderedDiagramPassed':sum(row['diagram']['renderedAuditPassed'] for row in records),
        'handCandidates':sum(row['hand']['candidateAvailable'] for row in records),
        'independentlyApprovedSourceHands':sum(row['hand']['independentSourceApproval'] for row in records),
        'handsApprovedByThisHarness':0},
    'chords':records,'limitations':['Anatomical hand contact, skin, deformation, collision, wrist, thumb and sleeve approval require separate visual/physical review.',
        'Linux Chromium with SwiftShader and Linux WebKit are not physical iPadOS Safari or iPad GPU evidence.']}
destination.parent.mkdir(parents=True,exist_ok=True)
destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'path':str(destination),'summary':report['summary']}))
