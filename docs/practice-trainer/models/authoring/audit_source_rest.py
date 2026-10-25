"""Audit the final exported skin and continuous sleeve together at rest.

This reconstructs positions from the actual GLB buffer inspection. It does not
certify any chord pose. NumPy and SciPy are required by the crossing diagnostic.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
AUTHOR = Path(__file__).resolve().parent
ASSET = ROOT / 'src/features/practice/assets/makehuman-left-arm-sleeved.glb'
rig = json.loads((AUTHOR / 'rig-data.json').read_text())
asset_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
assert rig['sha256'] == asset_sha, 'Run inspect_exported_rig.py for this GLB first'

positions = []
indices = []
for mesh in rig['meshes']:
    local = np.asarray(mesh['positions'])
    world = np.asarray(mesh['meshNodeWorldMatrix'])
    points = (world @ np.column_stack((local, np.ones(len(local)))).T).T[:, :3]
    triangles = np.asarray(mesh['indices']).reshape(-1, 3) + len(positions)
    positions.extend(points.tolist())
    indices.extend(triangles.tolist())

with tempfile.TemporaryDirectory(prefix='fretline-source-rest-') as temporary:
    candidate = Path(temporary) / 'combined-rest-mesh.json'
    output = Path(temporary) / 'crossings.json'
    candidate.write_text(json.dumps({'positions': positions, 'indices': indices}))
    subprocess.run([
        sys.executable, str(ROOT / 'scripts/practice/audit-hand-self-collisions.py'),
        str(candidate), '--mesh', '--output', str(output),
    ], check=True)
    report = json.loads(output.read_text())

report.update({
    'candidate': str(ASSET.relative_to(ROOT)),
    'assetFile': str(ASSET.relative_to(ROOT)),
    'assetSha256': asset_sha,
    'sourcePose': 'unposed source; actual mesh-node world transforms',
    'poseVerified': False,
    'reproductionScript': str(Path(__file__).relative_to(ROOT)),
})
target = AUTHOR / 'rest-triangle-crossing-audit.json'
target.write_text(json.dumps(report, indent=2) + '\n')
print(f'Wrote {target.relative_to(ROOT)}')
if report['crossingPairCount']:
    sys.exit('Source rest mesh contains nonadjacent triangle intersections')
