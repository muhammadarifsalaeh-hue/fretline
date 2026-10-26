"""Accept this feature review from actual outputs, without erasing historical failures."""
from pathlib import Path
import json,hashlib,itertools
ROOT=Path(__file__).resolve().parents[3];DIR=ROOT/'docs/yamaha-import';TEST=DIR/'tests'
def read(p):return json.loads((TEST/p).read_text())
browser=read('final/browser-results.json');assert browser['passed'] and len(browser['checks'])==280 and all(c['passed'] for c in browser['checks'])
assert browser['sourceAndBuildUnchangedDuringRun']
for key in ['consoleErrors','runtimeErrors','networkErrors','harnessFailures']:assert not browser.get(key),key
for file,expected in browser['sourceAndBuildSHA256'].items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==expected,file
ids=[m['guitarId'] for m in json.loads((DIR/'preview-manifest.json').read_text())['models']]
cases={c['case'] for c in browser['checks']};assert len(cases)==280
for engine,mode,viewport,gid in itertools.product(['chromium','webkit'],['production','preview'],['desktop','tablet','mobile'],ids):assert f'{engine}-{mode}-{viewport}-{gid}' in cases
core=read('core/results.json');current=[x for x in core if not any('phase'+str(i)+':check' in x['command'] for i in range(5,10))];assert all(x['exitCode']==0 for x in current)
data=read('data-check.json');assert data['passed'] and len(data['checks'])==11
preserved=read('preservation.json');assert preserved['passed'] and all(c['passed'] for c in preserved['checks'])
shots=read('screenshots/captures.json');assert shots['passed'] and len(shots['captures'])==14 and not shots['errors']
filters=read('price-filters.json');assert filters['passed'] and len(filters['checks'])==6
isolation=read('direct-asset-isolation.json');assert isolation['passed'] and len(isolation['checks'])==8
gallery=read('legacy-gallery-final/regression/browser-production.json');assert gallery['passed'] and len(gallery['checks'])==79
shared=read('legacy-shared-final/shared-regression.json');failed=[c['case'] for c in shared['checks'] if not c['passed']];assert failed==['price-1440'],failed
assert not any(shared.get(k) for k in ['consoleErrors','runtimeErrors','failedRequests','harnessFailure'])
static_failed=[x for x in core if x['exitCode']!=0];assert len(static_failed)==5
standalone=read('core/phase8-catalog-standalone.json');assert standalone['exitCode']==1
summary={'featureReviewAcceptancePassed':True,'allHistoricalTestsPassed':False,'all19ArchivesPresent':False,'allAccessibleInputsProcessed':True,'availableArchives':18,'requestedArchives':19,'missingConfirmedArchiveModel':'FGX830C','newImageFiles':20,'newImageLicensesVerified':0,'productionNewImages':0,'previewImageModels':18,'THBPricesConfirmed':17,'priceUnconfirmed':['FG800J'],'catalogModels':200,'brands':10,'modelsPerBrand':20,'practiceModified':False,'masterMerged':False,'browserCasesPassed':280,'browserVersions':browser.get('browserVersions'),'consoleErrors':0,'runtimeErrors':0,'networkErrors':0,'dataEvidenceChecksPassed':11,'previewPluginChecksPassed':13,'actualDevAssetIsolationChecksPassed':8,'preservationChecksPassed':8,'reviewScreenshots':14,'legacyGalleryPassed':79,'legacySharedPassed':17,'legacySharedTotal':18,'legacySharedRemainingFailure':'The old price-1440 fixture expects no prices below THB30000; 17 newly sourced Yamaha prices now exist. Original test unchanged; current-boundary regression passed6/6.','currentPriceFilterChecksPassed':6,'legacyStaticFailures':[x['command'] for x in static_failed],'legacyAdditionalCatalogCheckPassed':False,'physicalIPadSafariTested':False,'readyForAutomaticMasterMerge':False,'reviewedDataSHA256':data['sourceSha256']}
(TEST/'acceptance.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
