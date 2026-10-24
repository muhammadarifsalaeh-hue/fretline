import fs from 'node:fs';
import * as THREE from '/workspace/fretline/node_modules/three/build/three.module.js';
import { buildStudyGuitar } from '/tmp/fretline-stage31-assets/buildStudyGuitar.mjs';
const pose=JSON.parse(fs.readFileSync(process.argv[2]));
const model=buildStudyGuitar({textures:false,stringPathsMm:pose.stringPathsMm,pressOffsetsMm:pose.pressOffsetsBeforeWireMM??pose.pressOffsetsMm??[4,4,4]});
model.group.updateMatrixWorld(true);
const meshes=[];
model.group.traverse(o=>{
 if(!o.isMesh||!['d-section-neck-back','curved-fingerboard','grooved-nut','headstock-solid'].includes(o.name)&&!/^fret-\d+$/.test(o.name)&&!/^string-[1-6]$/.test(o.name))return;
 const p=o.geometry.attributes.position,vector=new THREE.Vector3(),vertices=[];
 for(let i=0;i<p.count;i++){vector.fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);vertices.push(vector.toArray());}
 const indices=o.geometry.index?Array.from(o.geometry.index.array):Array.from({length:p.count},(_,i)=>i),triangles=[];
 for(let i=0;i<indices.length;i+=3)triangles.push(indices.slice(i,i+3));
 meshes.push({name:o.name,vertices,triangles,role:/^string-/.test(o.name)?'string':/^fret-/.test(o.name)?'fret':'solid',controlPointsMm:o.userData.controlPointsMm});
});
const result={coordinateFrame:'mm, nutx0, +X towardbody,+Y outward, lowE+Z',posePath:process.argv[2],metadata:model.metadata,meshes};
fs.writeFileSync(process.argv[3],JSON.stringify(result));
console.log(meshes.map(m=>[m.name,m.triangles.length]));
