#!/usr/bin/env python3
"""Actual 42-pose rejection audit; geometric success never approves anatomy.

Requires Python NumPy/SciPy and the existing Node dependencies. Every tested
string path is exported from the runtime controller, not duplicated C targets.
Known unapproved failures remain visible in the per-chord report. --require names
the corrected batch which must pass; a rejected verified pose always fails CI.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('contact_audit', ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def transform_hash(pose):
    return hashlib.sha256(json.dumps({'root': pose['root'], 'bones': pose['bones']}, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def strictly_approved(pose):
    return pose.get('status') == 'verified' and pose.get('reviewed') is True and all(
        pose.get('audit', {}).get(gate) is True
        for gate in ['collisionPassed', 'contactPassed', 'anatomyPassed', 'multiViewReviewed'])


def clip_line(points, low, high):
    segments = []
    for start, end in zip(points[:-1], points[1:]):
        delta = end-start
        if abs(delta[0]) < 1e-10:
            if low <= start[0] <= high:
                segments.append((start, end))
            continue
        v = sorted(((low-start[0])/delta[0], (high-start[0])/delta[0]))
        first, last = max(0., v[0]), min(1., v[1])
        if last-first > 1e-9:
            segments.append((start+first*delta, start+last*delta))
    return segments


def clearance(triangles, segments, radius):
    if not len(triangles) or not segments:
        raise ValueError('Missing real surface or physical string segment')
    return min(float(a.c.segment_triangle_distances(triangles, x, y).min()) for x, y in segments)-radius


def contacts(chord):
    result = []
    for bar in chord['barres']:
        result += [{'finger': bar['finger'], 'string': s, 'fret': bar['fret'], 'kind': 'barre'}
                   for s in range(bar['fromString'], bar['toString']-1, -1)]
    for i, fret in enumerate(chord['frets']):
        if not fret:
            continue
        finger, string = chord['fingers'][i], 6-i
        if any(c['finger'] == finger and c['string'] == string and c['fret'] == fret for c in result):
            continue
        result.append({'finger': finger, 'string': string, 'fret': fret, 'kind': 'tip'})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--library', type=Path, default=ROOT/'src/features/practice/assets/hand-poses.json')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/practice-hand-batch-2/geometry')
    parser.add_argument('--require', default='C,Cmaj7,Am7')
    parser.add_argument('--chords', default='all')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    library = json.loads(args.library.read_text())
    rig = a.c.m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
    model = ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb'
    assert digest(model) == library['assetSha256'] == rig.data['sha256'], 'Wrong source GLB/rig/library hash'
    chords = json.loads(subprocess.check_output(['node', '--input-type=module', '-e',
        "import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"], cwd=ROOT))
    assert len(chords) == 42 and {c['id'] for c in chords} == set(library['poses']), 'Chord/pose IDs must stay intact'
    chosen = set(args.chords.split(',')) if args.chords != 'all' else {c['id'] for c in chords}
    required = set(filter(None, args.require.split(',')))
    assert chosen <= {c['id'] for c in chords} and required <= chosen
    rows = []
    palmar = rig.normals[rig.triangles].mean(axis=1) @ rig.palmar > .05
    dominant = rig.joint_bones[rig.joints[np.arange(len(rig.joints)), rig.weights.argmax(axis=1)]]
    with tempfile.TemporaryDirectory(prefix='fretline-hand-audit-') as temporary:
        temp = Path(temporary)
        for chord in chords:
            key = chord['id']
            if key not in chosen:
                continue
            pose = library['poses'][key]
            world = a.world_from_pose(rig, pose)
            skin = rig.skin(world)
            combined, indices, labels, sample_depths = [], [], [], []
            for mesh in rig.data['meshes']:
                points = rig.skin_mesh(world, mesh)
                faces = np.array(mesh['indices']).reshape(-1, 3)
                samples = np.vstack([points, points[faces].mean(axis=1),
                    *(points[faces[:, i]]*.5+points[faces[:, (i+1) % 3]]*.5 for i in range(3))])
                sample_depths.append(a.c.m.wood_depth(samples))
                offset = len(combined)
                combined.extend(points.tolist())
                indices.extend((np.array(mesh['indices'])+offset).tolist())
                labels.extend([mesh['name']]*len(points))
            mesh_file = temp/'combined.json'
            mesh_file.write_text(json.dumps({'positions': combined, 'indices': indices, 'dominantBones': labels}))
            self_file, guitar_file, cross_file = temp/'self.json', temp/'guitar.json', temp/'guitar-crossings.json'
            command = ['python', str(ROOT/'scripts/practice/audit-hand-self-collisions.py'), str(mesh_file), '--mesh']
            subprocess.run(command+['--output', str(self_file)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
            own = json.loads(self_file.read_text())
            depth = np.concatenate(sample_depths)
            row = {'id': key, 'voicing': chord['voicing'], 'poseTransformSha256': transform_hash(pose),
                'skinAndClothSelfCrossingPairs': own['crossingPairCount'],
                'woodSamples': len(depth), 'woodSamplesInsideOver002Mm': int((depth > .02).sum()),
                'maximumWoodDepthMm': float(depth.max()), 'guitar': {'status': 'not-run'},
                'contacts': [], 'strings': [], 'geometricPassed': False,
                'teachingStatus': pose['status'], 'anatomicalApproval': False}
            raw = {'poseTransformSha256': row['poseTransformSha256'], 'assetSha256': library['assetSha256'], 'self': own}
            # Rejected self-colliding poses never receive a positive contact claim.
            if not own['crossingPairCount']:
                subprocess.run(['node', str(ROOT/'scripts/practice/export-guitar-collision-mesh.mjs'), key, str(guitar_file)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
                guitar = json.loads(guitar_file.read_text())
                subprocess.run(command+['--against', str(guitar_file), '--output', str(cross_file)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
                cross = json.loads(cross_file.read_text())
                row['guitar'] = {'status': 'tested', 'crossingPairs': cross['crossingPairCount'], 'runtimeExportSha256': digest(guitar_file)}
                raw['guitar'] = cross
                lines = {s['number']: s for s in guitar['strings']}
                tri = skin[rig.triangles]
                for string in range(1, 7):
                    s = lines[string]
                    line = np.array(s['controlPointsMm'])
                    segments = list(zip(line[:-1], line[1:]))
                    fret = chord['frets'][6-string]
                    value = clearance(tri, segments, s['radiusMm'])
                    row['strings'].append({'number': string, 'fret': fret, 'wholeSkinClearanceMm': value,
                        'openStringPassed': value >= .2 if fret == 0 else None})
                for target in contacts(chord):
                    number = target['finger']+1
                    names = [rig.by_name[f'finger{number}-{i}.L'] for i in range(1, 4)]
                    owned = np.isin(dominant[rig.triangles], names).all(axis=1) & palmar
                    if target['kind'] == 'tip':
                        owned &= (dominant[rig.triangles] == names[-1]).any(axis=1)
                    wire = a.c.m.fret_x(target['fret'])
                    s = lines[target['string']]
                    segments = clip_line(np.array(s['controlPointsMm']), wire-6, wire-1.1)
                    value = clearance(tri[owned], segments, s['radiusMm'])
                    row['contacts'].append(target | {'actualOwnerPalmarSkinClearanceMm': value, 'passed': -.00001 <= value <= .12})
                row['geometricPassed'] = not cross['crossingPairCount'] and not row['woodSamplesInsideOver002Mm'] \
                    and all(s['openStringPassed'] is not False for s in row['strings']) \
                    and all(t['passed'] for t in row['contacts'])
            evidence = args.output/(key+'-raw.json.gz')
            with gzip.open(evidence, 'wt') as out:
                json.dump(raw, out)
            row['rawEvidence'] = evidence.name
            rows.append(row)
            print(f"{key}: self={own['crossingPairCount']} geometry={'PASS' if row['geometricPassed'] else 'FAIL'}", flush=True)
    passed = {r['id'] for r in rows if r['geometricPassed']}
    errors = [key+' corrected batch regressed' for key in sorted(required-passed)]
    errors += [r['id']+' is incorrectly labelled verified' for r in rows if r['teachingStatus'] == 'verified' and not r['geometricPassed']]
    errors += [key+' lacks independent review gates for verified status' for key, pose in library['poses'].items()
               if pose.get('status') == 'verified' and not strictly_approved(pose)]
    report = {'assetSha256': library['assetSha256'], 'librarySnapshotSha256': digest(args.library),
        'sourceChordSha256': digest(ROOT/'src/features/practice/data/chords.js'), 'count': len(rows),
        'geometricPassed': len(passed), 'verifiedTeachingHands': sum(strictly_approved(p) for p in library['poses'].values()),
        'requiredBatch': sorted(required), 'testSuitePassed': not errors, 'all42GeometricPassed': len(passed) == 42,
        'errors': errors, 'scope': 'Actual FK/LBS skin and garment triangle crossings, dense wood rejection, actual runtime exported string paths and assigned-digit palmar contact. No anatomical or physical iPad approval.',
        'rows': rows}
    (args.output/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
