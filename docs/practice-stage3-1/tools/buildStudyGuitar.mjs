import * as THREE from 'three';

/**
 * Scratch generic acoustic study neck. All geometry is in millimetres.
 * Nut x=0; +X runs toward the body; +Y is out of the fingerboard; low E is +Z.
 * These are illustrative design dimensions, not a catalog guitar or CAD asset.
 */
export const STUDY_GUITAR = Object.freeze({
  scaleLength: 648, frets: 12, radius: 350, nutWidth: 43, widthAt12: 54,
  boardThickness: 5, backDepth: 21, stringSpanNut: 35, stringSpanBridge: 52,
  fretHeight: 1, fretCrownWidth: 2.2, pressOffset: 4, pressHeight: .75,
  openStringBottomAtNut: 1.4, openStringBottomAt12: 3.0,
  headstockLength: 175, headstockWidth: 70, headstockThickness: 14,
  headstockAngle: 14, tunerSpacing: 33,
});
const GAUGES = [1.32, .91, .66, .46, .33, .25];
const NOTES = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'];
const C_FRETS = [null, 3, 2, 0, 1, 0];
const C_FINGERS = [null, 3, 2, null, 1, null];
export const fretX = (fret) => STUDY_GUITAR.scaleLength * (1 - 2 ** (-fret / 12));
const boardLength = fretX(STUDY_GUITAR.frets) + 6;
export const widthAtX = (x) => THREE.MathUtils.lerp(STUDY_GUITAR.nutWidth, STUDY_GUITAR.widthAt12, THREE.MathUtils.clamp(x / fretX(12), 0, 1));
export const boardTopY = (z) => -(z * z) / (2 * STUDY_GUITAR.radius);
export const stringSpanAtX = (x) => THREE.MathUtils.lerp(STUDY_GUITAR.stringSpanNut, STUDY_GUITAR.stringSpanBridge, x / STUDY_GUITAR.scaleLength);
export const stringZ = (number, x) => (number - 3.5) * stringSpanAtX(x) / 5;
export const openStringCenterY = (x, number) => {
  const radius = GAUGES[6 - number] / 2;
  const atNut = boardTopY(stringZ(number, 0)) + STUDY_GUITAR.openStringBottomAtNut + radius;
  const at12 = boardTopY(stringZ(number, fretX(12))) + STUDY_GUITAR.openStringBottomAt12 + radius;
  return THREE.MathUtils.lerp(atNut, at12, x / fretX(12));
};
export const neckBackY = (x, z) => {
  const half = widthAtX(x) / 2;
  return boardTopY(z) - STUDY_GUITAR.boardThickness - (STUDY_GUITAR.backDepth - STUDY_GUITAR.boardThickness) * Math.sqrt(Math.max(0, 1 - (z / half) ** 2));
};

function woodMaps(enabled) {
  if (!enabled || typeof document === 'undefined') return {};
  const width = 512, height = 128;
  const make = (color) => {
    const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
    const ctx = canvas.getContext('2d');
    const image = ctx.createImageData(width, height);
    for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
      const longWave = Math.sin(y * .35 + Math.sin(x / 100 + y * .012) * 1.5);
      const fine = Math.sin(y * 2.9 + Math.sin(x / 80) * .4);
      const knot = Math.sin(Math.sqrt(((x - 170) / 5) ** 2 + ((y - 63) * 2) ** 2) * .7) * Math.exp(-(((x - 170) / 150) ** 2) - ((y - 63) / 40) ** 2);
      const grain = .5 + longWave * .23 + fine * .13 + knot * .07;
      const i = (y * width + x) * 4;
      const rgb = color ? [64 + grain * 31, 35 + grain * 19, 21 + grain * 13] : [125 + grain * 62, 125 + grain * 62, 125 + grain * 62];
      image.data.set([...rgb, 255], i);
    }
    ctx.putImageData(image, 0, 0);
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(1.3, 1);
    texture.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    return texture;
  };
  return { map: make(true), roughnessMap: make(false), bumpMap: make(false) };
}

function addMesh(group, geometry, material, name) {
  const mesh = new THREE.Mesh(geometry, material); mesh.name = name;
  mesh.castShadow = true; mesh.receiveShadow = true; group.add(mesh);
  return mesh;
}

