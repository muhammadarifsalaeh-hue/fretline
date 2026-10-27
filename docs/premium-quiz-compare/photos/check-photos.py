"""Inspect actual local source/derivative files, not just metadata existence."""
from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];DOC=Path(__file__).resolve().parent
m=json.loads((DOC/'manifest.json').read_text());checks=[]
def test(name,passed):
 checks.append({'name':name,'passed':bool(passed)});assert passed,name;print('PASS',name,flush=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
test('five real editorial sources and fifteen distinct local WebP variants',m['sourcePhotos']==5 and m['localWebPDerivatives']==15 and len(m['images'])==5)
files=[]
for p in m['images']:
 source=DOC/p['sourceDownload']['localFile'];im=Image.open(source);im.load()
 test(p['id']+' retained source bytes and dimensions',sha(source)==p['sourceDownload']['sha256'] and im.size==(p['sourceDownload']['width'],p['sourceDownload']['height']))
 test(p['id']+' source is editorial, license/source recorded, not catalog model evidence',p['kind']=='editorial-photograph' and p['selectedProductEvidence'] is False and p['endorsementImplied'] is False and p['license']=='Unsplash License' and p['licenseUrl']=='https://unsplash.com/license' and p['sourceUrl'].startswith('https://unsplash.com/photos/') and p['rightsEvidence']['assertion']=='Free to use under the Unsplash License' and p['sourceDownload']['httpStatus']==200)
 widths=[v['width'] for v in p['variants']];test(p['id']+' responsive widths',widths==([480,960,1600] if p['id'].endswith('Hero') else [360,480,720]))
 for v in p['variants']:
  path=ROOT/'src/assets/discovery'/v['file'];variant=Image.open(path);variant.load();files.append(path)
  test(v['file']+' is decoded WebP, checksum-bound, proportional and source-sized',variant.format=='WEBP' and variant.size==(v['width'],v['height']) and sha(path)==v['sha256'] and path.stat().st_size==v['bytes'] and v['width']<=im.width and abs(v['width']/v['height']-im.width/im.height)<.002)
test('no stray runtime discovery image is omitted from provenance',set(files)==set((ROOT/'src/assets/discovery').glob('*.webp')))
total=sum(p.stat().st_size for p in files);test('all fifteen responsive images stay below one MiB combined',total<1024*1024)
module=(ROOT/'src/data/discoveryPhotography.js').read_text();test('real runtime module references local variants and never temporary/CDN image URLs',all(v['file'] in module for p in m['images'] for v in p['variants']) and 'src/assets/discovery/' in module and 'images.unsplash.com' not in module and '/tmp/' not in module)
(DOC/'checks.json').write_text(json.dumps({'passed':True,'checks':checks,'sourcePhotos':5,'responsiveWebPFiles':15,'runtimeBytes':total,'newCatalogProductImages':0},ensure_ascii=False,indent=2)+'\n')
print(len(checks),'actual photo source/asset checks passed.')
