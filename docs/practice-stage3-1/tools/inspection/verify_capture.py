"""Compare actual browser deformed vertices to the independent GLB evaluator.
This verifies rendering identity, never playable chord/contact correctness.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'audit'))
from skin_from_glb import evaluate

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=Path, required=True)
parser.add_argument('--capture-dir', type=Path, required=True)
parser.add_argument('--engine', choices=['chromium', 'webkit'], required=True)
parser.add_argument('--source', type=Path, default=Path('/tmp/fretline-stage3-assets/fk-source-gltf-compatible.json'))
args = parser.parse_args()
config_path = args.config.resolve(); config = json.loads(config_path.read_text())
model_path = (config_path.parent / config['modelUrl']).resolve()
pose_path = (config_path.parent / config['poseUrl']).resolve() if config.get('poseUrl') else None
expected, metadata = evaluate(model_path, pose_path, args.source)
actual = json.loads((args.capture_dir / f'{args.engine}-vertices.json').read_text())
capture = json.loads((args.capture_dir / f'{args.engine}-capture-report.json').read_text())
assert metadata['glbSHA256'] == capture['proof']['modelSha256']
meshes = {}
for name, mesh in expected.items():
    points = np.array(actual[name]); target = mesh['positions']
    assert points.shape == target.shape, (name, points.shape, target.shape)
    delta = np.linalg.norm(points - target, axis=1)
    meshes[name] = {'vertices': len(points), 'maxErrorMm': float(delta.max()), 'meanErrorMm': float(delta.mean()), 'matchesWithinPointOneMm': bool(delta.max() < .1)}
assert set(expected) == set(actual), (list(expected), list(actual))
hashes = {view['screenshot']: hashlib.sha256((args.capture_dir / view['screenshot']).read_bytes()).hexdigest()
          for check in capture['checks'] for view in check['views']}
report = {'scope': 'Numerical identity of actual browser scene and independently audited mesh; NOT chord/contact approval',
          'engine': args.engine, 'modelSha256': metadata['glbSHA256'], 'meshes': meshes,
          'allVertexComparisonsPassed': all(row['matchesWithinPointOneMm'] for row in meshes.values()),
          'renderingChecksPassed': capture['passedRenderingChecks'], 'screenshotSha256': hashes,
          'poseApproved': False}
out = args.capture_dir / f'{args.engine}-runtime-transfer-validation.json'
out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ['engine', 'meshes', 'allVertexComparisonsPassed', 'renderingChecksPassed', 'poseApproved']}, indent=2))
