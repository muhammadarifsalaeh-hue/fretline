"""Serial existing acceptance plus new actual candidate rendering checks.

Requires the root agent to freeze/build the app and start production preview.
This runner never edits app files, builds, installs, or certifies hand anatomy.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:5430')
parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'reports')
parser.add_argument('--chords', default='Em7')
parser.add_argument('--cases', default='chromium,webkit,regressions,camera-controls,batch-poses,hand-reveal,summary')
args = parser.parse_args()
args.output = args.output.resolve()
args.output.mkdir(parents=True, exist_ok=True)
env = dict(os.environ)
env.setdefault('PLAYWRIGHT_BROWSERS_PATH', '/tmp/fretline-browser-engines')
env.setdefault('PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS', '1')
env.setdefault('XDG_CACHE_HOME', '/tmp/fretline-webkit-cache')
env.setdefault('XDG_CONFIG_HOME', '/tmp/fretline-webkit-config')
env.setdefault('GSETTINGS_BACKEND', 'memory')
extra_libs = '/tmp/fretline-webkit-libs/usr/lib/x86_64-linux-gnu'
if Path(extra_libs).is_dir():
    env['LD_LIBRARY_PATH'] = extra_libs + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')

commands = []
for engine in ['chromium', 'webkit']:
    commands.append((engine, [sys.executable, str(Path(__file__).with_name('run-trainer-settled.py')),
                     '--url', args.url, '--engine', engine, '--output', str(args.output / engine)]))
commands += [
    ('regressions', [sys.executable, str(ROOT / 'docs/practice-trainer/tests/run-regressions.py'),
                     '--url', args.url, '--output', str(args.output / 'regressions')]),
    ('camera-controls', [sys.executable, str(ROOT / 'docs/practice-trainer/tests/camera-controls.py'),
                     '--url', args.url, '--output', str(args.output / 'camera-controls')]),
    ('batch-poses', [sys.executable, str(Path(__file__).with_name('batch-poses-browser.py')),
                     '--url', args.url, '--output', str(args.output / 'batch-poses'), '--chords', args.chords]),
    ('hand-reveal', [sys.executable, str(Path(__file__).with_name('hand-reveal-browser.py')),
                     '--url', args.url, '--output', str(args.output / 'hand-reveal')]),
    ('summary', [sys.executable, str(Path(__file__).with_name('summarize.py')),
                     '--reports', str(args.output)]),
]
summary = {'scope': 'Browser/runtime/regression checks only; hand anatomy and physical iPad approval are separate', 'runs': []}
for name, command in commands:
    if name not in args.cases.split(','):
        continue
    with (args.output / (name + '.txt')).open('w') as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
    summary['runs'].append({'name': name, 'returncode': result.returncode, 'passed': result.returncode == 0})
    print(('PASS' if result.returncode == 0 else 'FAIL'), name, flush=True)
summary['passed'] = all(row['passed'] for row in summary['runs'])
(args.output / 'run-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
raise SystemExit(0 if summary['passed'] else 1)
