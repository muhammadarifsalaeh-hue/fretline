// Isolated authoring viewer; never imported by the public application or build.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import React from 'react';
import { createRoot } from 'react-dom/client';
import ChordDiagram from '/src/features/practice/components/ChordDiagram.jsx';
import { PRACTICE_CHORDS } from '/src/features/practice/data/chords.js';
import { buildStudyGuitar } from '/src/features/practice/scene/studyGuitar.js';
import { createFrettedStringController } from '/src/features/practice/scene/frettedStrings.js';
import { referenceCameraUp,fitPerspectiveDistance,CAMERA_DIRECTIONS } from '/src/features/practice/scene/cameraMath.js';
const host=document.querySelector('#stage'),scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,.03,100);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'});renderer.setPixelRatio(1.5);renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;host.append(renderer.domElement);
camera.up.copy(referenceCameraUp(CAMERA_DIRECTIONS.front,3));
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.enablePan=false;controls.minDistance=1;controls.maxDistance=30;
scene.add(new THREE.HemisphereLight('#f7e8ce','#34353b',.7));
for(const [color,power,position]of[['#ffe3bb',1.9,[-4,7,4]],['#d8e4f3',.65,[4,3,-5]],['#d6aa68',1,[-6,-2,-3]],['#ead9c3',1.2,[1,-6,3]]]){const light=new THREE.DirectionalLight(color,power);light.position.set(...position);scene.add(light)}
const room=new RoomEnvironment(),pmrem=new THREE.PMREMGenerator(renderer),environment=pmrem.fromScene(room,.04,.1,100,{size:64});scene.environment=environment.texture;scene.environmentIntensity=.45;room.dispose();pmrem.dispose();
const space=new THREE.Group();space.scale.setScalar(1/40);scene.add(space);const guitar=buildStudyGuitar();space.add(guitar.group);const strings=createFrettedStringController(guitar),hand=new THREE.Group();hand.scale.setScalar(1000);space.add(hand);
const buffer=await fetch('/src/features/practice/assets/makehuman-left-arm-sleeved.glb').then(r=>r.arrayBuffer());
const sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',buffer))].map(b=>b.toString(16).padStart(2,'0')).join('');
if(sha!=='23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc')throw Error('Unexpected original GLB');
const loaded=await new GLTFLoader().parseAsync(buffer,location.href);hand.add(loaded.scene);const bones=new Map(),rest=new Map();loaded.scene.traverse(o=>{if(o.isBone){const name=o.userData.name||o.name;bones.set(name,o);rest.set(name,{position:o.position.clone(),scale:o.scale.clone()})}if(o.isSkinnedMesh)o.frustumCulled=false});
const library=await fetch('/src/features/practice/assets/hand-poses.json').then(r=>r.json());const diagram=createRoot(document.querySelector('#diagram'));
function signature(){let hash=2166136261;const values=[...hand.position.toArray(),...hand.quaternion.toArray()];[...bones].sort(([a],[b])=>a.localeCompare(b)).forEach(([,b])=>values.push(...b.quaternion.toArray()));for(const word of new Uint32Array(new Float32Array(values).buffer))hash=Math.imul(hash^word,16777619)>>>0;return hash.toString(16).padStart(8,'0')}
let frame=0,active=null,pose=null,reviewBounds=null;
const render=()=>{frame=0;scene.updateMatrixWorld(true);loaded.scene.traverse(o=>{if(o.isSkinnedMesh)o.skeleton.update()});renderer.render(scene,camera)};
const invalidate=()=>{if(!frame)frame=requestAnimationFrame(render)};
controls.addEventListener('change',invalidate);
function view(name='front'){
 const direction=new THREE.Vector3(...CAMERA_DIRECTIONS[name]).normalize();
 const bounds=reviewBounds||new THREE.Box3(new THREE.Vector3(-10,-112,-70).multiplyScalar(1/40),new THREE.Vector3(150,32,40).multiplyScalar(1/40));const target=bounds.getCenter(new THREE.Vector3());
 controls.target.copy(target);camera.position.copy(target).addScaledVector(direction,fitPerspectiveDistance(camera,bounds,target,direction,1.08));controls.update();invalidate();window.inspect.view=name;
}
function choose(id,candidate){
 const chord=PRACTICE_CHORDS.find(c=>c.id===id);if(!chord)throw Error('Unknown chord');const next=candidate||library.poses[id];if(next.chordId!==id)throw Error('Wrong chord identity');
 hand.position.fromArray(next.root.positionMm);hand.quaternion.fromArray(next.root.quaternion).normalize();for(const [name,b]of bones){b.position.copy(rest.get(name).position);b.scale.copy(rest.get(name).scale);b.quaternion.fromArray(next.bones[name].quaternion).normalize()}
 strings.update(chord,true,next.pressOffsetsMm);pose=next;
 scene.updateMatrixWorld(true);reviewBounds=new THREE.Box3();const vertex=new THREE.Vector3();
 loaded.scene.traverse(o=>{if(!o.isSkinnedMesh)return;o.skeleton.update();const indices=o.geometry.attributes.skinIndex,weights=o.geometry.attributes.skinWeight;
  for(let i=0;i<indices.count;i++){let slot=0;for(let j=1;j<4;j++)if(weights.getComponent(i,j)>weights.getComponent(i,slot))slot=j;const bone=o.skeleton.bones[indices.getComponent(i,slot)];const name=bone?.userData.name||bone?.name||'';
   if(!name.startsWith('finger')&&!name.startsWith('metacarpal'))continue;o.getVertexPosition(i,vertex);o.localToWorld(vertex);reviewBounds.expandByPoint(vertex)}
 });
 const wrist=bones.get('wrist.L');if(wrist)reviewBounds.expandByPoint(wrist.getWorldPosition(vertex));reviewBounds.expandByScalar(.35);view(window.inspect.view||'front');active=chord;document.querySelector('#chord').textContent=id;document.querySelector('#voicing').textContent=chord.voicing;document.querySelector('#chords').value=id;
 document.querySelector('#spec').textContent=chord.frets.map((f,i)=>`สาย ${6-i}: ${f===null?'ไม่เล่น':f===0?'เปิด':`เฟรต ${f} / นิ้ว ${chord.fingers[i]}`}`).join('\n');diagram.render(React.createElement(ChordDiagram,{chord}));invalidate();return{chord:id,assetSHA256:sha,originalRestTranslations:true};
}
const select=document.querySelector('#chords');for(const c of PRACTICE_CHORDS){const o=document.createElement('option');o.value=c.id;o.textContent=c.id;select.append(o)}select.addEventListener('change',()=>choose(select.value));document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
window.inspect={choose,viewAngle:view,pose:()=>pose,chord:()=>active,modelSHA256:sha,camera:()=>({position:camera.position.toArray(),target:controls.target.toArray()}),signature,renderInfo:()=>({calls:renderer.info.render.calls,triangles:renderer.info.render.triangles})};
const resize=()=>{const b=host.getBoundingClientRect();renderer.setSize(b.width,b.height,false);camera.aspect=b.width/b.height;camera.updateProjectionMatrix();view(window.inspect.view||'front')};new ResizeObserver(resize).observe(host);resize();choose(new URL(location.href).searchParams.get('chord')||'C');document.body.dataset.ready='true';document.querySelector('#state').textContent='โมเดลต้นฉบับ · แขนเสื้อดำ';
