import { GUITARS, GUITARS_BY_ID, SAVED_GUITARS_BY_ID } from '@/data/guitars';
import { getSupabase, remoteCatalogEnabled } from './config';
import { LANG } from '@/i18n';

const original = new Map(GUITARS.map(g=>[g.id,g]));
export function resolveRecord(data, signed = new Map()) {
  const base=original.get(data.id);
  const gallery=(data.gallery??[]).flatMap(im=>{
    if (im.legacyIndex != null) {
      const old=base?.gallery[im.legacyIndex];
      return old ? [{...old,label:im.label??old.label,alt:im.alt??old.alt}] : [];
    }
    const src=signed.get(im.storagePath);
    return src ? [{...im,src,label:im.label||'รูปสินค้า',kind:'photo'}] : [];
  });
  return {...data,description:LANG==='en'&&data.descriptionEn?data.descriptionEn:data.description??'',slug:data.id,gallery,image:gallery[0]?.src??null,hasPhotos:gallery.length>0,colors:data.colors??[],tags:data.tags??[],specs:data.specs??{}};
}
export async function signedImages(client, data) {
  const paths=[...new Set(data.flatMap(d=>(d.gallery??[]).map(im=>im.storagePath).filter(Boolean)))];
  if (!paths.length) return new Map();
  const {data:urls,error}=await client.storage.from('guitar-images').createSignedUrls(paths,86400);
  if (error || urls?.some(im=>im.error || !im.signedUrl)) throw new Error('โหลดภาพสินค้าไม่สำเร็จ กรุณาลองอีกครั้ง');
  return new Map(urls.map(im=>[im.path,im.signedUrl]));
}
export function installPublishedCatalog(rows, signed) {
  if (!Array.isArray(rows) || new Set(rows.map(g=>g.id)).size!==rows.length || rows.some(g=>!g.id || ['__proto__','constructor','prototype'].includes(g.id))) throw new Error('ข้อมูล Catalog ไม่ถูกต้อง');
  const mapped=rows.map(g=>resolveRecord(g,signed));
  for (const g of GUITARS) { delete GUITARS_BY_ID[g.id]; delete SAVED_GUITARS_BY_ID[g.id]; }
  GUITARS.splice(0,GUITARS.length,...mapped);
  for (const g of mapped) { GUITARS_BY_ID[g.id]=g; SAVED_GUITARS_BY_ID[g.id]=g; }
}
export async function hydratePublishedCatalog() {
  if (!remoteCatalogEnabled()) return;
  const client=await getSupabase();
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),20000);
  try {
    const {data,error}=await client.rpc('get_published_catalog').abortSignal(controller.signal);
    if (error || data?.ready!==true || !Array.isArray(data.guitars)) throw new Error('ยังโหลด Catalog ไม่สำเร็จ กรุณาลองอีกครั้ง');
    const images=await signedImages(client,data.guitars);
    installPublishedCatalog(data.guitars,images);
  } finally { clearTimeout(timer); }
}
