import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { buildStudyGuitar } from '../buildStudyGuitar.mjs';
const stage=document.querySelector('#stage'), status=document.querySelector('#state');
let renderer;
try { renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'}); }
catch(error){status.textContent='WebGL unavailable: '+error.message;throw error;}
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;stage.append(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#111317');
const camera=new THREE.PerspectiveCamera(38,1,.05,100);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=2;controls.maxDistance=25;controls.enablePan=true;
const pmrem=new THREE.PMREMGenerator(renderer), environment=pmrem.fromScene(new RoomEnvironment(),.04);scene.environment=environment.texture;scene.environmentIntensity=.45;pmrem.dispose();
scene.add(new THREE.HemisphereLight('#fcf4e6','#27292e',.35));
const key=new THREE.DirectionalLight('#fff0d5',1.4);key.position.set(-2,7,5);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-7;key.shadow.camera.right=7;key.shadow.camera.top=7;key.shadow.camera.bottom=-7;key.shadow.normalBias=.015;scene.add(key);
const rim=new THREE.DirectionalLight('#d3e4ff',.6);rim.position.set(5,-2,-5);scene.add(rim);
const root=new THREE.Group();root.scale.setScalar(1/40);scene.add(root);
const render=()=>{scene.updateMatrixWorld(true);renderer.render(scene,camera);window.inspectionCamera={position:camera.position.toArray(),target:controls.target.toArray()};};controls.addEventListener('change',render);
function resize(){const rect=stage.getBoundingClientRect();renderer.setSize(rect.width,rect.height);camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();render();}new ResizeObserver(resize).observe(stage);
const poses={front:{position:[1.8,5.3,3.8],target:[1.8,-.85,-.1]},side:{position:[6.8,.6,4.8],target:[1.8,-.85,-.15]},player:{position:[2.8,4.0,-5.8],target:[1.8,-.85,-.1]},context:{position:[7,10,12],target:[1.2,-.5,0]}};
let activeView='front';function setView(name){activeView=name;const pose=poses[name];camera.position.fromArray(pose.position);controls.target.fromArray(pose.target);controls.update();for(const b of document.querySelectorAll('[data-view]'))b.setAttribute('aria-pressed',String(b.dataset.view===name));render();window.inspectionView=name;}
for(const b of document.querySelectorAll('[data-view]'))b.addEventListener('click',()=>setView(b.dataset.view));document.querySelector('#reset').addEventListener('click',()=>setView(activeView));setView('front');resize();
try{
const pose=await fetch('../c-major-runtime-pose.json').then(r=>{if(!r.ok)throw new Error('Pose HTTP'+r.status);return r.json();});
const neck=buildStudyGuitar({textures:true,pressOffsetsMm:pose.pressOffsetsMm});root.add(neck.group);
const gltf=await new GLTFLoader().loadAsync('../anatomical-hand-optimized.glb');
let joints=0,skinned=0,triangles=0;
gltf.scene.traverse(o=>{
 if(o.isBone&&pose.jointLocals[o.name]){o.matrix.fromArray(pose.jointLocals[o.name]);o.matrixAutoUpdate=false;joints++;}
 if(o.isSkinnedMesh){skinned++;o.castShadow=true;o.receiveShadow=true;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;const mats=Array.isArray(o.material)?o.material:[o.material];for(const mat of mats){if(mat.normalMap){mat.bumpMap=mat.normalMap;mat.normalMap=null;mat.bumpScale=.0009;mat.needsUpdate=true;}}}
});
const transform=new THREE.Group();transform.name='left-hand-mm-from-gltf';transform.matrix.fromArray(pose.mmFromGLTF);transform.matrixAutoUpdate=false;transform.add(gltf.scene);root.add(transform);scene.updateMatrixWorld(true);
const boneProof={};gltf.scene.traverse(o=>{if(o.isBone){const v=o.getWorldPosition(new THREE.Vector3()).multiplyScalar(40);boneProof[o.name]=v.toArray();}if(o.isSkinnedMesh)o.skeleton.update();});
const vertexProof={}; gltf.scene.traverse(o=>{if(o.isSkinnedMesh){vertexProof[o.name]=[];for(let i=0;i<o.geometry.attributes.position.count;i++){const point=o.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(o.matrixWorld).multiplyScalar(40);vertexProof[o.name].push(point.toArray());}}});window.inspectionVertices=vertexProof;
const proof={actual3D:true,poseApproved:false,status:'failed contact gate',jointsApplied:joints,skinnedMeshes:skinned,handTriangles:triangles,neckTriangles:neck.metadata,modelSha256:pose.modelSha256,worldMmBonePositions:boneProof};window.inspectionProof=proof;window.inspectionReady=true;document.querySelector('#proof').textContent=JSON.stringify(proof,null,2);status.textContent='Research pose — contact gate FAILED';status.style.color='#edb3a0';render();
}catch(error){status.textContent='Asset inspection failed: '+error.message;console.error(error);window.inspectionError=error.message;}
