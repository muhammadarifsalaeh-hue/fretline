import * as THREE from 'three';
import { createStudyStringGeometry, STUDY_GUITAR } from './studyGuitar.js';
import { pressureX, validatePressureOffsets } from './pressureContacts.js';

// A displayed hand presses the actual tubes, rather than passing through an
// unchanged open string. Original poses retain their inclusive barre paths;
// authored maps use each sounding string's canonical effective finger/fret.
export function createFrettedStringController(model) {
  const originals = model.strings.map((string) => string.userData.controlPointsMm.map((p) => new THREE.Vector3(...p)));
  let state = 'open', shapeKey = 'open';
  function update(chord, handVisible, offsets) {
    if (handVisible && !validatePressureOffsets(chord, offsets)) throw new Error('INVALID_FINGER_PRESSURE');
    const nextState = handVisible ? chord.id : 'open';
    const nextShape = handVisible && offsets ? `${nextState}:${JSON.stringify(Object.entries(offsets).sort())}` : nextState;
    if (shapeKey === nextShape) return;
    model.strings.forEach((string, index) => {
      const number = 6 - index, radius = string.userData.radiusMm;
      const original = originals[index];
      let points = original.map((p) => p.clone());
      const frets = new Set();
      if (handVisible) {
        if (chord.frets[index] > 0) frets.add(chord.frets[index]);
        // Legacy poses retain their original tubes byte for byte. New authored
        // pressure maps follow the effective finger/fret in the chord diagram.
        (offsets ? [] : chord.barres || []).forEach((barre) => {
          if (number <= barre.fromString && number >= barre.toString) frets.add(barre.fret);
        });
      }
      if (frets.size) {
        points = original.filter((p) => p.x <= 0).map((p) => p.clone());
        for (const fret of [...frets].sort((a, b) => a - b)) {
          const wireX = model.surfaces.fretX(fret);
          for (const x of [pressureX(number, fret, offsets), wireX]) {
            const z = model.surfaces.stringZ(number, x);
            // Small crown clearance prevents numerical grazing at intermediate
            // wires of a barre. This is a generic study model, not catalog data.
            const y = model.surfaces.boardTopY(z) + STUDY_GUITAR.fretHeight + radius + .025;
            points.push(new THREE.Vector3(x, y, z));
          }
        }
        points.push(original.at(-1).clone());
        const referenceX = model.metadata.referenceStringXmm;
        if (!points.some((p) => Math.abs(p.x - referenceX) < 1e-7)) {
          const right = points.findIndex((p) => p.x > referenceX);
          if (right > 0) {
            const a = points[right - 1], b = points[right];
            points.splice(right, 0, a.clone().lerp(b, (referenceX - a.x) / (b.x - a.x)));
          }
        }
      }
      const geometry = createStudyStringGeometry(points, radius, 6, 7);
      string.geometry.dispose(); string.geometry = geometry;
      string.userData.open = !frets.size;
      string.userData.activeControlPointsMm = points.map((p) => p.toArray());
      const samples = geometry.userData.centerlineSamplesMm;
      const ring = samples.findIndex((p) => Math.abs(p[0] - model.metadata.referenceStringXmm) < 1e-7);
      const anchor = model.anchors.strings[index].position.set(0, 0, 0);
      const positions = geometry.attributes.position;
      for (let side = 0; side < geometry.userData.radialSegments; side++) {
        anchor.add(new THREE.Vector3().fromBufferAttribute(positions, ring * geometry.userData.radialSegments + side));
      }
      anchor.multiplyScalar(1 / geometry.userData.radialSegments);
    });
    state = nextState; shapeKey = nextShape;
    model.group.userData.stringPose = state;
  }
  return { update, get state() { return state; } };
}
