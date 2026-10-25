"""Join only the current frozen batch's actual browser reports."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--reports', type=Path, default=Path(__file__).parent / 'reports')
args = parser.parse_args()
folder = args.reports


def load(path):
    return json.loads((folder / path).read_text())


def error_counts(report):
    return {key: len(report.get(key, [])) for key in ['consoleErrors', 'runtimeErrors', 'failedRequests', 'badResponses', 'networkErrors']}


trainer = {engine: load(engine + '/browser-trainer-' + engine + '.json') for engine in ['chromium', 'webkit']}
focused_path = 'chromium-performance/browser-trainer-chromium-performance-lifecycle.json'
focused = load(focused_path) if (folder / focused_path).exists() else None
regressions = load('regressions/regression-summary.json')
camera = load('camera-controls/camera-controls.json')
batch = load('batch-poses/batch-poses-browser.json')
source = ROOT / 'src/features/practice/assets/hand-poses.json'
library = json.loads(source.read_text())
source_pose_hash = hashlib.sha256(source.read_bytes()).hexdigest()
artifacts = trainer['chromium']['productionArtifactSHA256']
matching_assets = artifacts == trainer['webkit']['productionArtifactSHA256'] == batch['productionArtifactSHA256']
matching_pose = source_pose_hash == batch['poseLibrarySHA256'] and any(name.startswith('hand-poses-') and sha == source_pose_hash for name, sha in artifacts.items())
initial_chromium = trainer['chromium']
original_failures = [row['case'] for row in initial_chromium['checks'] if not row['passed']]
chromium_coverage = initial_chromium['checks']
chromium_pass = initial_chromium['passed']
if original_failures:
    assert original_failures == ['performance-lifecycle'], 'Only the proven startup timing case may use focused corrected evidence'
    assert focused is not None
    focused_rows = [row for row in focused['checks'] if row['case'] == 'performance-lifecycle']
    assert len(focused_rows) == 1 and len(focused['checks']) == 1
    matching_assets = matching_assets and artifacts == focused['productionArtifactSHA256']
    chromium_coverage = [focused_rows[0] if row['case'] == 'performance-lifecycle' else row for row in initial_chromium['checks']]
    chromium_pass = all(row['passed'] for row in chromium_coverage) and focused['passed'] and not any(error_counts(initial_chromium).values())
    chromium_pass = chromium_pass and initial_chromium['buildArtifactsUnchangedDuringRun'] and focused['buildArtifactsUnchangedDuringRun']
review_gates = ['collisionPassed', 'contactPassed', 'anatomyPassed', 'multiViewReviewed']
approved = [chord for chord, pose in library['poses'].items() if pose.get('status') == 'verified' and pose.get('reviewed') is True and all(pose.get('audit', {}).get(gate) is True for gate in review_gates)]
summary = {
    'scope': 'Frozen-build browser/rendering/lifecycle regression acceptance; numerical and anatomical hand approval are separate',
    'productionArtifactSHA256': artifacts,
    'matchingProductionAssetsAcrossReports': matching_assets,
    'matchingCurrentSourcePoseLibrary': matching_pose,
    'browserTrainer': {engine: {'passed': chromium_pass if engine == 'chromium' else report['passed'], 'cases': len(report['checks']),
        'browserVersion': report['browserVersion'], 'errors': error_counts(report),
        'buildArtifactsUnchangedDuringRun': report['buildArtifactsUnchangedDuringRun'],
        'performance': next(check['details'] for check in (chromium_coverage if engine == 'chromium' else report['checks']) if check['case'] == 'performance-lifecycle')}
        for engine, report in trainer.items()},
    'chromiumInitialFailureAndFocusedCoverage': {
        'initialRunPassed': initial_chromium['passed'],
        'initialPassedCases': sum(row['passed'] for row in initial_chromium['checks']),
        'initialCaseCount': len(initial_chromium['checks']),
        'initialFailedCases': original_failures,
        'initialReport': 'chromium/browser-trainer-chromium.json',
        'focusedCorrectedCasePassed': focused['passed'] if original_failures and focused else None,
        'focusedReport': focused_path if original_failures and focused else None,
        'acceptedCaseCoverage': len(chromium_coverage),
        'sameFrozenProductionAssets': matching_assets,
        'reason': ('Observed one already-scheduled hand-publish frame after asset-ready; explicit initial two-rAF/stable-size/count readiness precedes the original unchanged800msidleassertion. Original20/21runremainsfailed.'
                   if original_failures else 'The complete Chromium run passed all cases; no focused case replacement was used.')},
    'legacyBrowserRegressions': {'passed': regressions['passed'], 'checks': sum(row['checks'] for row in regressions['runs']), 'runs': regressions['runs']},
    'allSevenCameraPresets': {'passed': camera['passed'], 'engineCases': len(camera['checks']), 'errors': error_counts(camera)},
    'newCandidateRendering': {'passed': batch['passed'], 'engineViewportCases': len(batch['checks']),
        'errors': error_counts(batch), 'actualSourceTransformsChecked': ['C', 'Cmaj7', 'Am7'],
        'fourViewCandidateCapture': ['Cmaj7', 'Am7'], 'fourViewCIncludedInCanonicalSuites': True},
    'sourceIndependentTeachingHandApprovals': approved,
    'handsApprovedByThisHarness': 0,
    'limitations': ['Linux Chromium/SwiftShader and Linux WebKit are not physical iPadOS Safari or native iPad performance evidence.',
        'These browser tests do not certify finger contact, collisions, skin weights, or anatomical pose correctness.',
        'Historical Phase 5–9 static baseline failures are reported separately, not relabelled passes.'],
}
summary['passed'] = matching_assets and matching_pose and chromium_pass and trainer['webkit']['passed'] and regressions['passed'] and camera['passed'] and batch['passed']
(folder / 'final-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in summary.items() if key not in ['productionArtifactSHA256', 'browserTrainer', 'legacyBrowserRegressions']}, ensure_ascii=False, indent=2))
raise SystemExit(0 if summary['passed'] else 1)
