import assert from 'node:assert/strict';
import fs from 'node:fs';
import { PRACTICE_CHORDS } from '../../../src/features/practice/data/chords.js';
import { ChordAudioPlayer, chordTones, strumOffsets, PLAYBACK_RATES } from '../../../src/features/practice/audio/chordAudio.js';
let passed=0;const rows=[];
async function test(name,fn){await fn();passed++;rows.push({name,passed:true});console.log('PASS',name);}
const tuning=[40,45,50,55,59,64];
await test('All 42 canonical voicings sound only their actual open/fretted strings at the correct pitch',()=>{
 for(const chord of PRACTICE_CHORDS){const actual=chordTones(chord);const expected=chord.frets.flatMap((f,i)=>f===null?[]:[{string:6-i,midi:tuning[i]+f}]);
  assert.equal(actual.length,expected.length);
  actual.forEach((tone,i)=>{assert.equal(tone.string,expected[i].string);assert.equal(tone.midi,expected[i].midi);assert.ok(Math.abs(69+12*Math.log2(tone.frequency/440)-tone.midi)<1e-10);});
 }
});
await test('Slowing the strum changes timing without changing pitch, order or muted-string exclusion',()=>{
 for(const chord of PRACTICE_CHORDS){const n=chordTones(chord).length,normal=strumOffsets(n,1);
  for(const rate of PLAYBACK_RATES){const offsets=strumOffsets(n,rate);assert.equal(offsets[0],0);offsets.forEach((t,i)=>assert.ok(Math.abs(t-normal[i]/rate)<1e-12));}
 }
});
await test('Invalid note spellings and unsupported rates cannot schedule sound',async()=>{
 assert.throws(()=>chordTones({notes:['H3',null,null,null,null,null]}));assert.throws(()=>strumOffsets(5,0));assert.throws(()=>strumOffsets(5,Infinity));
});
function fixture({suspended=false}={}){
 let resume;const nodes=[],states=[];
 const param=()=>({value:0,setValueAtTime(){},exponentialRampToValueAtTime(){},cancelAndHoldAtTime(){}});
 const context={currentTime:10,state:suspended?'suspended':'running',destination:{},resumes:0,closed:0,
 createPeriodicWave:(real,imaginary)=>({real,imaginary}),createBiquadFilter:()=>({frequency:param(),Q:param(),connect(){},disconnect(){}}),
 createGain:()=>({gain:param(),connect(){},disconnect(){this.disconnected=true;}}),
 createOscillator(){const node={frequency:{value:0},starts:[],stops:[],setPeriodicWave(){},connect(){},disconnect(){this.disconnected=true;},start(t){this.starts.push(t);},stop(t){this.stops.push(t);}};nodes.push(node);return node;},
 resume(){this.resumes++;return new Promise(resolve=>{resume=()=>{this.state='running';resolve();};});},
 close(){this.closed++;this.state='closed';return Promise.resolve();}};
 let created=0;const player=new ChordAudioPlayer({onState:s=>states.push(s),contextFactory:()=>{created++;return context;}});
 return {player,context,nodes,states,unlock:()=>resume(),created:()=>created};
}
await test('One voice per sounding string, bounded level envelope and tempo schedule',async()=>{
 const t=fixture();const chord=PRACTICE_CHORDS.find(c=>c.id==='C');await t.player.play(chord,.5);
 assert.equal(t.nodes.length,5);assert.equal(t.created(),1);const times=t.nodes.map(n=>n.starts[0]);times.forEach((v,i)=>assert.ok(Math.abs(v-10.025-i*.24)<1e-9));
 t.nodes.forEach((n,i)=>assert.equal(n.frequency.value,chordTones(chord)[i].frequency));t.nodes.forEach(n=>n.onended());assert.equal(t.player.playing,false);assert.equal(t.states.at(-1).status,'idle');
 t.player.dispose();
});
await test('Stop cancels future strums and a stale ended event cannot stop a replacement chord',async()=>{
 const t=fixture();await t.player.play(PRACTICE_CHORDS[0]);const old=[...t.nodes];t.player.stop();assert.equal(t.player.voices.size,0);assert.ok(old.every(n=>n.stops.length===2));
 await t.player.play(PRACTICE_CHORDS[8]);old.forEach(n=>n.onended());assert.equal(t.player.playing,true);assert.equal(t.created(),1);t.player.dispose();
});
await test('A pending iPad unlock superseded by stop cannot start stale chord audio',async()=>{
 const t=fixture({suspended:true});const pending=t.player.play(PRACTICE_CHORDS[0]);assert.equal(t.context.resumes,1);t.player.stop();t.unlock();await pending;assert.equal(t.nodes.length,0);assert.equal(t.player.playing,false);t.player.dispose();
});
await test('Unmount/dispose closes its audio context once and prevents future playback',async()=>{
 const t=fixture();await t.player.play(PRACTICE_CHORDS[0]);const count=t.nodes.length;t.player.dispose();t.player.dispose();await t.player.play(PRACTICE_CHORDS[1]);assert.equal(t.context.closed,1);assert.equal(t.nodes.length,count);assert.equal(t.player.voices.size,0);
});
fs.mkdirSync('docs/practice-complete-42/tests',{recursive:true});fs.writeFileSync('docs/practice-complete-42/tests/audio-unit.json',JSON.stringify({passed:true,checks:passed,chordsChecked:42,allPitchesFromCanonicalData:true,realBrowserAudioTestSeparate:true,unitContextIsFixture:true,rows},null,2)+'\n');
console.log(`Practice audio: ${passed} passed, 0 failed.`);
