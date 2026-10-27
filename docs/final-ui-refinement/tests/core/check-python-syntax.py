"""Parse original Python scripts without writing bytecode or changing files."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
files = sorted((ROOT / 'scripts').rglob('*.py'))
for file in files:
    ast.parse(file.read_text(), filename=str(file.relative_to(ROOT)))
print(f'PASS Python syntax parsing: {len(files)} scripts')
