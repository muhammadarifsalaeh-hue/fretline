import assert from 'node:assert/strict';
import * as THREE from 'three';
import { CAMERA_DIRECTIONS, referenceCameraUp, placeCamera } from '../../src/features/practice/scene/cameraMath.js';
const bounds = new THREE.Box3(new THREE.Vector3(-100,-80,-130),new THREE.Vector3(220,40,40));
const target = new THREE.Vector3(50,0,-20);
for (const aspect of [1440/1000,1024/1366,390/844]) {
  const camera = new THREE.PerspectiveCamera(38,aspect,.1,2000);camera.up.copy(referenceCameraUp());
  for (const preset of ['angle','player']) {
    placeCamera(camera,bounds,target,preset);camera.updateProjectionMatrix();
    const front = new THREE.Vector3(65,5,0), back = new THREE.Vector3(65,-20,0);
    const direction = camera.position.clone().sub(target).normalize();
    assert.ok(direction.y>.5, preset+': the eye must be on the fingerboard side, not behind the neck');
    assert.ok(front.distanceTo(camera.position)<back.distanceTo(camera.position),preset+': fingerboard face must be nearer than rear wood');
    const low = new THREE.Vector3(65,2,18).project(camera), high = new THREE.Vector3(65,2,-18).project(camera);
    assert.ok(low.y>high.y,preset+': low E must project above high e');
    const head=new THREE.Vector3(-70,0,0).project(camera), body=new THREE.Vector3(180,0,0).project(camera);
    assert.ok(head.x>body.x && head.y>body.y,preset+': headstock remains right/up');
  }
}
assert.deepEqual(CAMERA_DIRECTIONS.angle,[-.12,1,.30]);
console.log('PASS default/player board visibility, E–e order and headstock direction at desktop/tablet/mobile aspects; original default unchanged');
