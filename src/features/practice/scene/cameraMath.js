import * as THREE from 'three';

export const CAMERA_DIRECTIONS = Object.freeze({
  angle: [-.12, 1, .30],
  front: [0, 1, .02],
  head: [-1, .55, .24],
  back: [.08, -1, .22],
  side: [-.08, .18, 1],
  // Player looks down from the low-E edge while retaining the board face.
  // A negative Y direction exposed rear wood and hid the fretting fingers.
  player: [.22, .65, .95],
});

/** +Z is the low-E edge. No guitar coordinate or string index changes. */
export function referenceCameraUp(direction = CAMERA_DIRECTIONS.angle, slopeDegrees = 15) {
  const backwards = new THREE.Vector3(...direction).normalize();
  const up = new THREE.Vector3(0, 0, 1).addScaledVector(backwards, -backwards.z).normalize();
  const right = new THREE.Vector3().crossVectors(backwards.clone().negate(), up).normalize();
  const head = new THREE.Vector3(-1, 0, 0);
  const baseSlope = Math.atan2(head.dot(up), head.dot(right));
  const roll = THREE.MathUtils.degToRad(slopeDegrees) - baseSlope;
  return up.multiplyScalar(Math.cos(roll)).addScaledVector(right, Math.sin(roll)).normalize();
}

export const boundsCorners = bounds => Array.from({length: 8}, (_, i) => new THREE.Vector3(
  i & 1 ? bounds.max.x : bounds.min.x,
  i & 2 ? bounds.max.y : bounds.min.y,
  i & 4 ? bounds.max.z : bounds.min.z,
));

/** Fits every corner under perspective, including projected depth, and arbitrary fixed up. */
export function fitPerspectiveDistance(camera, bounds, target, direction, margin = 1.12) {
  const backwards = direction.clone().normalize();
  const right = new THREE.Vector3().crossVectors(backwards.clone().negate(), camera.up).normalize();
  const up = new THREE.Vector3().crossVectors(right, backwards).normalize();
  if (right.lengthSq() < .5 || up.lengthSq() < .5) throw new RangeError('Camera up is parallel to the view');
  const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const tanH = tanV * camera.aspect;
  let distance = camera.near * 2;
  for (const corner of boundsCorners(bounds)) {
    const relative = corner.sub(target), depth = relative.dot(backwards);
    distance = Math.max(distance,
      depth + margin * Math.abs(relative.dot(right)) / tanH,
      depth + margin * Math.abs(relative.dot(up)) / tanV,
      depth + camera.near * 2,
    );
  }
  return distance;
}

export function placeCamera(camera, bounds, target, preset = 'angle', margin = 1.12) {
  const direction = new THREE.Vector3(...CAMERA_DIRECTIONS[preset]).normalize();
  const distance = fitPerspectiveDistance(camera, bounds, target, direction, margin);
  camera.position.copy(target).addScaledVector(direction, distance);
  camera.lookAt(target); camera.updateMatrixWorld(true);
  return distance;
}