function indexedGeometry(positions, indices, uv = []) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  if (uv.length) geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  return geometry;
}

/** A closed loft along X, using a clockwise Y/Z ring viewed along +X. */
function loftRings(rings) {
  const n = rings[0].length, positions = [], uv = [], indices = [];
  rings.forEach((ring, row) => ring.forEach((point, col) => {
    positions.push(...point); uv.push(row / (rings.length - 1), col / n);
  }));
  for (let row = 0; row < rings.length - 1; row++) for (let col = 0; col < n; col++) {
    const a = row * n + col, c = row * n + (col + 1) % n, b = a + n, d = c + n;
    indices.push(a, b, c, c, b, d);
  }
  for (const [row, reverse] of [[0, false], [rings.length - 1, true]]) {
    const ring = rings[row], center = ring.reduce((sum, v) => sum.map((value, i) => value + v[i] / n), [0, 0, 0]);
    const ci = positions.length / 3; positions.push(...center); uv.push(.5, .5);
    for (let col = 0; col < n; col++) {
      const a = row * n + col, b = row * n + (col + 1) % n;
      if (reverse) indices.push(ci, b, a); else indices.push(ci, a, b);
    }
  }
  return indexedGeometry(positions, indices, uv);
}

function dNeckGeometry() {
  const rings = [];
  for (let row = 0; row <= 24; row++) {
    const x = -9 + (boardLength + 9) * row / 24, half = widthAtX(x) / 2;
    const ring = [];
    for (let segment = 0; segment <= 20; segment++) {
      const angle = Math.PI * segment / 20, z = -half * Math.cos(angle);
      ring.push([x, neckBackY(x, z), z]);
    }
    for (let col = 1; col < 8; col++) {
      const z = half - 2 * half * col / 8; ring.push([x, boardTopY(z) - STUDY_GUITAR.boardThickness, z]);
    }
    rings.push(ring);
  }
  return loftRings(rings);
}

function fingerboardGeometry() {
  // A real solid: curved top, full-depth sides, flat underside, and end caps.
  const rings = [];
  for (let row = 0; row <= 24; row++) {
    const x = boardLength * row / 24, half = widthAtX(x) / 2, ring = [];
    // Top traverses right -> left so its normals point +Y in this loft convention.
    for (let col = 0; col <= 16; col++) {
      const z = half - 2 * half * col / 16; ring.push([x, boardTopY(z), z]);
    }
    for (let col = 0; col <= 8; col++) {
      const z = -half + 2 * half * col / 8; ring.push([x, boardTopY(z) - STUDY_GUITAR.boardThickness, z]);
    }
    rings.push(ring);
  }
  return loftRings(rings);
}

function crownGeometry(x) {
  const rings = [], half = widthAtX(x) / 2 - .25;
  // This sweep runs along Z, so construct directly rather than reusing the X loft.
  const positions = [], uv = [], indices = [], across = 8, crown = 12;
  for (let row = 0; row <= across; row++) {
    const z = -half + 2 * half * row / across;
    const ring = [];
    for (let col = 0; col < crown; col++) {
      const angle = 2 * Math.PI * col / crown;
      ring.push([x + Math.cos(angle) * STUDY_GUITAR.fretCrownWidth / 2,
        boardTopY(z) + STUDY_GUITAR.fretHeight / 2 + Math.sin(angle) * STUDY_GUITAR.fretHeight / 2, z]);
    }
    rings.push(ring);
    ring.forEach((v, col) => { positions.push(...v); uv.push(row / across, col / crown); });
  }
  const n = crown;
  for (let row = 0; row < across; row++) for (let col = 0; col < n; col++) {
    const a = row * n + col, b = a + n, c = row * n + (col + 1) % n, d = c + n;
    indices.push(a, c, b, c, d, b);
  }
  for (const row of [0, across]) {
    const ci = positions.length / 3, z = rings[row][0][2];
    positions.push(x, boardTopY(z) + .5, z); uv.push(.5, .5);
    for (let col = 0; col < crown; col++) {
      const a = row * n + col, b = row * n + (col + 1) % n;
      if (!row) indices.push(ci, b, a); else indices.push(ci, a, b);
    }
  }
  return indexedGeometry(positions, indices, uv);
}

