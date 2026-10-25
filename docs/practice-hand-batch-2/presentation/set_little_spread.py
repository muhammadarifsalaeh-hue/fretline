#!/usr/bin/env python3
"""Repeat a small real-joint authoring operation; never move other digits."""
import argparse,importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('solver',ROOT/'scripts/practice/solve-hand-poses.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('output',type=Path);ap.add_argument('degrees',type=float);args=ap.parse_args()
r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');p=json.loads(args.input.read_text());angles=np.array(p['solverParameters']);angles[19]=np.deg2rad(args.degrees);p['solverParameters']=angles.tolist();q=r.rotations(angles)
for name in ['finger5-1.L','finger5-2.L','finger5-3.L']:p['bones'][name]['quaternion']=q[r.by_name[name]].tolist()
p['audit']={'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False}
args.output.write_text(json.dumps(p,indent=2)+'\n')
