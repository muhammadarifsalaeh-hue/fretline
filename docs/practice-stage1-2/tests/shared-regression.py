"""Run existing shared regressions without overwriting Phase B evidence.

Only its hard-coded output path is redirected. Test bodies stay unchanged.
The original script's __file__ is preserved for its repository path resolution.
"""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[3]
original = ROOT / 'docs/signature-redesign/phase-b/tests/acceptance.py'
output = ROOT / 'docs/practice-stage1-2'
output.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('FRETLINE_QA_OUTPUT_DIR', str(output))
os.environ.setdefault('FRETLINE_QA_REPORT', 'shared-regression.json')
source = original.read_text()
old = 'OUT = Path(__file__).resolve().parents[1]'
assert source.count(old) == 1, 'Revisit the output adapter after a source harness change'
adapted = source.replace(old, "OUT = Path(os.environ['FRETLINE_QA_OUTPUT_DIR'])", 1)
exec(compile(adapted, str(original), 'exec'), {'__file__': str(original), '__name__': '__main__'})
