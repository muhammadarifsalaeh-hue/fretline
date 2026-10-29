export const TYPES = [['electric','กีตาร์ไฟฟ้า'],['acoustic','กีตาร์โปร่ง'],['classical','กีตาร์คลาสสิก'],['bass','เบส']];
export const SPEC_GROUPS = [
  ['ข้อมูลทั่วไป', [['bodyShape','ทรงบอดี้'],['strings','จำนวนสาย','number'],['orientation','การวางมือ']]],
  ['บอดี้และวัสดุ', [['body','ไม้บอดี้'],['top','ไม้หน้า'],['back','ไม้หลัง'],['sides','ไม้ข้าง'],['bodyConstruction','โครงสร้างบอดี้'],['bodyFinish','สีและการเคลือบ']]],
  ['คอและฟิงเกอร์บอร์ด', [['neck','ไม้คอ'],['fretboard','ไม้ฟิงเกอร์บอร์ด'],['neckProfile','ทรงคอ'],['scale','สเกล (นิ้ว)','number'],['scaleMm','สเกล (มม.)','number'],['frets','จำนวนเฟรต','number'],['nutWidthMm','ความกว้างนัท (มม.)','number'],['fingerboardRadiusMm','รัศมีฟิงเกอร์บอร์ด (มม.)','number']]],
  ['ฮาร์ดแวร์และอิเล็กทรอนิกส์', [['pickupConfiguration','รูปแบบปิ๊กอัป'],['pickups','รุ่นปิ๊กอัป'],['electronics','ระบบอิเล็กทรอนิกส์'],['controls','ชุดควบคุม'],['bridge','บริดจ์'],['tuners','ลูกบิด']]],
  ['ข้อมูลเพิ่มเติม', [['colorOptions','สีที่มี'],['countryOfManufacture','ประเทศผู้ผลิต'],['weightKg','น้ำหนัก (กก.)','number']]],
];
export const validSource = (source) => /^https?:\/\/[^ /]+/.test(source?.url ?? '') && /^\d{4}-\d{2}-\d{2}$/.test(source?.verifiedOn ?? '') && Number.isFinite(Date.parse(source.verifiedOn));
export function prepareDraft(data) {
  const d = structuredClone(data);
  d.slug = d.id;
  d.price = d.price === '' || d.price == null ? null : Number(d.price);
  d.oldPrice = null;
  for (const [,fields] of SPEC_GROUPS) for (const [key,,type] of fields) {
    const value = d.specs[key];
    d.specs[key] = value == null || String(value).trim() === '' ? null : type === 'number' ? Number(value) : String(value).trim();
  }
  if (d.price == null) d.priceSource = null;
  else d.priceSource = { ...d.priceSource, currency: 'THB', kind: d.priceSource?.kind ?? 'retailer-listed', stockStatus: 'unknown' };
  if (validSource(d.source)) {
    d.source.fields = [...new Set([...(d.source.fields ?? []), ...Object.entries(d.specs).filter(([,v]) => v != null).map(([key]) => `specs.${key}`), ...(d.description ? ['description'] : []), ...(d.price != null ? ['price'] : [])])];
    d.dataStatus = 'partial';
  }
  d.gallery = d.gallery ?? [];
  d.colors = d.colors ?? []; d.tags = d.tags ?? [];
  d.keywords = [d.id,d.brand,d.name,d.keywords ?? ''].join(' ').slice(0,6000);
  return d;
}
export function validateDraft(d, publish = false) {
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(d.id ?? '') || d.id.length < 3 || d.id.length>120 || ['constructor','prototype','__proto__'].includes(d.id)) return 'ID ใช้ตัวอักษรอังกฤษพิมพ์เล็ก ตัวเลข และขีดกลาง 3–120 ตัว';
  if (!d.brand || !TYPES.some(([id])=>id===d.category)) return 'กรุณาเลือกแบรนด์และประเภท';
  if (d.price != null && (!Number.isFinite(d.price) || d.price<=0 || d.price>9999999999 || Math.round(d.price*100)/100!==d.price)) return 'ราคาต้องมากกว่า 0 หรือเว้นว่างเพื่อแสดงสอบถามราคา';
  if (d.price != null && !validSource(d.priceSource)) return 'กรุณาระบุแหล่งราคาและวันที่ตรวจสอบ';
  for (const [,fields] of SPEC_GROUPS) for (const [key,label,type] of fields) {
    const n=d.specs[key];
    if (type==='number' && n!=null && (!Number.isFinite(n) || n<0 || n>10000 || (n===0 && key!=='frets') || (['strings','frets'].includes(key) && !Number.isInteger(n)))) return `${label} ไม่ถูกต้อง`;
  }
  if (publish && !d.name?.trim()) return 'กรุณาระบุชื่อรุ่นก่อนเผยแพร่';
  if (publish && (d.price!=null || Object.values(d.specs).some(v=>v!=null && v!=='')) && !validSource(d.source)) return 'กรุณาระบุแหล่งสเปกและวันที่ตรวจสอบก่อนเผยแพร่';
  for(const source of [d.source,d.priceSource].filter(validSource)) if (source.verifiedOn>new Date().toISOString().slice(0,10)) return 'วันที่ตรวจสอบต้องไม่อยู่ในอนาคต';
  return null;
}
export function blankGuitar(brand = '') {
  return { id:'', name:'', brand, category:'electric', description:'', descriptionEn:'', featured:false, price:null, priceSource:null, specs:{}, gallery:[], colors:[], tags:[], source:null, dataStatus:'partial' };
}
export function completeness(d) {
  const keys=['bodyShape','strings','body','neck','fretboard','frets','bridge'];
  if (['acoustic','classical'].includes(d.category)) keys.push('top','back','sides');
  else keys.push('pickups','electronics');
  const missing=keys.filter(k=>d.specs?.[k]==null || d.specs[k]==='');
  if (!(d.specs?.scale || d.specs?.scaleMm)) missing.push('scale');
  return missing;
}
export function seedRecord(g) {
  const { image,hasPhotos,...data }=g;
  return { ...data, gallery:g.gallery.map(({src,srcSet,...im},index)=>({...im,legacyIndex:index})) };
}
