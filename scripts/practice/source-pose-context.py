"""Read the immutable authoring baseline without checking out or resetting files.

Runtime poses can advance while offline fitting starts from the audited source.
Accepted endpoints are adopted separately only through their exact mesh reports.
"""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np

BASELINE='218eab5a1b72125b7981b01ebe8aa417dd58fef7'

def load_source_context(previous):
    root=Path(__file__).resolve().parents[2]
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    data=subprocess.check_output(['git','show',BASELINE+':src/features/practice/assets/hand-poses.json'],cwd=root)
    library=json.loads(data);library_sha=hashlib.sha256(data).hexdigest()
    gate=previous.gate;math=previous.m
    rig=math.Rig(root/'docs/practice-trainer/models/authoring/rig-data.json')
    model_sha=sha(root/'src/features/practice/assets/makehuman-left-arm-sleeved.glb')
    chord_sha=sha(root/'src/features/practice/data/chords.js')
    prior=json.loads((root/'docs/practice-hand-batch-3/geometry/summary.json').read_text())
    assert prior['librarySnapshotSha256']==library_sha
    assert model_sha==rig.data['sha256']==library['assetSha256']==prior['assetSha256']
    assert prior['sourceChordSha256']==chord_sha
    chords=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=root))
    ids={c['id'] for c in chords}
    assert len(chords)==42 and ids==set(library['poses'])
    assert prior['count']==42 and len(prior['rows'])==42 and {r['id']for r in prior['rows']}==ids
    assert prior['testSuitePassed'] is True and prior['errors']==[]
    assert all(r['poseTransformSha256']==gate.transform_hash(library['poses'][r['id']])for r in prior['rows'])
    accepted={r['id']for r in prior['rows']if r['geometricPassed'] is True}
    assert accepted=={'C','Dm','E7','Cmaj7','Fmaj7','Em7','Am7'}
    dominant=rig.joint_bones[rig.joints[np.arange(len(rig.joints)),rig.weights.argmax(1)]]
    palmar=rig.normals[rig.triangles].mean(1)@rig.palmar>.05
    faces={}
    for finger in math.FINGERS:
        names=[rig.by_name[f'finger{math.NUMBERS[finger]}-{i}.L']for i in range(1,4)]
        owned=np.isin(dominant[rig.triangles],names).all(1)&palmar
        faces[finger,'barre']=rig.triangles[owned]
        faces[finger,'tip']=rig.triangles[owned&(dominant[rig.triangles]==names[-1]).any(1)]
    return {'library':library,'library_sha':library_sha,'model_sha':model_sha,'chord_sha':chord_sha,
            'rig_sha':sha(root/'docs/practice-trainer/models/authoring/rig-data.json'),'rig':rig,
            'chords':{c['id']:c for c in chords},'accepted':accepted,'faces':faces,'dominant':dominant}
