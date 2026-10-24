import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FRET_COUNT, STRING_COUNT, getFretPosition, getFingerPosition, getStringZ } from '../data/fretboard';

// A generic study model, not an asset or specification of any catalog guitar.
// Model coordinates use 40 mm per world unit: nut -> body is +X, board up is +Y.
const UNIT = 40;
const LENGTH = getFretPosition(FRET_COUNT) / UNIT;
const NUT_X = -LENGTH / 2;
const xAt = (mm) => NUT_X + mm / UNIT;
const topAt = (z) => .14 - z * z / (2 * 8.75);

function woodTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512; canvas.height = 128;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#38251b'; ctx.fillRect(0, 0, 512, 128);
  // Deterministic procedural grain: no downloaded photos or model likeness.
  for (let row = 0; row < 128; row += 2) {
    ctx.strokeStyle = row % 6 ? '#21161075' : '#91624466';
    ctx.lineWidth = row % 3 ? .6 : 1.2;
    ctx.beginPath();
    for (let x = 0; x <= 512; x += 8) {
      const y = row + Math.sin(x / 87 + row * .2) * 1.8;
      if (!x) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping; texture.repeat.set(2, 1);
  return texture;
}

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
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map, depthTest: false, toneMapped: false }));
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

function buildNeck() {
  const group = new THREE.Group();
  const grain = woodTexture();
  const walnut = new THREE.MeshStandardMaterial({ color: '#9d7650', map: grain, roughness: .57 });
  const boardMaterial = new THREE.MeshStandardMaterial({ map: grain, color: '#c3a180', roughness: .58 });
  const metal = new THREE.MeshStandardMaterial({ color: '#c7c2af', metalness: .7, roughness: .27 });
  const outline = new THREE.Shape();
  outline.moveTo(NUT_X - .08, -.575); outline.lineTo(LENGTH / 2 + .14, -.72);
  outline.lineTo(LENGTH / 2 + .14, .72); outline.lineTo(NUT_X - .08, .575); outline.closePath();
  const neckGeometry = new THREE.ExtrudeGeometry(outline, { depth: .36, bevelEnabled: true, bevelSize: .055, bevelThickness: .055, bevelSegments: 3, steps: 1 });
  neckGeometry.rotateX(Math.PI / 2);
  group.add(new THREE.Mesh(neckGeometry, walnut));

  // Curved, gently tapered fingerboard. Fret positions below use equal temperament.
  const positions = [], uvs = [], indices = [], rows = 32, columns = 12;
  for (let row = 0; row <= rows; row++) {
    const fraction = row / rows, x = NUT_X + fraction * (LENGTH + .12);
    for (let col = 0; col <= columns; col++) {
      const z = (col / columns * 2 - 1) * (.575 + .145 * fraction);
      positions.push(x, topAt(z), z); uvs.push(fraction, col / columns);
      if (row < rows && col < columns) {
        const a = row * (columns + 1) + col, b = a + columns + 1;
        indices.push(a, a + 1, b, a + 1, b + 1, b);
      }
    }
  }
  const boardGeometry = new THREE.BufferGeometry();
  boardGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  boardGeometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  boardGeometry.setIndex(indices); boardGeometry.computeVertexNormals();
  group.add(new THREE.Mesh(boardGeometry, boardMaterial));
  const nut = new THREE.Mesh(new THREE.BoxGeometry(.075, .13, 1.18), new THREE.MeshStandardMaterial({ color: '#ede1bc', roughness: .4 }));
  nut.position.set(NUT_X - .025, .16, 0); group.add(nut);

  for (let fret = 1; fret <= FRET_COUNT; fret++) {
    const x = xAt(getFretPosition(fret)), halfWidth = .575 + .145 * (x - NUT_X) / LENGTH;
    const points = Array.from({ length: 9 }, (_, index) => {
      const z = -halfWidth + 2 * halfWidth * index / 8;
      return new THREE.Vector3(x, topAt(z) + .018, z);
    });
    const wire = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), 12, .016, 6, false), metal);
    wire.name = `fret-${fret}`; group.add(wire);
    if ([3, 5, 7, 9, 12].includes(fret)) {
      for (const z of fret === 12 ? [-.24, .24] : [0]) {
        const dot = new THREE.Mesh(new THREE.CircleGeometry(.048, 16), new THREE.MeshStandardMaterial({ color: '#d9cba4', roughness: .4 }));
        dot.rotation.x = -Math.PI / 2; dot.position.set(xAt(getFingerPosition(fret)), topAt(z) + .003, z); group.add(dot);
      }
      const number = label(String(fret), { size: .23 });
      number.position.set(xAt(getFingerPosition(fret)), .12, -.94); group.add(number);
    }
  }

  const head = new THREE.Mesh(new THREE.BoxGeometry(1.35, .28, 1.36), walnut);
  head.position.set(NUT_X - .8, -.08, 0); head.rotation.z = -.07; group.add(head);
  for (let index = 0; index < STRING_COUNT; index++) {
    const z = getStringZ(index) / UNIT;
    const radius = [.016, .013, .010, .007, .005, .004][index];
    const string = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, LENGTH + 1.12, 8),
      new THREE.MeshStandardMaterial({ color: index < 3 ? '#d5b577' : '#d9d7ca', metalness: .65, roughness: .28 }));
    string.rotation.z = Math.PI / 2;
    string.position.set(-.45, topAt(z) + .09, z); string.name = `string-${6 - index}`; group.add(string);
    const peg = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, .22, 10), metal);
    peg.position.set(NUT_X - .35 - (index % 3) * .38, .12, index < 3 ? .65 : -.65); group.add(peg);
  }
  return group;
}

