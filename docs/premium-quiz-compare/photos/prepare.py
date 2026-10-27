"""Create local WebP derivatives of five separately verified editorial photographs.

Inputs are downloaded Unsplash image variants in /tmp/fretline-photo-research,
not invented catalog product photographs. Source photos preserve their frame.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import hashlib,json,shutil,datetime
ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path('/tmp/fretline-photo-research')
OUT=ROOT/'src/assets/discovery';OUT.mkdir(exist_ok=True)
DOC=ROOT/'docs/premium-quiz-compare/photos';(DOC/'originals').mkdir(exist_ok=True)
PHOTOS=[
 {'id':'quizHero','slug':'quiz-studio','input':'quiz-studio.jpg','imageId':'1511379938547-c1f69419868d','photoId':'MEL-jJnm7RQ','author':'Wes Hicks','sourceUrl':'https://unsplash.com/photos/several-guitars-beside-of-side-table-MEL-jJnm7RQ','altTh':'กีตาร์ไฟฟ้าและกีตาร์โปร่งวางในห้องดนตรีข้างหน้าต่าง','altEn':'Electric and acoustic guitars in a naturally lit music room','objectPosition':'72% 53%','description':'Real music-room photograph with electric and acoustic instruments. The room is naturally lit, not the artificially lit studio in the supplied design reference.'},
 {'id':'compareHero','slug':'compare-guitars','input':'compare-window-shop.jpg','imageId':'1773093219310-711be04f4fa2','photoId':'YRY0Eo6Yq4s','author':'Masha','sourceUrl':'https://unsplash.com/photos/guitars-displayed-in-a-store-window-YRY0Eo6Yq4s','altTh':'กีตาร์ไฟฟ้าหลายรูปทรงเรียงอยู่ในหน้าร้านดนตรี','altEn':'A variety of electric guitar shapes displayed in a music shop window','objectPosition':'65% 52%','description':'Real shop-window photograph with several distinct electric-guitar shapes. It is not an invented three-guitar studio scene and does not depict the selected comparison models.'},
 {'id':'electricPlayer','slug':'electric-player','input':'electric-player.jpg','imageId':'1686895052735-37336c0d5235','photoId':'gO3BhocajAY','author':'Mila Vasileva','sourceUrl':'https://unsplash.com/photos/a-close-up-of-a-person-playing-an-electric-guitar-gO3BhocajAY','altTh':'มือของผู้เล่นกำลังดีดสายกีตาร์ไฟฟ้า','altEn':'A musician picking the strings of an electric guitar','objectPosition':'50% 50%','description':'Generic editorial playing photograph, not a product illustration or an endorsement.'},
 {'id':'acousticPlayer','slug':'acoustic-player','input':'acoustic-player.jpg','imageId':'1771254240340-ae73c5a378ff','photoId':'fPiy383YBEM','author':'Alexander Mass','sourceUrl':'https://unsplash.com/photos/person-playing-an-acoustic-guitar-indoors-fPiy383YBEM','altTh':'ผู้เล่นกำลังฝึกกีตาร์โปร่งในห้องด้วยแสงอบอุ่น','altEn':'An acoustic guitarist practicing indoors in warm light','objectPosition':'50% 50%','description':'Generic editorial acoustic-playing photograph, not the catalog guitar selected by the recommendation engine.'},
 {'id':'chordHands','slug':'chord-hands','input':'chord-hands.jpg','imageId':'1741229395001-6d8d2a97f05e','photoId':'2KzBcgEMOgM','author':'Alex Kolundzija','sourceUrl':'https://unsplash.com/photos/a-hand-plays-guitar-close-up-2KzBcgEMOgM','altTh':'ภาพระยะใกล้ของมือที่กำลังจับสายบนคอกีตาร์','altEn':'Close-up of a fretting hand on a guitar neck','objectPosition':'48% 50%','description':'Atmospheric fretting-hand photograph, not a certified chord diagram or an example of the Practice hand solver.'},
]
def sha(data):return hashlib.sha256(data).hexdigest()
previous={p['id']:p for p in json.loads((DOC/'manifest.json').read_text())['images']} if (DOC/'manifest.json').exists() else {}
proof=SOURCE/'source-web-read.json'
if proof.exists():
 webread=proof.read_bytes();web=json.loads(webread);text='\n'.join(x.get('text','') for x in web['content']);assert text.count('Free to use under')==5 and 'Internal Error' not in text;webread_hash=sha(webread)
else:
 assert len(previous)==5,'Retain the manifest and original source files before regeneration.'
 webread_hash=next(iter(previous.values()))['rightsEvidence']['webToolResponseSha256']
manifest=[]
for photo in PHOTOS:
 source=SOURCE/photo['input'] if (SOURCE/photo['input']).exists() else DOC/'originals'/photo['input'];data=source.read_bytes();im=ImageOps.exif_transpose(Image.open(source)).convert('RGB')
 assert im.size==(1800,1200),[photo['id'],im.size]
 if source.resolve()!=(DOC/'originals'/photo['input']).resolve():shutil.copyfile(source,DOC/'originals'/photo['input'])
 variants=[]
 for width in ([480,960,1600] if photo['id'].endswith('Hero') else [360,480,720]):
  height=round(im.height*width/im.width);resized=im.resize((width,height),Image.Resampling.LANCZOS);file=f"{photo['slug']}-{width}.webp";path=OUT/file;resized.save(path,'WEBP',quality=84,method=6)
  variants.append({'file':file,'width':width,'height':height,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())})
 record={**photo,'license':'Unsplash License','licenseUrl':'https://unsplash.com/license','credit':f"{photo['author']} / Unsplash",'checkedOn':'2026-10-26','kind':'editorial-photograph','selectedProductEvidence':False,'endorsementImplied':False,'sourceDownload':{'url':f"https://images.unsplash.com/photo-{photo['imageId']}?auto=format&fit=max&w=1800&q=90",'httpStatus':200,'downloadedAt':previous.get(photo['id'],{}).get('sourceDownload',{}).get('downloadedAt',datetime.datetime.fromtimestamp(source.stat().st_mtime,datetime.timezone.utc).isoformat()),'format':'JPEG','width':im.width,'height':im.height,'bytes':len(data),'sha256':sha(data),'fullResolutionMasterDownloaded':False,'localFile':'originals/'+photo['input']},'rightsEvidence':{'method':'publisher-photo-page-and-license-page-web-read','assertion':'Free to use under the Unsplash License','photoPageUrl':photo['sourceUrl'],'licensePageUrl':'https://unsplash.com/license','webToolResponseSha256':webread_hash,'executorDirectPhotoPageHTTP':401 if photo['id']=='quizHero' else None,'note':'Publisher photo pages and license were successfully read with the web tool. Direct executor requests to the sample photo page and license page returned 401; the other photo-page executor fetches were not attempted. None is represented as HTTP200 rights evidence. Actual images downloaded via the publisher CDN returned HTTP200.'},'changes':'Downloaded 1800px source variant; EXIF orientation applied; metadata stripped; resized proportionally and encoded WebP. No crop, recoloring, retouching, compositing or image generation. Responsive page framing may use CSS cover/gradient overlays.','variants':variants}
 manifest.append(record)
(DOC/'manifest.json').write_text(json.dumps({'schemaVersion':1,'checkedOn':'2026-10-26','sourcePhotos':5,'localWebPDerivatives':15,'images':manifest},ensure_ascii=False,indent=2)+'\n')
(DOC/'license-evidence.json').write_text(json.dumps({'source':'https://unsplash.com/license','method':'publisher-page-web-read','checkedOn':'2026-10-26','webToolResponseSha256':webread_hash,'licenseName':'Unsplash License','shortExcerpt':'All images can be downloaded and used for free','interpretation':'The displayed license permits downloading and use, including commercial use, and modification. It excludes selling unmodified copies and replicating a competing image service. These files illustrate Fretline pages, not an image redistribution service. No model/brand endorsement is implied.','attribution':'Not required by this license, but retained visibly in the Fretline image credits.','sourcePhotoPages':{p['id']:p['sourceUrl'] for p in PHOTOS}},ensure_ascii=False,indent=2)+'\n')
records=[]
for m in manifest:
 records.append({k:m[k] for k in ['id','slug','author','sourceUrl','license','licenseUrl','credit','altTh','altEn','objectPosition'] }|{'variants':m['variants']})
module="""// Licensed generic editorial photographs only. Never selected-product or finish evidence.
// Sources, license observation, source/derivative hashes: docs/premium-quiz-compare/photos/.
import { LANG } from '@/i18n';
const files = import.meta.glob('/src/assets/discovery/*.webp', { eager: true, query: '?url', import: 'default' });
const records = """+json.dumps(records,ensure_ascii=False,indent=2)+""";
const url = (file) => files[`/src/assets/discovery/${file}`];
export const DISCOVERY_PHOTOGRAPHY = Object.fromEntries(records.map((record) => {
  const largest = record.variants[record.variants.length - 1];
  return [record.id, {
    ...record,
    src: url(largest.file), srcSet: record.variants.map((image) => `${url(image.file)} ${image.width}w`).join(', '),
    width: largest.width, height: largest.height,
    alt: LANG === 'en' ? record.altEn : record.altTh,
    sizes: record.id.endsWith('Hero') ? '(min-width: 1024px) 70vw, 100vw' : '(min-width: 1024px) 18vw, 33vw',
    kind: 'editorial-photograph', productEvidence: false,
  }];
}));
export const DISCOVERY_PHOTO_CREDITS = Object.values(DISCOVERY_PHOTOGRAPHY);
"""
(ROOT/'src/data/discoveryPhotography.js').write_text(module)
canvas=Image.new('RGB',(1250,800),(10,10,10));draw=ImageDraw.Draw(canvas)
for i,m in enumerate(manifest):
 im=Image.open(OUT/m['variants'][-1]['file']);im.thumbnail((400,320));x=(i%3)*415;y=(i//3)*400;canvas.paste(im,(x,y));draw.text((x,y+330),m['id']+' / '+m['author'],fill='white')
canvas.save(DOC/'contact-sheet.jpg',quality=88)
print('Prepared',len(manifest),'real photographs and',sum(len(m['variants']) for m in manifest),'WebP files;',sum(v['bytes'] for m in manifest for v in m['variants']),'total runtime bytes')
