"""Verify every protected pre-redesign input against its Git-bound baseline."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];DIR=Path(__file__).resolve().parent
baseline=json.loads((DIR/'before/baseline.json').read_text());hashes=baseline['protectedSHA256']
changed=[name for name,digest in hashes.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
old_scores=json.loads((ROOT/'docs/premium-quiz-compare/tests/baseline-scores.json').read_text())
report={'baselineCommit':baseline['baselineCommit'],'protectedFiles':len(hashes),'changedProtectedFiles':changed,'scoringAndDataByteIdentical':not changed,'previouslyFrozenAnswerCombinations':len(old_scores['combinations']),'previouslyFrozenRecommendationRecords':sum(len(x['matches']) for x in old_scores['combinations']),'note':'All original scoring/data files remain byte-identical; browser acceptance also compares resulting IDs/scores/reasons with frozen fixtures. This does not certify physical iPad Safari.'}
report['passed']=not changed
(DIR/'preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));assert report['passed'],changed
