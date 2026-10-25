#!/usr/bin/env python3
"""Real-mesh negative regressions; test fixtures never edit musical data."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
library_path = ROOT/'src/features/practice/assets/hand-poses.json'
chord_path = ROOT/'src/features/practice/data/chords.js'
chord_sha = hashlib.sha256(chord_path.read_bytes()).hexdigest()
library = json.loads(library_path.read_text())
seed = json.loads((ROOT/'docs/practice-hand-batch-2/Am7/seed-C-runtime.json').read_text())
fixtures = []
# A shared name/ID cannot turn a C hand pressing B1 into Cmaj7's open B.
wrong = copy.deepcopy(library)
wrong['poses']['Cmaj7'] = copy.deepcopy(seed)
wrong['poses']['Cmaj7']['chordId'] = 'Cmaj7'
fixtures.append(('reject unchanged C hand labelled Cmaj7', wrong, 'Cmaj7', 'guitar'))
# Translation preserves the hand's self-shape but drives its fingertips into wood.
wrong = copy.deepcopy(library)
wrong['poses']['C']['root']['positionMm'][1] -= 10
fixtures.append(('reject a geometrically intact hand inside the neck', wrong, 'C', 'wood'))
# The physical finger must reach the selected fret, not merely any point on B/D/A.
wrong = copy.deepcopy(library)
wrong['poses']['C']['root']['positionMm'][0] += 20
fixtures.append(('reject fingertips displaced to the wrong fret region', wrong, 'C', 'fret'))
# Geometric contact alone cannot award independent anatomical/visual approval.
wrong = copy.deepcopy(library)
wrong['poses']['C']['status'] = 'verified'
wrong['poses']['C']['reviewed'] = False
wrong['poses']['C']['audit']['anatomyPassed'] = False
fixtures.append(('reject verified status without independent review gates', wrong, 'C', 'approval'))

with tempfile.TemporaryDirectory(prefix='fretline-hand-regression-') as temporary:
    folder = Path(temporary)
    for index, (label, fixture, key, failure) in enumerate(fixtures):
        file, output = folder/f'{index}.json', folder/f'report-{index}'
        file.write_text(json.dumps(fixture))
        result = subprocess.run(['python', str(ROOT/'scripts/practice/check-hand-geometry.py'),
            '--library', str(file), '--chords', key, '--require', key, '--output', str(output)],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        report = json.loads((output/'summary.json').read_text())
        row = report['rows'][0]
        assert result.returncode == 1 and not report['testSuitePassed'], (label, result.stdout)
        if failure != 'approval':
            assert not row['geometricPassed'], (label, result.stdout)
        if failure == 'guitar':
            assert row['guitar']['crossingPairs'] > 0 and any(s['openStringPassed'] is False for s in row['strings'])
        elif failure == 'wood':
            assert row['woodSamplesInsideOver002Mm'] > 0
        elif failure == 'fret':
            assert any(contact['passed'] is False for contact in row['contacts'])
        else:
            assert row['geometricPassed'] and report['verifiedTeachingHands'] == 0
            assert any('independent review gates' in error for error in report['errors'])
        print('PASS '+label, flush=True)
assert hashlib.sha256(chord_path.read_bytes()).hexdigest() == chord_sha
assert json.loads(library_path.read_text()) == library
print('4/4 real-mesh negative regressions passed; musical and runtime data untouched.')