function nutGeometry() {
  const ringAt = (x) => {
    const ring = [], half = STUDY_GUITAR.nutWidth / 2;
    const samples = [...new Set([...Array.from({ length: 129 }, (_, col) => -half + 2 * half * col / 128),
      ...Array.from({ length: 6 }, (_, index) => stringZ(6 - index, 0))])].sort((a, b) => a - b);
    for (const z of samples) {
      let top = boardTopY(z) + 1.8;
      for (let string = 1; string <= 6; string++) {
        const radius = GAUGES[6 - string] / 2, dz = z - stringZ(string, 0);
        top -= .4 * Math.exp(-((dz / (radius + .17)) ** 2));
      }
      ring.push([x, top, z]);
    }
    ring.push([x, -4.9, half], [x, -4.9, -half]);
    return ring.reverse();
  };
  return loftRings([ringAt(-4.3), ringAt(0)]);
}

function applyPlanarUv(geometry, xLength, zWidth) {
  const position = geometry.getAttribute('position'), uv = [];
  for (let i = 0; i < position.count; i++) uv.push(position.getX(i) / xLength, position.getZ(i) / zWidth + .5);
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
}

function headstockShape() {
  const shape = new THREE.Shape();
  shape.moveTo(-3, -21.5);
  shape.bezierCurveTo(-18, -24, -24, -31, -49, -32);
  shape.lineTo(-134, -35);
  shape.bezierCurveTo(-162, -35, -175, -28, -175, -17);
  shape.lineTo(-175, 17);
  shape.bezierCurveTo(-175, 28, -162, 35, -134, 35);
  shape.lineTo(-49, 32);
  shape.bezierCurveTo(-24, 31, -18, 24, -3, 21.5); shape.closePath();
  return shape;
}

/** Tube whose samples include EVERY control point, including string/fret contacts. */
function polylineTube(controlPoints, radius, radialSegments = 6, step = 7) {
  const points = [controlPoints[0].clone()];
  for (let segment = 1; segment < controlPoints.length; segment++) {
    const a = controlPoints[segment - 1], b = controlPoints[segment];
    const count = Math.max(1, Math.ceil(a.distanceTo(b) / step));
    for (let i = 1; i <= count; i++) points.push(a.clone().lerp(b, i / count));
  }
  const positions = [], uv = [], indices = [], up = new THREE.Vector3(0, 1, 0);
  points.forEach((point, row) => {
    const tangent = points[Math.min(row + 1, points.length - 1)].clone().sub(points[Math.max(0, row - 1)]).normalize();
    const binormal = tangent.clone().cross(up).normalize();
    const normal = binormal.clone().cross(tangent).normalize();
    for (let col = 0; col < radialSegments; col++) {
      const angle = 2 * Math.PI * col / radialSegments;
      const v = point.clone().addScaledVector(normal, Math.cos(angle) * radius).addScaledVector(binormal, Math.sin(angle) * radius);
      positions.push(...v.toArray()); uv.push(row / (points.length - 1), col / radialSegments);
      if (row < points.length - 1) {
        const a = row * radialSegments + col, b = a + radialSegments;
        const c = row * radialSegments + (col + 1) % radialSegments, d = c + radialSegments;
        indices.push(a, c, b, c, d, b);
      }
    }
  });
  return indexedGeometry(positions, indices, uv);
}

