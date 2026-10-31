"""Independent fret-domain rejection and Python-vs-runtime pressure-line parity."""
import copy,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('gate',Path(__file__).with_name('check-geometry.py'));gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate)
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v4.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
chords=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=ROOT));rows=[]
with tempfile.TemporaryDirectory(prefix='fretline-pressure-parity-')as temporary:
 folder=Path(temporary)
 for chord in chords:
  contacts=gate.effective_contacts(chord);groups=list(dict.fromkeys((t['string'],t['fret'])for t in contacts));group_for=[groups.index((t['string'],t['fret']))for t in contacts];offsets={f'{string}:{fret}':float(2+(i%4)*5)for i,(string,fret)in enumerate(groups)};pose={'chordId':chord['id'],'pressOffsetsMm':offsets};gate.check_pressure_offsets(chord,pose)
  for key in offsets:
   for value in [0,-1,.5,30,float('nan'),float('inf'),True,'4']:
    bad=copy.deepcopy(pose);bad['pressOffsetsMm'][key]=value
    try:gate.check_pressure_offsets(chord,bad)
    except AssertionError:pass
    else:raise AssertionError('Invalid offset accepted')
  for bad_map in [None,[],{},dict(offsets,**{'6:12':3})]:
   try:gate.check_pressure_offsets(chord,dict(pose,pressOffsetsMm=bad_map))
   except AssertionError:pass
   else:raise AssertionError('Missing/wrong canonical contact accepted')
  source=folder/'pose.json';source.write_text(json.dumps(pose));target=folder/'guitar.json';subprocess.run(['node',str(Path(__file__).with_name('export-guitar.mjs')),chord['id'],str(target),str(source)],cwd=ROOT,check=True);guitar=json.loads(target.read_text());xs=np.array([f.m.fret_x(fret)-offsets[f'{string}:{fret}']for string,fret in groups]);predicted=f.pressure_lines(guitar,chord,contacts,group_for,xs);error=0
  for line in guitar['strings']:
   number=line['number'];actual=np.array(line['controlPointsMm']);before=np.array(predicted[number]['controlPointsMm']);sample=np.unique(np.r_[actual[:,0],before[:,0],np.linspace(actual[0,0],actual[-1,0],1200)])
   for axis in [1,2]:error=max(error,float(np.max(abs(np.interp(sample,actual[:,0],actual[:,axis])-np.interp(sample,before[:,0],before[:,axis])))))
  assert error<1e-10,(chord['id'],error);rows.append({'id':chord['id'],'pressureKeysMatchCanonicalFingering':True,'invalidOffsetsRejected':True,'maximumRuntimeLineErrorMm':error});print('PASS',chord['id'],error,flush=True)
report={'passed':True,'chords':42,'independentNumericBounds':True,'actualRuntimeExportCompared':True,'rows':rows};(ROOT/'docs/practice-complete-42/tests/pressure-geometry-unit.json').write_text(json.dumps(report,indent=2)+'\n')
