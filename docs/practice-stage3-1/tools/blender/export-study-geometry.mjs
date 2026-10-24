import fs from 'node:fs';
import { buildStudyGuitar } from '../buildStudyGuitar.mjs';
const pose=JSON.parse(fs.readFileSync(process.argv[2] || '/tmp/fretline-stage3-assets/c-major-runtime-pose.json'));
const { group }=buildStudyGuitar({textures:false,stringPathsMm:pose.stringPathsMm,pressOffsetsMm:pose.pressOffsetsMm??pose.pressOffsetsBeforeWireMM??[4,4,4]});
group.updateMatrixWorld(true);
const meshes=[];
group.traverse(o=>{
 if(!o.isMesh)return;
 const geometry=o.geometry.clone().applyMatrix4(o.matrixWorld),p=geometry.attributes.position;
 const m=o.material;
 meshes.push({name:o.name,positions:[...p.array],indices:geometry.index?[...geometry.index.array]:Array.from({length:p.count},(_,i)=>i),uv:geometry.attributes.uv?[...geometry.attributes.uv.array]:null,material:{name:m.name,color:m.color.toArray(),metalness:m.metalness,roughness:m.roughness}});
});
fs.writeFileSync('/tmp/fretline-stage31-assets/blender/study-guitar-meshes.json',JSON.stringify({units:'mm',poseStatus:'UNVALIDATED_C_MAJOR',meshes}));
console.log({meshes:meshes.length,triangles:meshes.reduce((s,m)=>s+m.indices.length/3,0)});
