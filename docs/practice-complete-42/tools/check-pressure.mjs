import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync}from'node:child_process';
import {PRACTICE_CHORDS,PRACTICE_CHORD_BY_ID}from'../../../src/features/practice/data/chords.js';
import {buildStudyGuitar}from'../../../src/features/practice/scene/studyGuitar.js';
import {createFrettedStringController}from'../../../src/features/practice/scene/frettedStrings.js';
import {pressureContacts,pressureKey,pressureOffsetBounds,pressureX,validatePressureOffsets}from'../../../src/features/practice/scene/pressureContacts.js';
const file='src/features/practice/scene/frettedStrings.js',legacySource=execFileSync('git',['show',`1f2836b:${file}`],{encoding:'utf8'});
// Load the original controller with its original study geometry, without editing it.
const url=new URL('../../../src/features/practice/scene/studyGuitar.js',import.meta.url).href;
const {createFrettedStringController:legacy}=await import('data:text/javascript,'+encodeURIComponent(legacySource.replace("'./studyGuitar.js'",JSON.stringify(url)).replace("'three'",JSON.stringify(import.meta.resolve('three')))));
let count=0;const test=(name,fn)=>{fn();count++;console.log('PASS',name)};
function mapFor(c,value=12){return Object.fromEntries(pressureContacts(c).map(t=>[pressureKey(t.string,t.fret),Math.min(value,pressureOffsetBounds(t.fret).max)]))}
test('All 42 legacy string meshes, points, anchors and states remain exactly identical',()=>{
 for(const chord of PRACTICE_CHORDS){const old=buildStudyGuitar({textures:false}),next=buildStudyGuitar({textures:false});const a=legacy(old),b=createFrettedStringController(next);a.update(chord,true);b.update(chord,true);assert.equal(a.state,b.state);
 old.strings.forEach((s,i)=>{assert.deepEqual(s.geometry.attributes.position.array,next.strings[i].geometry.attributes.position.array);assert.deepEqual(s.geometry.index.array,next.strings[i].geometry.index.array);assert.deepEqual(s.userData.activeControlPointsMm,next.strings[i].userData.activeControlPointsMm);assert.deepEqual(old.anchors.strings[i].position,next.anchors.strings[i].position)});
 }
});
test('Valid pressure maps cover every and only actual finger/barre contact in every canonical chord',()=>{for(const c of PRACTICE_CHORDS){const map=mapFor(c);assert.equal(validatePressureOffsets(c,map),true);for(const t of pressureContacts(c)){const x=pressureX(t.string,t.fret,map);assert.ok(x>648*(1-2**(-(t.fret-1)/12))+4.999)}}});
test('Wrong strings, wrong frets, open/muted keys, missing keys, arrays and null cannot be approved',()=>{const c=PRACTICE_CHORD_BY_ID.C,good=mapFor(c);for(const bad of [null,[],{}, {...good,'6:1':4},{...good,'3:1':4},{...good,'1:1':4},{...good,'5:3':undefined}])assert.equal(validatePressureOffsets(c,bad),false)});
test('Zero, negative, infinite, NaN, booleans and values crossing either wire are rejected',()=>{const c=PRACTICE_CHORD_BY_ID.C;for(const value of [0,-1,Infinity,NaN,true,'4',.5,30,100]){const map=mapFor(c);map['5:3']=value;assert.equal(validatePressureOffsets(c,map),false)}});
test('The runtime refuses invalid pressure data before rebuilding any string mesh',()=>{const m=buildStudyGuitar({textures:false}),c=createFrettedStringController(m),before=m.strings.map(s=>s.geometry);assert.throws(()=>c.update(PRACTICE_CHORD_BY_ID.C,true,{'6:12':99}));m.strings.forEach((s,i)=>assert.equal(s.geometry,before[i]))});
test('Staggered A finger pressures change real string tubes without changing frets, fingers or pitch',()=>{const chord=PRACTICE_CHORD_BY_ID.A,snapshot=JSON.stringify(chord),m=buildStudyGuitar({textures:false}),c=createFrettedStringController(m);const map=Object.fromEntries(pressureContacts(chord).map(t=>[pressureKey(t.string,t.fret),t.finger===1?22:t.finger===2?13:4]));c.update(chord,true,map);for(const t of pressureContacts(chord))assert.ok(m.strings[6-t.string].userData.activeControlPointsMm.some(p=>Math.abs(p[0]-pressureX(t.string,t.fret,map))<1e-9));assert.equal(JSON.stringify(chord),snapshot)});
test('A full barre cannot import obsolete duplicate lower-fret pressure keys beneath a higher finger',()=>{const chord=PRACTICE_CHORD_BY_ID.F,good=mapFor(chord);assert.equal(validatePressureOffsets(chord,good),true);for(const key of ['5:1','4:1','3:1'])assert.equal(validatePressureOffsets(chord,{...good,[key]:8}),false)});
test('Changing pressure within the same chord rebuilds tubes and hiding the hand restores original open paths',()=>{const chord=PRACTICE_CHORD_BY_ID.A,m=buildStudyGuitar({textures:false}),c=createFrettedStringController(m);c.update(chord,true,mapFor(chord,10));const first=m.strings[2].geometry;c.update(chord,true,mapFor(chord,18));assert.notEqual(m.strings[2].geometry,first);c.update(chord,false);m.strings.forEach(s=>assert.deepEqual(s.userData.activeControlPointsMm,s.userData.controlPointsMm))});
fs.writeFileSync(new URL('../tests/pressure-unit.json',import.meta.url),JSON.stringify({passed:true,checks:count,legacyChordsCompared:42,teachingApproval:false},null,2)+'\n');console.log(`${count}/${count}`);