/** Creates a real WebGL scene. No render loop runs while the model is idle. */
export function createNeckScene(host, { chord, canvasLabel, onError, onInteraction }) {
  const canvas = document.createElement('canvas');
  canvas.setAttribute('data-practice-canvas', '');
  canvas.setAttribute('aria-label', canvasLabel);
  canvas.setAttribute('aria-describedby', 'practice-camera-help'); canvas.tabIndex = 0;
  canvas.dataset.stringCount = String(STRING_COUNT); canvas.dataset.fretCount = String(FRET_COUNT);
  const context = canvas.getContext('webgl2', { alpha: true, antialias: true, powerPreference: 'low-power' });
  if (!context) throw new Error('WEBGL_UNAVAILABLE');
  const renderer = new THREE.WebGLRenderer({ canvas, context, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.35;
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight('#f8e8cc', '#26232a', 2.5));
  const key = new THREE.DirectionalLight('#ffe1ac', 4); key.position.set(-2, 7, 3); scene.add(key);
  const fill = new THREE.DirectionalLight('#dce7ef', 2.5); fill.position.set(3, 4, -5); scene.add(fill);
  const rim = new THREE.DirectionalLight('#c89951', 2); rim.position.set(-6, 1, -2); scene.add(rim);
  let neck;
  try { neck = buildNeck(); }
  catch (error) {
    // Release a partially initialized graphics context before showing recovery UI.
    disposeObject(scene); renderer.dispose(); renderer.forceContextLoss(); throw error;
  }
  const markers = new THREE.Group(); scene.add(neck, markers);
  canvas.dataset.stringCount = String(neck.children.filter((object) => object.name.startsWith('string-')).length);
  canvas.dataset.fretCount = String(neck.children.filter((object) => object.name.startsWith('fret-')).length);
  const camera = new THREE.PerspectiveCamera(38, 1, .1, 100);
  camera.position.set(0, 7, 10);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = false; controls.enablePan = false;
  controls.rotateSpeed = .65; controls.zoomSpeed = .7;
  controls.minPolarAngle = .08; controls.maxPolarAngle = Math.PI * .83;
  let disposed = false, lost = false, frame = 0, fitDistance = 13;
  const updateDiagnostics = () => {
    canvas.dataset.camera = JSON.stringify({
      position: camera.position.toArray().map((v) => +v.toFixed(5)),
      target: controls.target.toArray().map((v) => +v.toFixed(5)),
      distance: +camera.position.distanceTo(controls.target).toFixed(5),
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

  function preset(name = 'angle') {
    const direction = name === 'front' ? [0, 1, .035] : name === 'head' ? [-1, .48, .32] : [.12, .8, 1];
    controls.target.set(name === 'head' ? -1.4 : -.65, 0, 0);
    camera.position.copy(controls.target).add(new THREE.Vector3(...direction).normalize().multiplyScalar(fitDistance));
    controls.update(); updateDiagnostics(); invalidate();
  }
  const resize = () => {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height || disposed) return;
    camera.aspect = width / height; camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
    const nextFit = Math.max(10.2 / camera.aspect, 4.1) / (2 * Math.tan(THREE.MathUtils.degToRad(19))) * 1.12;
    const offset = camera.position.clone().sub(controls.target).multiplyScalar(nextFit / fitDistance);
    fitDistance = nextFit; controls.minDistance = nextFit * .38; controls.maxDistance = nextFit * 2.1;
    camera.position.copy(controls.target).add(offset); controls.update(); updateDiagnostics(); invalidate();
  };
  const rotate = (horizontal = 0, vertical = 0) => {
    const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
    spherical.theta += horizontal;
    spherical.phi = THREE.MathUtils.clamp(spherical.phi + vertical, controls.minPolarAngle, controls.maxPolarAngle);
    camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));
    controls.update(); updateDiagnostics(); invalidate();
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
      const z = getStringZ(index) / UNIT;
      const marker = label(fret === null ? '×' : fret === 0 ? '○' : String(nextChord.fingers[index]), { gold: fret > 0, size: fret > 0 ? .29 : .23 });
      marker.position.set(fret > 0 ? xAt(getFingerPosition(fret)) : NUT_X - .24, topAt(z) + .19, z);
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
      disposeObject(scene); renderer.dispose(); renderer.forceContextLoss(); canvas.remove();
    },
  };
}
