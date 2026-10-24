import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { FRET_COUNT, STRING_COUNT, getFretPosition } from '../data/fretboard';
import { buildStudyGuitar } from './studyGuitar';
import { CAMERA_DIRECTIONS, referenceCameraUp, fitPerspectiveDistance } from './cameraMath';

// Generic study geometry, never a catalog guitar or a validated anatomical pose.
// World scale: 40 mm/unit. Nut -> body is +X, board face +Y, low E +Z.
const UNIT = 40;
const NUT_X = -getFretPosition(FRET_COUNT) / UNIT / 2;
const xAt = (mm) => NUT_X + mm / UNIT;

function label(text, { gold = false, size = .24 } = {}) {
  const canvas = document.createElement('canvas');
  canvas.width = 128; canvas.height = 128;
  const ctx = canvas.getContext('2d');
  if (gold) {
    ctx.beginPath(); ctx.arc(64, 64, 54, 0, Math.PI * 2);
    ctx.fillStyle = '#e0c58c'; ctx.fill();
    ctx.lineWidth = 5; ctx.strokeStyle = '#9a7441'; ctx.stroke();
  }
  ctx.fillStyle = gold ? '#17130d' : '#ded6c2';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = `${gold ? 600 : 400} 68px sans-serif`;
  ctx.fillText(text, 64, 67);
  const map = new THREE.CanvasTexture(canvas);
  map.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map, depthTest: true, toneMapped: false }));
  sprite.scale.set(size, size, 1); sprite.renderOrder = 3;
  return sprite;
}

function disposeObject(root) {
  const materials = new Set(), textures = new Set();
  root.traverse((object) => {
    object.geometry?.dispose();
    const items = object.material ? (Array.isArray(object.material) ? object.material : [object.material]) : [];
    items.forEach((material) => materials.add(material));
  });
  materials.forEach((material) => {
    Object.values(material).forEach((value) => { if (value?.isTexture) textures.add(value); });
    material.dispose();
  });
  textures.forEach((texture) => texture.dispose());
  root.clear();
}

