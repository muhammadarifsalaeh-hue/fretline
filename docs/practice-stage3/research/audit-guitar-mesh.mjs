import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import { buildStudyGuitar, fretX, neckBackY, boardTopY, widthAtX, stringZ, openStringCenterY } from './buildStudyGuitar.mjs';
const result = buildStudyGuitar({ textures: false });
const spec = JSON.parse(fs.readFileSync(new URL('./study-guitar-dimensions.json', import.meta.url)));
let triangles = 0, meshes = 0, vertices = 0;
const checks = [];
const check = (name, run) => { run(); checks.push({ name, passed: true }); };
const near = (a, b, tolerance = 1e-5) => assert.ok(Math.abs(a - b) <= tolerance, `${a} != ${b}`);
const names = [];
result.group.traverse((object) => {
  if (!object.isMesh) return;
  meshes++; names.push(object.name);
  const geometry = object.geometry, position = geometry.getAttribute('position');
  vertices += position.count;
  triangles += (geometry.index?.count ?? position.count) / 3;
  assert.ok([...position.array].every(Number.isFinite), object.name);
  assert.ok([...geometry.getAttribute('normal').array].every(Number.isFinite), object.name);
  if (geometry.index) assert.ok([...geometry.index.array].every((i) => i < position.count), object.name);
});
check('Six strings are genuinely meshed with correct low-E to high-E numbering', () => {
  assert.deepEqual(result.strings.map((o) => o.userData.number), [6,5,4,3,2,1]);
  assert.deepEqual(result.strings.map((o) => o.userData.note), ['E2','A2','D3','G3','B3','E4']);
  assert.equal(names.filter((n) => /^string-[1-6]$/.test(n)).length, 6);
});
check('Twelve separate fret crowns have decreasing equal-tempered spacing', () => {
  assert.equal(names.filter((n) => /^fret-\d+$/.test(n)).length, 12);
  near(fretX(12), 324);
  const gaps = Array.from({length: 12}, (_,i) => fretX(i+1)-fretX(i));
  assert.ok(gaps.every((gap, i) => i === 0 || gap < gaps[i-1]));
  for(let i=1;i<gaps.length;i++) near(gaps[i]/gaps[i-1], 2**(-1/12));
});
check('D back is total21mm deep at center; canonical curved edge and taper match', () => {
  for(const x of [0,32,66,99,150,324]) {
    near(neckBackY(x,0), -21);
    const half=widthAtX(x)/2;
    near(neckBackY(x,half), boardTopY(half)-5);
    near(neckBackY(x,half*.6), boardTopY(half*.6)-5-16*Math.sqrt(1-.6**2));
  }
  near(widthAtX(0),43); near(widthAtX(324),54);
});
check('All three C pad targets match the shared physical target JSON', () => {
  assert.equal(result.stringTargets.length,3);
  for(let i=0;i<3;i++) {
    const actual=result.stringTargets[i], expected=spec.activeFingerTargets[i];
    assert.equal(actual.finger,expected.finger); assert.equal(actual.string,expected.string); assert.equal(actual.fret,expected.fret);
    actual.padContactTargetMm.forEach((v,k)=>near(v,expected.padContactTargetMm[k],1e-10));
  }
});
check('C pressure and following fret support points are explicitly sampled by each string', () => {
  for(const target of result.stringTargets) {
    const string=result.strings.find((s)=>s.userData.number===target.string);
    const points=string.userData.controlPointsMm;
    assert.ok(points.some((p)=>p.every((v,k)=>Math.abs(v-target.stringCenterMm[k])<1e-10)));
    const fretPoint=points.find((p)=>Math.abs(p[0]-fretX(target.fret))<1e-10);
    assert.ok(fretPoint); near(fretPoint[1],boardTopY(fretPoint[2])+1+string.userData.diameterMm/2);
  }
});
check('Open string bottom action at nut and twelfth follows the shared canonical dimensions', () => {
  for(let number=1;number<=6;number++) {
    const radius=spec.stringDiametersMm[6-number]/2;
    near(openStringCenterY(0,number)-radius-boardTopY(stringZ(number,0)),spec.unpressedStringBottomAtNutMm);
    near(openStringCenterY(324,number)-radius-boardTopY(stringZ(number,324)),spec.unpressedStringBottomAt12Mm);
  }
});
let minimumOpenFretClearanceMm = Infinity;
check('All six open strings clear all twelve actual elliptical crown profiles', () => {
  for(let number=1;number<=6;number++) for(let fret=1;fret<=12;fret++) {
    const radius=spec.stringDiametersMm[6-number]/2;
    for(let k=0;k<=200;k++) {
      const dx=-1.1+2.2*k/200, x=fretX(fret)+dx, z=stringZ(number,x);
      const crownY=boardTopY(z)+.5+.5*Math.sqrt(Math.max(0,1-(dx/1.1)**2));
      const gap=openStringCenterY(x,number)-radius-crownY;
      minimumOpenFretClearanceMm=Math.min(minimumOpenFretClearanceMm,gap);
      assert.ok(gap>.05,`string${number}/fret${fret}: ${gap}mm clearance`);
    }
  }
});
check('Nut groove seats and each string bottom agree at1.4mm above the board', () => {
  const nut=result.group.getObjectByName('grooved-nut').geometry.attributes.position;
  for(let number=1;number<=6;number++) {
    const z=stringZ(number,0), floor=boardTopY(z)+1.4, radius=spec.stringDiametersMm[6-number]/2;
    const candidates=[];
    for(let i=0;i<nut.count;i++) if(Math.abs(nut.getZ(i)-z)<1e-5 && Math.abs(nut.getX(i))<1e-5 && nut.getY(i)>0) candidates.push(nut.getY(i));
    assert.ok(candidates.length>0);
    near(Math.min(...candidates),floor,2e-6);
    near(openStringCenterY(0,number)-radius,floor);
  }
});
check('Legitimate per-finger C offsets update actual string control points without changing fret or string', () => {
  const offsets=[4.5502,4.0548,4.0984], variant=buildStudyGuitar({textures:false,pressOffsetsMm:offsets});
  for(const target of variant.stringTargets) {
    near(target.stringCenterMm[0],fretX(target.fret)-offsets[target.finger-1]);
    near(target.stringCenterMm[2],stringZ(target.string,target.stringCenterMm[0]));
  }
  for(const values of [[2,4,4],[4,9,4],[4,NaN,4],[4,4]]) assert.throws(()=>buildStudyGuitar({textures:false,pressOffsetsMm:values}),RangeError);
});
check('Six3+3 tuners and the requested175mm/14degree headstock are present', () => {
  assert.equal(result.headstock.children.filter((o)=>/^tuner-/.test(o.name)).length,6);
  near(result.headstock.rotation.z,14*Math.PI/180);
  assert.equal(result.metadata.dimensions.headstockLength,175);
});
check('Surface normal winding faces outward on board, D back and metal crown', () => {
  for(const [name, kind, sign] of [['curved-fingerboard','top',1],['d-section-neck-back','back',-1],['fret-2','crown',1]]) {
    const mesh=result.group.getObjectByName(name), p=mesh.geometry.attributes.position, normal=mesh.geometry.attributes.normal;
    const samples=[];
    for(let i=0;i<p.count;i++) {
      const x=p.getX(i), y=p.getY(i), z=p.getZ(i);
      if(kind==='top'&&x>20&&x<300&&Math.abs(z)<15&&Math.abs(y-boardTopY(z))<1e-4) samples.push(normal.getY(i));
      if(kind==='back'&&x>20&&x<300&&Math.abs(z)<1&&y< -20.5) samples.push(normal.getY(i));
      if(kind==='crown'&&Math.abs(z)<15&&Math.abs(y-boardTopY(z)-1)<1e-4) samples.push(normal.getY(i));
    }
    assert.ok(samples.length>0,name);
    assert.ok(samples.reduce((a,b)=>a+b,0)/samples.length*sign>.98,name);
  }
});
check('Geometry remains below20k triangles with finite normal/position/index data', () => {
  assert.ok(triangles<20000); assert.ok(triangles>10000); assert.ok(vertices>5000);
});
const report = { scratchOnly: true, notAnAdoptedHandPose: true, triangles, meshes, vertices,
  minimumOpenFretClearanceMm, dimensions: result.metadata.dimensions, boundsMm: result.metadata.boundsMm, checks, passed: true,
  limitations: ['Generic modeled design, not manufacturer CAD.', 'No actual browser/render visual review in this isolated geometry audit.', 'Wood grain is procedural; realism still depends on lighting, environment, materials and the validated hand pose.', '70 static meshes are not a physical iPad frame-rate benchmark. Parent may merge/instance static hardware if profiling warrants it.'] };
fs.writeFileSync(new URL('./guitar-mesh-audit.json', import.meta.url), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({triangles,meshes,vertices,checks:checks.length,passed:true}));
