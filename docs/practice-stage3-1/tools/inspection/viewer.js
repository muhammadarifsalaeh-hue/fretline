import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { buildStudyGuitar } from '../buildStudyGuitar.mjs';

const stage = document.querySelector('#stage'), state = document.querySelector('#state');
const buttons = [...document.querySelectorAll('button')];
const params = new URL(location.href).searchParams;
let renderer, frame = 0;
try { renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'low-power' }); }
catch (error) { state.textContent = `WebGL unavailable: ${error.message}`; window.inspectionError = error.message; throw error; }
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = .9;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.domElement.tabIndex = 0; renderer.domElement.setAttribute('aria-label', 'Actual 3D C Major hand candidate');
renderer.domElement.setAttribute('aria-describedby', 'camera-help'); stage.append(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color('#111317');
const camera = new THREE.PerspectiveCamera(38, 1, .03, 100);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = false; controls.enablePan = false; controls.minDistance = 1.5; controls.maxDistance = 35;
controls.rotateSpeed = .65; controls.zoomSpeed = .7;
const pmrem = new THREE.PMREMGenerator(renderer), room = new RoomEnvironment();
const environment = pmrem.fromScene(room, .04); scene.environment = environment.texture; scene.environmentIntensity = .35;
room.dispose(); pmrem.dispose();
scene.add(new THREE.HemisphereLight('#f7f0e6', '#292b2f', .3));
const key = new THREE.DirectionalLight('#fff4e4', 1.1); key.position.set(-2, 7, 5); key.castShadow = true;
key.shadow.mapSize.set(1024, 1024); Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7 });
key.shadow.normalBias = .006; scene.add(key);
const fill = new THREE.DirectionalLight('#dde6ee', .5); fill.position.set(4, -3, -5); scene.add(fill);
const root = new THREE.Group(); root.scale.setScalar(1 / 40); scene.add(root);
const views = {
  front: { direction: [0, 1, .002], up: [0, 0, 1], label: 'Front · camera +Y · low E (+Z) up · headstock to observer’s right' },
  side: { direction: [.05, .08, 1], up: [0, 1, 0], label: 'Side profile · camera low-E side (+Z) · board outward +Y' },
  back: { direction: [.002, -1, .002], up: [0, 0, 1], label: 'Behind neck · camera −Y · low E (+Z) up · headstock left' },
  player: { direction: [.2, -.55, 1], up: [0, 0, 1], label: 'Player · behind board (−Y), above low-E edge (+Z) · +Z up' },
};
let activeView = 'front', focus = new THREE.Box3(new THREE.Vector3(0, -3, -.9), new THREE.Vector3(3, 1, .9));
let ready = false;
const render = () => {
  frame = 0; scene.updateMatrixWorld(true); renderer.render(scene, camera);
  window.inspectionCamera = { view: activeView, position: camera.position.toArray(), target: controls.target.toArray(), up: camera.up.toArray(), aspect: camera.aspect, distance: camera.position.distanceTo(controls.target) };
  window.inspectionProjection = () => corners(focus).map(point => point.project(camera).toArray());
};
const invalidate = () => { if (!frame) frame = requestAnimationFrame(render); };
controls.addEventListener('change', invalidate);
const corners = box => Array.from({ length: 8 }, (_, i) => new THREE.Vector3(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z));
function frameView(name) {
  activeView = name;
  const view = views[name], direction = new THREE.Vector3(...view.direction).normalize(), center = focus.getCenter(new THREE.Vector3());
  camera.up.fromArray(view.up);
  const right = new THREE.Vector3().crossVectors(new THREE.Vector3().copy(direction).negate(), camera.up).normalize();
  const up = new THREE.Vector3().crossVectors(direction, right).normalize();
  const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)), tanH = tanV * camera.aspect;
  let distance = 2;
  for (const corner of corners(focus)) {
    const delta = corner.sub(center), depth = delta.dot(direction);
    distance = Math.max(distance, Math.abs(delta.dot(right)) / tanH + depth, Math.abs(delta.dot(up)) / tanV + depth);
  }
  distance *= 1.18;
  controls.target.copy(center); camera.position.copy(center).addScaledVector(direction, distance);
  controls.update();
  for (const button of document.querySelectorAll('[data-view]')) button.setAttribute('aria-pressed', String(button.dataset.view === name));
  document.querySelector('#view-direction').textContent = view.label;
  window.inspectionView = name; render();
}
for (const button of document.querySelectorAll('[data-view]')) button.addEventListener('click', () => frameView(button.dataset.view));
document.querySelector('#reset').addEventListener('click', () => frameView(activeView));
const resize = () => {
  const { width, height } = stage.getBoundingClientRect(); camera.aspect = width / height; camera.updateProjectionMatrix(); renderer.setSize(width, height, false);
  frameView(activeView);
};
new ResizeObserver(resize).observe(stage); resize();
renderer.domElement.addEventListener('keydown', event => {
  if (!ready || event.ctrlKey || event.metaKey || event.altKey) return;
  if (event.key === 'Home' || event.key === '0') { event.preventDefault(); frameView(activeView); return; }
  const offset = camera.position.clone().sub(controls.target), spherical = new THREE.Spherical().setFromVector3(offset);
  const actions = { ArrowLeft: () => { spherical.theta -= .12; }, ArrowRight: () => { spherical.theta += .12; }, ArrowUp: () => { spherical.phi -= .1; }, ArrowDown: () => { spherical.phi += .1; }, '+': () => { spherical.radius *= .85; }, '=': () => { spherical.radius *= .85; }, '-': () => { spherical.radius *= 1.18; } };
  if (!actions[event.key]) return; event.preventDefault(); actions[event.key](); spherical.phi = THREE.MathUtils.clamp(spherical.phi, .05, Math.PI - .05); spherical.radius = THREE.MathUtils.clamp(spherical.radius, controls.minDistance, controls.maxDistance);
  camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); controls.update(); invalidate();
});
const fetchJSON = async url => { const response = await fetch(url); if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`); return response.json(); };
const hash = async buffer => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', buffer)), n => n.toString(16).padStart(2, '0')).join('');

try {
  const configPath = params.get('config');
  if (!configPath) throw new Error('Supply ?config=../path/to/candidate-config.json. No old candidate is selected automatically.');
  const configURL = new URL(configPath, location.href), config = await fetchJSON(configURL);
  if (!config.modelUrl) throw new Error('Candidate config must name modelUrl explicitly.');
  const modelURL = new URL(config.modelUrl, configURL), poseURL = config.poseUrl ? new URL(config.poseUrl, configURL) : null;
  const pose = poseURL ? await fetchJSON(poseURL) : null;
  state.textContent = 'Loading the specified anatomical GLB…';
  const response = await fetch(modelURL); if (!response.ok) throw new Error(`Model HTTP ${response.status}`);
  const binary = await response.arrayBuffer(), modelSha256 = await hash(binary);
  if (config.modelSha256 && config.modelSha256 !== modelSha256) throw new Error('GLB SHA256 does not match the candidate configuration.');
  const gltf = await new GLTFLoader().parseAsync(binary, new URL('.', modelURL).href);
  const neck = buildStudyGuitar({ textures: true, pressOffsetsMm: config.pressOffsetsMm ?? pose?.pressOffsetsMm ?? [4, 4, 4], stringPathsMm: config.stringPathsMm ?? pose?.stringPathsMm }); root.add(neck.group);
  let joints = 0, skinned = 0, triangles = 0;
  gltf.scene.traverse(object => {
    if (object.isBone && config.applyJointPose !== false && pose?.jointLocals?.[object.name]) { object.matrix.fromArray(pose.jointLocals[object.name]); object.matrixAutoUpdate = false; joints++; }
    if (!object.isMesh) return;
    if (object.isSkinnedMesh) skinned++;
    object.castShadow = true; object.receiveShadow = true; triangles += (object.geometry.index?.count ?? object.geometry.attributes.position.count) / 3;
    if (config.grayscaleNormalIsHeight) for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
      if (material.normalMap) { material.bumpMap = material.normalMap; material.normalMap = null; material.bumpScale = config.bumpScale ?? .0009; material.needsUpdate = true; }
    }
  });
  const transform = new THREE.Group(); transform.name = 'candidate-mm-from-gltf';
  const mmFromGLTF = config.mmFromGLTF ?? pose?.mmFromGLTF;
  if (!mmFromGLTF || mmFromGLTF.length !== 16) throw new Error('Config or pose must supply the explicit column-major mmFromGLTF matrix.');
  transform.matrix.fromArray(mmFromGLTF); transform.matrixAutoUpdate = false; transform.add(gltf.scene); root.add(transform); scene.updateMatrixWorld(true);
  const boneProof = {}, vertexProof = {}, meshBounds = new THREE.Box3();
  gltf.scene.traverse(object => {
    if (object.isBone) boneProof[object.name] = object.getWorldPosition(new THREE.Vector3()).multiplyScalar(40).toArray();
    if (object.isSkinnedMesh) object.skeleton.update();
    if (!object.isMesh) return;
    vertexProof[object.name] = [];
    for (let index = 0; index < object.geometry.attributes.position.count; index++) {
      const point = object.getVertexPosition(index, new THREE.Vector3()).applyMatrix4(object.matrixWorld);
      meshBounds.expandByPoint(point); vertexProof[object.name].push(point.multiplyScalar(40).toArray());
    }
  });
  focus = meshBounds.clone().union(new THREE.Box3(new THREE.Vector3(0, -.6, -.6), new THREE.Vector3(3, .1, .6)));
  window.inspectionVertices = vertexProof;
  window.inspectionProof = { actual3D: true, poseApproved: false, status: 'Unvalidated candidate; requires independent contact gate', configUrl: configURL.href, modelUrl: modelURL.href, poseUrl: poseURL?.href ?? null, modelSha256, poseSource: pose?.poseSource ?? config.poseSource ?? null, modifications: config.modifications ?? [], jointsApplied: joints, skinnedMeshes: skinned, handTriangles: triangles, neck: neck.metadata, handBoundsWorld: { min: meshBounds.min.toArray(), max: meshBounds.max.toArray() }, focusBoundsWorld: { min: focus.min.toArray(), max: focus.max.toArray() }, worldMmBonePositions: boneProof };
  document.querySelector('#proof').textContent = JSON.stringify(window.inspectionProof, null, 2);
  state.textContent = `C Major · ${config.label ?? 'research candidate'} · NOT APPROVED`;
  ready = true; buttons.forEach(button => { button.disabled = false; }); frameView(activeView); window.inspectionReady = true;
} catch (error) { state.textContent = `Inspection unavailable: ${error.message}`; window.inspectionError = error.message; console.error(error); }