function makeHeadstock(parent, materials) {
  const headstock = new THREE.Group(); headstock.name = 'sculpted-headstock';
  headstock.position.set(-2, -4, 0); headstock.rotation.z = THREE.MathUtils.degToRad(STUDY_GUITAR.headstockAngle);
  parent.add(headstock);
  const shape = headstockShape();
  const geometry = new THREE.ExtrudeGeometry(shape, { depth: STUDY_GUITAR.headstockThickness, bevelEnabled: true, bevelSize: .75, bevelThickness: .7, bevelSegments: 2, curveSegments: 6, steps: 1 });
  geometry.rotateX(Math.PI / 2); applyPlanarUv(geometry, 175, 70);
  addMesh(headstock, geometry, materials.neck, 'headstock-solid');
  const veneer = new THREE.ShapeGeometry(shape, 8); veneer.rotateX(-Math.PI / 2); applyPlanarUv(veneer, 175, 70);
  const top = addMesh(headstock, veneer, materials.veneer, 'headstock-veneer'); top.position.y = .75;
  const pegPositions = [];
  for (let index = 0; index < 6; index++) {
    const side = index < 3 ? 1 : -1, along = index < 3 ? index : 5 - index;
    const x = -47 - along * STUDY_GUITAR.tunerSpacing, z = side * 24;
    const machine = new THREE.Group(); machine.name = `tuner-${6 - index}`; machine.position.set(x, 0, z); headstock.add(machine);
    const housing = addMesh(machine, new THREE.CylinderGeometry(6.2, 5.7, 7, 12), materials.metal, 'tuner-housing'); housing.position.y = -17.5;
    const washer = addMesh(machine, new THREE.TorusGeometry(4, .65, 5, 14), materials.metal, 'tuner-washer'); washer.rotation.x = Math.PI / 2; washer.position.y = 1.05;
    const post = addMesh(machine, new THREE.CylinderGeometry(2.4, 2.4, 9, 12), materials.metal, 'tuner-post'); post.position.y = 4.8;
    const shaft = addMesh(machine, new THREE.CylinderGeometry(1.65, 1.65, 17, 8), materials.metal, 'tuner-shaft'); shaft.rotation.x = Math.PI / 2; shaft.position.set(0, -17.5, side * 10);
    const button = addMesh(machine, new THREE.SphereGeometry(1, 12, 8), materials.pearl, 'tuner-button'); button.scale.set(6.3, 4.2, 2.6); button.position.set(0, -17.5, side * 20);
    const coilPoints = [], coilBase = 3.9, coilHeight = 2 * (GAUGES[index] + .15);
    for (let step = 0; step <= 36; step++) {
      const a = side * (step / 36 * Math.PI * 4 - Math.PI / 2);
      coilPoints.push(new THREE.Vector3(x + Math.cos(a) * 2.65, coilBase + step / 36 * coilHeight, z + Math.sin(a) * 2.65));
    }
    addMesh(headstock, polylineTube(coilPoints, GAUGES[index] / 2, 5, 4), materials.strings[index], 'string-wrap');
    pegPositions.push(new THREE.Vector3(x, coilBase + coilHeight, z - side * 2.65));
  }
  headstock.updateMatrix();
  return { headstock, pegPositions: pegPositions.map((v) => v.applyMatrix4(headstock.matrix)) };
}