/** Real WebGL, rendered on demand. The model never changes when a camera moves. */
export function createNeckScene(host, { chord, canvasLabel, onError, onInteraction }) {
  const canvas = document.createElement('canvas');
  canvas.setAttribute('data-practice-canvas', '');
  canvas.setAttribute('aria-label', canvasLabel);
  canvas.setAttribute('aria-describedby', 'practice-camera-help'); canvas.tabIndex = 0;
  const context = canvas.getContext('webgl2', { alpha: true, antialias: true, powerPreference: 'low-power' });
  if (!context) throw new Error('WEBGL_UNAVAILABLE');
  const renderer = new THREE.WebGLRenderer({ canvas, context, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight('#f7e8ce', '#34353b', 1.65));
  const key = new THREE.DirectionalLight('#ffe3bb', 3.2); key.position.set(-4, 7, 4); scene.add(key);
  const fill = new THREE.DirectionalLight('#d8e4f3', 1.65); fill.position.set(4, 3, -5); scene.add(fill);
  const rim = new THREE.DirectionalLight('#d6aa68', 1.3); rim.position.set(-6, -2, -3); scene.add(rim);
  // A back softbox keeps inspection views readable, not a black silhouette.
  const backFill = new THREE.DirectionalLight('#ead9c3', 3.0); backFill.position.set(1, -6, 3); scene.add(backFill);
  let model, environment;
  try {
    model = buildStudyGuitar();
    const room = new RoomEnvironment(), pmrem = new THREE.PMREMGenerator(renderer);
    try {
      // Small procedural studio environment, baked once; no HDR/photo download.
      environment = pmrem.fromScene(room, .04, .1, 100, { size: 64 });
      scene.environment = environment.texture; scene.environmentIntensity = .7;
    } finally { room.dispose(); pmrem.dispose(); }
  } catch (error) {
    if (model) disposeObject(model.group);
    environment?.dispose(); disposeObject(scene);
    renderer.dispose(); renderer.forceContextLoss(); throw error;
  }
  const neck = model.group;
  neck.scale.setScalar(1 / UNIT); neck.position.x = NUT_X;
  const markers = new THREE.Group(), fretLabels = new THREE.Group();
  scene.add(neck, markers, fretLabels);
  for (const fret of [3, 5, 7, 9, 12]) {
    const mm = (getFretPosition(fret - 1) + getFretPosition(fret)) / 2;
    const number = label(String(fret), { size: .23 });
    number.position.set(xAt(mm), 0, -(model.surfaces.widthAtX(mm) / 2 + 9) / UNIT);
    fretLabels.add(number);
  }
  canvas.dataset.stringCount = String(model.strings.length);
  canvas.dataset.fretCount = String(model.metadata.fretCount);
  canvas.dataset.handStatus = 'not-integrated';
  scene.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(neck).union(new THREE.Box3().setFromObject(fretLabels)).expandByScalar(.2);
  // Target the fretboard axis so perspective keeps the neck's 15-degree slope.
  const target = new THREE.Vector3(bounds.getCenter(new THREE.Vector3()).x, 0, 0);
  const camera = new THREE.PerspectiveCamera(38, 1, .1, 100);
  // OrbitControls caches this up-axis in its constructor. Set it first, once.
  camera.up.copy(referenceCameraUp());
  camera.position.copy(target).addScaledVector(new THREE.Vector3(...CAMERA_DIRECTIONS.angle).normalize(), 15);
  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(target);
  controls.enableDamping = false; controls.enablePan = false;
  controls.rotateSpeed = .65; controls.zoomSpeed = .7;
  // Keep the low-E edge upright while allowing true front/back/player views.
  controls.minPolarAngle = .45; controls.maxPolarAngle = Math.PI - .45;
  let disposed = false, lost = false, frame = 0, fitDistance = 15;
  const rounded = (vector) => vector.toArray().map((v) => +v.toFixed(7));
  const worldPoint = (point) => neck.localToWorld(point.clone());
  const project = (point) => rounded(worldPoint(point).project(camera));
  const geometrySignature = () => {
    // Fingerprint actual position buffers and model matrices, excluding sprites.
    // Recomputed on demand, so the diagnostics detect geometry mutation as well.
    let hash = 2166136261;
    neck.traverse((object) => {
      const array = object.geometry?.attributes.position?.array;
      if (!array) return;
      const words = new Uint32Array(array.buffer, array.byteOffset, array.byteLength / 4);
      for (const word of words) hash = Math.imul(hash ^ word, 16777619) >>> 0;
      const matrix = new Float32Array(object.matrixWorld.elements);
      for (const word of new Uint32Array(matrix.buffer)) hash = Math.imul(hash ^ word, 16777619) >>> 0;
    });
    return hash.toString(16).padStart(8, '0');
  };
  const updateDiagnostics = () => {
    camera.updateMatrixWorld(true); neck.updateMatrixWorld(true);
    canvas.dataset.camera = JSON.stringify({
      position: rounded(camera.position), target: rounded(controls.target), up: rounded(camera.up),
      distance: +camera.position.distanceTo(controls.target).toFixed(7), fov: camera.fov, aspect: camera.aspect,
    });
    canvas.dataset.practiceProjection = JSON.stringify({
      headstock: project(model.anchors.headstock), nut: project(model.anchors.nut),
      body: project(model.anchors.bodyDirection),
      strings: model.anchors.strings.map(({ number, note, radiusMm, position }) => ({
        number, note, radius: radiusMm / UNIT, world: rounded(worldPoint(position)), ndc: project(position),
      })), geometrySignature: geometrySignature(),
    });
  };
  const render = () => {
    frame = 0;
    if (disposed || lost || document.hidden) return;
    try { renderer.render(scene, camera); updateDiagnostics(); }
    catch { lost = true; onError('RENDER_FAILED'); }
  };
  const invalidate = () => { if (!disposed && !lost && !frame) frame = requestAnimationFrame(render); };
  controls.addEventListener('change', invalidate); controls.addEventListener('start', onInteraction);
  const setDistanceLimits = (distance) => {
    fitDistance = distance; controls.minDistance = distance * .38; controls.maxDistance = distance * 2.1;
  };
  function preset(name = 'angle') {
    const direction = new THREE.Vector3(...(CAMERA_DIRECTIONS[name] ?? CAMERA_DIRECTIONS.angle)).normalize();
    controls.target.copy(target);
    setDistanceLimits(fitPerspectiveDistance(camera, bounds, target, direction));
    camera.position.copy(target).addScaledVector(direction, fitDistance);
    controls.update(); updateDiagnostics(); invalidate();
  }
  const resize = () => {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height || disposed) return;
    const offset = camera.position.clone().sub(controls.target);
    const zoomRatio = offset.length() / fitDistance;
    camera.aspect = width / height; camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
    const nextFit = fitPerspectiveDistance(camera, bounds, controls.target, offset);
    setDistanceLimits(nextFit);
    camera.position.copy(controls.target).add(offset.setLength(THREE.MathUtils.clamp(nextFit * zoomRatio, controls.minDistance, controls.maxDistance)));
    controls.update(); updateDiagnostics(); invalidate();
  };
  const rotate = (horizontal = 0, vertical = 0) => {
    // Public controls methods respect its fixed up-axis; world-Y spherical math does not.
    controls.rotateLeft(-horizontal); controls.rotateUp(-vertical);
    updateDiagnostics(); invalidate();
  };
  const zoom = (factor) => {
    const offset = camera.position.clone().sub(controls.target);
    const distance = THREE.MathUtils.clamp(offset.length() * factor, controls.minDistance, controls.maxDistance);
    camera.position.copy(controls.target).add(offset.setLength(distance)); controls.update(); updateDiagnostics(); invalidate();
  };
  function setChord(nextChord) {
    disposeObject(markers);
    canvas.dataset.chordId = nextChord.id;
    nextChord.frets.forEach((fret, index) => {
      const number = 6 - index;
      // Schematic labels near the fret, never a claim of fingertip contact.
      const mm = fret > 0 ? getFretPosition(fret) - Math.min(4, (getFretPosition(fret) - getFretPosition(fret - 1)) * .25) : -10;
      const z = model.surfaces.stringZ(number, Math.max(0, mm));
      const y = model.surfaces.openStringCenterY(Math.max(0, mm), number);
      const marker = label(fret === null ? '×' : fret === 0 ? '○' : String(nextChord.fingers[index]), { gold: fret > 0, size: fret > 0 ? .29 : .23 });
      marker.position.set(xAt(mm), y / UNIT + .13, z / UNIT);
      markers.add(marker);
    });
    invalidate();
  }
  const keydown = (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const actions = {
      ArrowLeft: () => rotate(-.15), ArrowRight: () => rotate(.15),
      ArrowUp: () => rotate(0, -.12), ArrowDown: () => rotate(0, .12),
      '+': () => zoom(.85), '=': () => zoom(.85), '-': () => zoom(1.18),
      '0': () => preset(), Home: () => preset(),
    };
    if (!actions[event.key]) return;
    event.preventDefault(); onInteraction(); actions[event.key]();
  };
  const focus = () => canvas.focus({ preventScroll: true });
  const contextLost = (event) => { event.preventDefault(); lost = true; onError('CONTEXT_LOST'); };
  const visible = () => { if (!document.hidden) invalidate(); };
  canvas.addEventListener('keydown', keydown); canvas.addEventListener('pointerdown', focus);
  canvas.addEventListener('webglcontextlost', contextLost);
  document.addEventListener('visibilitychange', visible);
  host.appendChild(canvas);
  const observer = new ResizeObserver(resize); observer.observe(host);
  resize(); preset(); setChord(chord); cancelAnimationFrame(frame); render();
  return {
    preset, rotate, zoom, setChord,
    dispose() {
      disposed = true; cancelAnimationFrame(frame); observer.disconnect();
      controls.removeEventListener('change', invalidate); controls.removeEventListener('start', onInteraction);
      controls.dispose(); canvas.removeEventListener('keydown', keydown); canvas.removeEventListener('pointerdown', focus);
      canvas.removeEventListener('webglcontextlost', contextLost); document.removeEventListener('visibilitychange', visible);
      scene.environment = null; environment?.dispose();
      disposeObject(scene); renderer.dispose(); renderer.forceContextLoss(); canvas.remove();
    },
  };
}
