#!/usr/bin/env python3
"""Bounded F/Fmaj7 authoring experiment; never a pose approval.

Keeps the source chord voicing and original rig/weights. F starts from the
audited C hand, freezes the safe thumb chain, and updates real palmar triangle
correspondences. Fmaj7 keeps the actual saved C root/wrist/index and solves only
the middle/ring chains. Every output remains needs-review until the unchanged
external triangle/contact audit and independent visual review are completed.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


g = module('library_fitter', ROOT/'scripts/practice/generate-pose-library.py')
a = module('actual_contacts', ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
m = g.solver


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_combined(rig, pose, path):
    world = a.world_from_pose(rig, pose)
    positions, indices, labels = [], [], []
    for mesh in rig.data['meshes']:
        vertices = rig.skin_mesh(world, mesh)
        offset = len(positions)
        positions.extend(vertices.tolist())
        indices.extend((np.array(mesh['indices'])+offset).tolist())
        labels.extend([mesh['name']]*len(vertices))
    path.write_text(json.dumps({'positions': positions, 'indices': indices, 'dominantBones': labels}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chord', choices=['F', 'Fmaj7'], default='F')
    ap.add_argument('--evaluations', type=int, default=40)
    args = ap.parse_args()
    chord = next(c for c in g.central_chords() if c['id'] == args.chord)
    assert (chord['frets'], chord['fingers']) == ({
        'F': ([1, 3, 3, 2, 1, 1], [1, 3, 4, 2, 1, 1]),
        'Fmaj7': ([None, None, 3, 2, 1, 0], [None, None, 3, 2, 1, None]),
    }[args.chord]), 'Do not modify musical data to fit the hand'
    out = ROOT/'docs/practice-hand-batch-3'/args.chord
    out.mkdir(parents=True, exist_ok=True)
    library = json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text())
    seed = copy.deepcopy(library['poses']['C'])
    rig = m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
    assert sha(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb') == rig.data['sha256'] == seed['assetSha256']
    targets = g.targets_for(chord)
    history = []
    if args.chord == 'F':
        fitter = g.LibraryFitter(rig)
        x = np.array(seed['authoringSource']['sourceSolverParameters'])
        x[2] += 18
        x[6:10] = np.deg2rad([48, 24, 0, 0])
        x[18:22] = np.deg2rad([35, 0, 65, 35])
        lower, upper = m.bounds()
        lower = np.r_[lower, -1.4]
        upper = np.r_[upper, 1.4]
        lower[2] = -180
        lower[3:6], upper[3:6] = -1.8, 1.8
        lower[6:10] = np.deg2rad([0, -35, 0, 0])
        upper[6:10] = np.deg2rad([100, 35, 20, 18])
        # Freeze the audited thumb, rather than allowing the original solver
        # to drive its CMC axial rotation into a self-intersection.
        active = np.arange(22)
        for weight in [0.4, 2.]:
            correspondences = fitter.correspondences(x, targets)
            base = x.copy()

            def residual(values):
                current = base.copy()
                current[active] = values
                raw = fitter.residual(current, chord, targets, correspondences, weight)
                # Maintain a conservative neighbourhood of the safe C pose.
                # Exact self-intersections are still an independent rejection.
                return np.r_[raw, (current[6:22]-base[6:22])*.4]

            result = least_squares(residual, x[active], bounds=(lower[active], upper[active]),
                max_nfev=args.evaluations, x_scale='jac', ftol=1e-6)
            x[active] = result.x
            history.append({'weight': weight, 'evaluations': result.nfev, 'cost': float(result.cost),
                'success': bool(result.success), 'termination': result.message})
        pose = m.write_candidate(rig, x, targets, out/'candidate.json')
    else:
        pose = seed
        # Keep the actual counter-wrist root and safe original index/thumb.
        base = np.array(seed['authoringSource']['sourceSolverParameters'])
        fitted = base.copy()
        for finger in ['middle', 'ring']:
            slot = slice(6+4*m.FINGERS.index(finger), 10+4*m.FINGERS.index(finger))
            target = next(t for t in targets if t['finger'] == finger)
            original = fitted[slot].copy()
            initial_world = a.world_from_pose(rig, pose)
            fingertip = rig.skin(initial_world, rig.patch_ids[finger]).mean(0)
            desired = fingertip.copy()
            desired[0] = target['positionMm'][0]
            desired[2] = target['positionMm'][2]
            desired[1] = target['positionMm'][1] + .4
            names = [f'finger{m.NUMBERS[finger]}-{i}.L' for i in range(1, 4)]

            def candidate(values):
                current = copy.deepcopy(pose)
                p = fitted.copy()
                p[slot] = values
                q = rig.rotations(p)
                for name in names:
                    current['bones'][name]['quaternion'] = q[rig.by_name[name]].tolist()
                return current

            def residual(values):
                world = a.world_from_pose(rig, candidate(values))
                points = rig.skin(world)
                tip = points[rig.patch_ids[finger]].mean(0)
                depth = m.wood_depth(points[rig.finger_vertex_ids[finger]])
                return np.r_[(tip-desired)*2, depth*5, (values-original)*.12]

            result = least_squares(residual, original,
                bounds=(original-np.deg2rad([25, 25, 25, 25]), original+np.deg2rad([25, 25, 25, 25])),
                max_nfev=args.evaluations, ftol=1e-9, xtol=1e-9, gtol=1e-9)
            pose = candidate(result.x)
            fitted[slot] = result.x
            history.append({'finger': finger, 'evaluations': result.nfev, 'cost': float(result.cost),
                'success': bool(result.success), 'termination': result.message,
                'angularDeltaDegrees': np.rad2deg(result.x-original).tolist()})
    pose['chordId'] = args.chord
    pose['targets'] = targets
    pose['status'] = 'needs-review'
    pose['reviewed'] = False
    pose['audit'] = {key: False for key in ['collisionPassed', 'contactPassed', 'anatomyPassed', 'multiViewReviewed']}
    pose['reason'] = {'en': 'Bounded real-skin authoring candidate. Full unchanged external audit and anatomical review pending.',
        'th': 'ต้นแบบจากผิวมือจริง ยังรอตรวจการชนและตรวจท่าทางอิสระ'}
    pose['authoringSource'] = {'baseCommit': '74c2076', 'seedChord': 'C', 'modelSha256': rig.data['sha256'],
        'centralChordSha256': sha(ROOT/'src/features/practice/data/chords.js'), 'stages': history}
    (out/'candidate.json').write_text(json.dumps(pose, indent=2)+'\n')
    (out/'authoring.json').write_text(json.dumps({'chord': args.chord, 'stages': history, 'status': 'needs-review'}, indent=2)+'\n')
    write_combined(rig, pose, out/'combined-mesh.json')
    alternate = copy.deepcopy(library)
    alternate['poses'][args.chord] = pose
    (out/'candidate-library.json').write_text(json.dumps(alternate))
    print(json.dumps({'candidate': str(out/'candidate.json'), 'stages': history}, indent=2))


if __name__ == '__main__':
    main()