/** C Major only. The model is not a clinical or instrument-manufacturer reference. */
export function buildStudyGuitar({ textures = true, chordId = 'C', pressOffsetsMm = [4, 4, 4], stringPathsMm = null } = {}) {
  if (pressOffsetsMm.length !== 3 || pressOffsetsMm.some((v) => !Number.isFinite(v) || v < 3 || v > 8)) {
    throw new RangeError('Three finger press offsets in the current fret must each be between 3 and 8 mm.');
  }
  if (chordId !== 'C') throw new RangeError('This scratch hand-contact neck supports C Major only.');
  const group = new THREE.Group(); group.name = 'study-guitar-neck-mm';
  group.userData.units = 'millimetres'; group.userData.genericStudyModel = true;
  const maps = woodMaps(textures);
  const materials = {
    neck: new THREE.MeshPhysicalMaterial({ ...maps, color: '#bb8b60', roughness: .48, metalness: 0, clearcoat: .22, clearcoatRoughness: .27, bumpScale: .035 }),
    board: new THREE.MeshStandardMaterial({ ...maps, color: '#694a36', roughness: .55, metalness: 0, bumpScale: .025 }),
    veneer: new THREE.MeshPhysicalMaterial({ ...maps, color: '#65462f', roughness: .4, clearcoat: .27, clearcoatRoughness: .3, bumpScale: .02, side: THREE.DoubleSide }),
    metal: new THREE.MeshStandardMaterial({ color: '#c1bfb7', metalness: .9, roughness: .24 }),
    pearl: new THREE.MeshPhysicalMaterial({ color: '#d3c8ab', metalness: .08, roughness: .35, clearcoat: .15 }),
    nut: new THREE.MeshStandardMaterial({ color: '#e4d5b1', roughness: .48 }),
    inlay: new THREE.MeshStandardMaterial({ color: '#d9d5c7', roughness: .34, metalness: .12 }),
    strings: GAUGES.map((_, i) => new THREE.MeshStandardMaterial({ color: i < 3 ? '#bfa572' : '#d0cec5', metalness: .84, roughness: i < 3 ? .32 : .24 })),
  };
  addMesh(group, dNeckGeometry(), materials.neck, 'd-section-neck-back');
  addMesh(group, fingerboardGeometry(), materials.board, 'curved-fingerboard');
  addMesh(group, nutGeometry(), materials.nut, 'grooved-nut');
  for (let fret = 1; fret <= STUDY_GUITAR.frets; fret++) {
    const wire = addMesh(group, crownGeometry(fretX(fret)), materials.metal, `fret-${fret}`); wire.userData.fret = fret;
    if ([3, 5, 7, 9, 12].includes(fret)) {
      const x = (fretX(fret - 1) + fretX(fret)) / 2;
      for (const z of fret === 12 ? [-7.2, 7.2] : [0]) {
        const dot = addMesh(group, new THREE.CircleGeometry(2, 16), materials.inlay, 'fingerboard-inlay');
        dot.rotation.x = -Math.PI / 2; dot.position.set(x, boardTopY(z) + .035, z);
      }
      const side = addMesh(group, new THREE.CircleGeometry(.9, 10), materials.inlay, 'neck-side-dot');
      side.position.set(x, -2.7, widthAtX(x) / 2 + .035);
    }
  }
  const { headstock, pegPositions } = makeHeadstock(group, materials), strings = [], stringTargets = [];
  for (let index = 0; index < 6; index++) {
    const number = 6 - index, radius = GAUGES[index] / 2, fret = C_FRETS[index];
    const nutZ = stringZ(number, 0), nutY = openStringCenterY(0, number);
    const points = [pegPositions[index], new THREE.Vector3(-4.3, nutY, nutZ), new THREE.Vector3(0, nutY, nutZ)];
    if (fret > 0) {
      const x = fretX(fret) - pressOffsetsMm[C_FINGERS[index] - 1], z = stringZ(number, x);
      points.push(new THREE.Vector3(x, boardTopY(z) + STUDY_GUITAR.pressHeight, z));
      const wireX = fretX(fret), wireZ = stringZ(number, wireX);
      points.push(new THREE.Vector3(wireX, boardTopY(wireZ) + STUDY_GUITAR.fretHeight + radius, wireZ));
      stringTargets.push({ finger: C_FINGERS[index], string: number, fret, stringCenterMm: [x, boardTopY(z) + STUDY_GUITAR.pressHeight, z], padContactTargetMm: [x, boardTopY(z) + STUDY_GUITAR.pressHeight + radius, z] });
    }
    const endZ = stringZ(number, boardLength);
    points.push(new THREE.Vector3(boardLength, openStringCenterY(boardLength, number), endZ));
    if (stringPathsMm?.[number]) {
      const path = stringPathsMm[number];
      if (!Array.isArray(path) || path.length < 2 || path.some((v, i) => !Array.isArray(v) || v.length !== 3 || !v.every(Number.isFinite) || (i && v[0] <= path[i-1][0])) || Math.abs(path[0][0]) > .001 || Math.abs(path.at(-1)[0] - boardLength) > .001) {
        throw new RangeError('A physical string path must cover nut to board end with finite increasing mm coordinates.');
      }
      points.splice(2, points.length - 2, ...path.map(v => new THREE.Vector3(...v)));
    }
    const string = addMesh(group, polylineTube(points, radius, 6, 7), materials.strings[index], `string-${number}`);
    string.userData = { number, note: NOTES[index], diameterMm: GAUGES[index], controlPointsMm: points.map((v) => v.toArray()), muted: fret === null };
    strings.push(string);
  }
  stringTargets.sort((a, b) => a.finger - b.finger);
  group.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(group);
  const metadata = { units: 'mm', genericStudyModel: true, stringCount: strings.length, fretCount: STUDY_GUITAR.frets, tunerCount: 6, dimensions: STUDY_GUITAR, boundsMm: { min: bounds.min.toArray(), max: bounds.max.toArray() }, contactTargetsAreNotAValidatedHandPose: true };
  group.userData = { ...group.userData, ...metadata };
  return { group, strings, stringTargets, headstock, materials, metadata, surfaces: { widthAtX, boardTopY, neckBackY, stringZ, fretX, openStringCenterY } };
}
