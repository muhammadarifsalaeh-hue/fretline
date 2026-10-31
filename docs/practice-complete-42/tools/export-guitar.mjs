// Export the actual runtime strings, including optional audited pose pressures.
import fs from 'node:fs';
import * as THREE from 'three';
import { buildStudyGuitar } from '../../../src/features/practice/scene/studyGuitar.js';
import { createFrettedStringController } from '../../../src/features/practice/scene/frettedStrings.js';
import { PRACTICE_CHORD_BY_ID } from '../../../src/features/practice/data/chords.js';
const [id, output, poseFile] = process.argv.slice(2), chord = PRACTICE_CHORD_BY_ID[id];
if (!chord) throw Error('Unknown chord');
const pose = poseFile ? JSON.parse(fs.readFileSync(poseFile)) : null;
if (pose && pose.chordId !== id) throw Error('Wrong pose identity');
const model = buildStudyGuitar({ textures:false });
createFrettedStringController(model).update(chord,true,pose?.pressOffsetsMm);model.group.updateMatrixWorld(true);
const positions=[],indices=[],dominantBones=[];let offset=0;
model.group.traverse(o=>{if(!o.isMesh)return;const v=o.geometry.attributes.position;for(let i=0;i<v.count;i++){positions.push(new THREE.Vector3().fromBufferAttribute(v,i).applyMatrix4(o.matrixWorld).toArray());dominantBones.push(o.name)}const ix=o.geometry.index;for(let i=0;i<(ix?ix.count:v.count);i++)indices.push(offset+(ix?ix.getX(i):i));offset+=v.count});
const strings=model.strings.map((s,i)=>({number:6-i,radiusMm:s.userData.radiusMm,controlPointsMm:s.userData.activeControlPointsMm,openControlPointsMm:s.userData.controlPointsMm,centerlineSamplesMm:s.geometry.userData.centerlineSamplesMm}));
fs.writeFileSync(output,JSON.stringify({chordId:id,units:'millimetres',positions,indices,dominantBones,strings,pressOffsetsMm:pose?.pressOffsetsMm})+'\n');
