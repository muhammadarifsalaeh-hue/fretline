"""Exercise all original gallery assertions through the new Compare category UI.

The unchanged original suite expects every extended specification to be visible
at once. The new page intentionally opens its Main category; this adapter selects
All at the single Compare visit, retaining every original assertion verbatim.
The raw unadapted failure remains under legacy-final/.
"""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[3]
source_path = ROOT / 'docs/signature-redesign/phase-c-final/tests/regression-gallery.py'
source = source_path.read_text()
needle = "        page.goto(BASE + '/compare?ids=' + ID + ',yamaha-fg800', wait_until='networkidle')"
assert source.count(needle) == 1, 'Review the adapter after an original harness change'
source = source.replace(needle, needle + "\n        page.locator('[data-compare-category=\"all\"]').click()", 1)
os.environ.setdefault('FRETLINE_QA_URL', 'http://127.0.0.1:5451')
os.environ.setdefault('FRETLINE_QA_OUTPUT_DIR', str(ROOT / 'docs/premium-quiz-compare/tests/category-adapted-gallery'))
os.environ.setdefault('FRETLINE_QA_RUN', 'premium-category-adapter')
exec(compile(source, str(source_path), 'exec'), {'__file__': str(source_path), '__name__': '__main__'})
