"""Make an explicit viewer config from an actual GLB and a research pose.

This only proves numerical pose conversion. It never approves contact geometry.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'audit'))
from skin_from_glb import evaluate, trs, euler_xyz

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=Path, required=True)
parser.add_argument('--pose', type=Path, required=True)
parser.add_argument('--source', type=Path, default=Path('/tmp/fretline-stage3-assets/fk-source-gltf-compatible.json'))
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--label', required=True)
parser.add_argument('--baked-mm', action='store_true', help='Actual exported scene already uses canonical mm')
parser.add_argument('--height-map-fix', action='store_true', help='Original source grayscale normal is really height')
args = parser.parse_args()
args.model = Path(os.path.abspath(args.model)); args.pose = args.pose.resolve(); args.output = args.output.resolve()
args.output.parent.mkdir(parents=True, exist_ok=True)
pose = json.loads(args.pose.read_text())
raw = args.model.read_bytes(); json_length = struct.unpack_from('<I', raw, 12)[0]
glb = json.loads(raw[20:20 + json_length]); parents = {child: i for i, node in enumerate(glb['nodes']) for child in node.get('children', [])}
original_world = {}

def world(index):
    if index not in original_world:
        original_world[index] = (world(parents[index]) if index in parents else np.eye(4)) @ trs(glb['nodes'][index])
    return original_world[index]

for index in range(len(glb['nodes'])): world(index)

if args.baked_mm:
    runtime_pose = {'status': 'Unvalidated already-posed mesh; not instructional approval', 'mmFromGLTF': np.eye(4).T.reshape(-1).tolist(), 'jointLocals': {}, 'poseSource': str(args.pose)}
elif 'jointLocals' in pose:
    runtime_pose = dict(pose)
elif 'angles' in pose:
    source = json.loads(args.source.read_text()); bones = source['bones']; names = [bone['name'] for bone in bones]
    rest = np.array([bone['matrix'] for bone in bones]); inverse = np.linalg.inv(rest); posed = []
    for index, bone in enumerate(bones):
        parent = names.index(bone['parent']) if bone['parent'] else -1
        relative = inverse[parent] @ rest[index] if parent >= 0 else rest[index]
        basis = np.eye(4); basis[:3, :3] = euler_xyz(pose['angles'][bone['name']])
        posed.append((posed[parent] @ relative if parent >= 0 else relative) @ basis)
    deform = np.array(posed) @ inverse
    axes = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.]])
    wanted = {index: axes @ deform[names.index(node['name'])] @ axes.T @ original_world[index]
              for index, node in enumerate(glb['nodes']) if node.get('name') in names}
    locals = {glb['nodes'][index]['name']: (np.linalg.inv(wanted.get(parents.get(index), original_world.get(parents.get(index), np.eye(4)))) @ matrix).T.reshape(-1).tolist()
              for index, matrix in wanted.items()}
    q = np.array(pose['q']); outer = np.eye(4); outer[:3, :3] = euler_xyz(q[:3]) @ np.diag([-1, 1, 1]) * q[6]; outer[:3, 3] = q[3:6]
    runtime_pose = {'status': 'Numerical matrix conversion only; NOT CONTACT APPROVED', 'jointLocals': locals, 'mmFromGLTF': (outer @ axes.T).T.reshape(-1).tolist(), 'poseSource': str(args.pose)}
else:
    raise ValueError('Pose needs jointLocals or native angles/q, unless --baked-mm is explicitly supplied')

offsets = pose.get('pressOffsetsMm') or pose.get('pressOffsetsBeforeWireMM') or [4, 4, 4]
runtime_pose['pressOffsetsMm'] = offsets
if pose.get('stringPathsMm') is not None:
    runtime_pose['stringPathsMm'] = pose['stringPathsMm']
runtime_pose['modelSha256'] = hashlib.sha256(raw).hexdigest()
runtime_path = args.output.with_name(args.output.stem + '-runtime-pose.json')
runtime_path.write_text(json.dumps(runtime_pose, indent=2) + '\n')
config = {'label': args.label, 'modelUrl': os.path.relpath(args.model, args.output.parent), 'poseUrl': os.path.relpath(runtime_path, args.output.parent),
          'modelSha256': runtime_pose['modelSha256'], 'applyJointPose': not args.baked_mm,
          'grayscaleNormalIsHeight': args.height_map_fix, 'pressOffsetsMm': offsets,
          'modifications': ['See candidate pose and model repair provenance; this config does not approve the result.']}
args.output.write_text(json.dumps(config, indent=2) + '\n')

expected, _ = evaluate(args.model, None if args.baked_mm else args.pose, args.source, baked_mm=args.baked_mm)
actual, _ = evaluate(args.model, runtime_path, args.source, baked_mm=args.baked_mm)
errors = {name: float(np.linalg.norm(mesh['positions'] - actual[name]['positions'], axis=1).max()) for name, mesh in expected.items()}
assert all(error < .001 for error in errors.values()), errors
report = {'scope': 'numerical viewer pose conversion only; does not approve anatomy/contact', 'passed': True, 'maxPositionErrorMm': errors,
          'modelSha256': runtime_pose['modelSha256'], 'config': str(args.output), 'runtimePose': str(runtime_path)}
args.output.with_name(args.output.stem + '-conversion-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
