// Isolated, explicit UI/service contract fixture. Never imported by the app/build.
import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import '../../src/styles/tokens.css';
import '../../src/index.css';
import '../../src/styles/admin-studio.css';
import AdminEditor from '../../src/features/admin/AdminEditor';
import ProductImage from '../../src/components/guitar/ProductImage';
import CatalogCard from '../../src/components/catalog/CatalogCard';
import { ShopProvider } from '../../src/context/ShopContext';
import { GUITARS } from '../../src/data/guitars';
import { HOME_CATEGORY_ASSETS } from '../../src/data/homeCategoryAssets';
import { seedRecord } from '../../src/features/admin/product';
import { resolveRecord } from '../../src/features/admin/publicCatalog';

const base=seedRecord(GUITARS.find(g=>g.id==='yamaha-fg800'));
const initial={...base,id:'qa-image-upload',slug:'qa-image-upload',name:'ทดสอบภาพ FG800 เท่านั้น',gallery:[]};
const state={row:{id:initial.id,draft:structuredClone(initial),published:structuredClone(initial),status:'published',revision:1},uploads:[],calls:[],removed:[],registry:[],blobs:new Map(),failRegistrationOnce:false};
window.__imageFixture=state;
const client={
 from(table){const chain={select(){return chain;},eq(){return chain;},order(){return chain;},limit(){return chain;},then(resolve){return Promise.resolve({data:table==='guitar_images'?state.registry:[],error:null}).then(resolve);}};return chain;},
 storage:{from(bucket){if(bucket!=='guitar-images')throw Error('Wrong fixture bucket');return{
  async upload(path,blob,options){state.uploads.push({path,blob,options});state.blobs.set(path,URL.createObjectURL(blob));return{error:null};},
  async createSignedUrls(paths){return{data:paths.map(path=>({path,signedUrl:state.blobs.get(path)})),error:null};},
  async remove(paths){for(const path of paths){URL.revokeObjectURL(state.blobs.get(path));state.blobs.delete(path);state.removed.push(path);}return{error:null};},
 };}},
 async rpc(name,args){state.calls.push({name,args:structuredClone(args)});
  if(name==='admin_register_image'){
   if(state.failRegistrationOnce){state.failRegistrationOnce=false;return{error:new Error('Fixture registration failure')};}
   const data={id:crypto.randomUUID(),guitar_id:args.p_id,storage_path:args.p_path,metadata:args.p_metadata};state.registry.push(data);return{data,error:null};
  }
  if(args.p_expected_revision!==state.row.revision)throw Error('Fixture revision conflict');
  if(name==='admin_save_guitar')state.row={...state.row,draft:structuredClone(args.p_data),revision:state.row.revision+1};
  else if(name==='admin_set_publication')state.row={...state.row,published:structuredClone(state.row.draft),status:'published',revision:state.row.revision+1};
  else throw Error('Unexpected fixture RPC');
  return{data:structuredClone(state.row),error:null};
 },
};
function Harness(){
 const [row,setRow]=useState(state.row);
 const published=resolveRecord(row.published,new Map(state.blobs));
 return <ShopProvider><main style={{maxWidth:1100,margin:'auto',padding:20}}>
  <h1>ทดสอบส่วนแสดงภาพเท่านั้น</h1><p>ใช้ข้อมูลสำเนาและ service fixture ในหน่วยความจำ ไม่เชื่อม Auth, Storage หรือฐานข้อมูลจริง</p>
  <section className="admin-studio"><AdminEditor client={client} row={row} brands={[{id:'yamaha',name:'Yamaha'}]} onBack={()=>{}} onSaved={setRow}/></section>
  <section className="qa-published" style={{maxWidth:320}}><h2>ผล Published ในชุดทดสอบ</h2><CatalogCard guitar={published}/></section>
  <section className="qa-types" style={{display:'grid',gridTemplateColumns:'repeat(2,minmax(0,1fr))',gap:20}}>
   {Object.entries(HOME_CATEGORY_ASSETS).map(([type,image])=><div key={type} data-test-type={type}><h2>{type}</h2><ProductImage src={image.src} width={image.width} height={image.height} alt={`ภาพหมวด ${type} สำหรับทดสอบ component ไม่ใช่ภาพสินค้ารุ่นใด`} priority/></div>)}
  </section>
 </main></ShopProvider>;
}
const root=createRoot(document.getElementById('root'));
state.unmount=()=>root.unmount();
root.render(<React.StrictMode><BrowserRouter><Harness/></BrowserRouter></React.StrictMode>);
