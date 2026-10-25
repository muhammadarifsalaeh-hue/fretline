"""Run unchanged shared/gallery/camera acceptance with isolated trainer output.

Requires an already-built and running preview. This script does not build,
start servers, install dependencies, edit application files, or approve hands.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'reports' / 'regressions')
parser.add_argument('--cases', default='shared,gallery,camera-chromium,camera-webkit')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, FRETLINE_QA_URL=args.url, FRETLINE_QA_OUTPUT_DIR=str(args.output),
           FRETLINE_QA_REPORT='shared-regression.json', FRETLINE_QA_RUN='practice-trainer')
env.pop('FRETLINE_QA_CASES', None)
env.setdefault('PLAYWRIGHT_BROWSERS_PATH', '/tmp/fretline-browser-engines')
env.setdefault('PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS', '1')
env.setdefault('XDG_CACHE_HOME', '/tmp/fretline-webkit-cache')
env.setdefault('XDG_CONFIG_HOME', '/tmp/fretline-webkit-config')
env.setdefault('GSETTINGS_BACKEND', 'memory')
commands = {
    'shared': ([sys.executable, str(ROOT / 'docs/practice-stage1-2/tests/shared-regression.py')], args.output / 'shared-regression.json', 18),
    'gallery': ([sys.executable, str(ROOT / 'docs/signature-redesign/phase-c-final/tests/regression-gallery.py')], args.output / 'regression/browser-practice-trainer.json', 79),
}
for engine in ['chromium', 'webkit']:
    output = args.output / ('camera-' + engine)
    commands['camera-' + engine] = ([sys.executable, str(ROOT / 'docs/practice-stage3-3/tests/browser-camera.py'), '--url', args.url,
                                    '--engine', engine, '--output', str(output)], output / ('camera-orientation-' + engine + '.json'), 5)
summary = {'url': args.url, 'scope': 'Existing shared/gallery/camera regressions; no anatomical hand approval', 'runs': []}
for name in args.cases.split(','):
    command, report_path, expected_count = commands[name]
    with (args.output / (name + '.log')).open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    count = len(report.get('checks', []))
    row = {'case': name, 'returncode': result.returncode, 'report': str(report_path), 'checks': count,
           'expectedChecks': expected_count, 'passed': result.returncode == 0 and report.get('passed') is True and count == expected_count}
    summary['runs'].append(row)
    print(('PASS' if row['passed'] else 'FAIL'), name, f'{count}/{expected_count}', flush=True)
summary['passed'] = bool(summary['runs']) and all(row['passed'] for row in summary['runs'])
(args.output / 'regression-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
raise SystemExit(0 if summary['passed'] else 1)
