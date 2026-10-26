#!/usr/bin/env python3
"""Actual geometry/rig regressions for the shared offline solver.

These tests certify parameterization and musical topology, not teaching anatomy.
No runtime library, source mesh or musical record is edited by this test.
"""
import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('central_hand_solver', HERE/'solve.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class SharedSolverMath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = s.load_context()
        cls.rig = cls.context['rig']
        cls.temporary = tempfile.TemporaryDirectory(prefix='fretline-shared-math-')
        cls.guitar = s.runtime_guitar(cls.context['chords']['C'], cls.temporary.name)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_closed_triangle_face_edge_vertex_and_nearest_mesh(self):
        triangles = np.array([[[0.,0,0],[4,0,0],[0,4,0]], [[0,0,20],[4,0,20],[0,4,20]]])
        cases = [([1,1,3],[1,1,0]), ([3,3,2],[2,2,0]), ([-2,-1,0],[0,0,0]), ([1,1,19],[1,1,20])]
        for query, expected in cases:
            with self.subTest(query=query):
                point, face, bary = s.closest_triangle_point(triangles, np.array(query, dtype=float))
                np.testing.assert_allclose(point, expected, atol=1e-12)
                np.testing.assert_allclose(bary @ triangles[face], point, atol=1e-12)
                self.assertAlmostEqual(float(bary.sum()), 1.)
                self.assertGreaterEqual(float(bary.min()), -1e-12)

    def test_degenerate_triangles_and_rigid_transform_covariance(self):
        for triangle, query, expected in [([[0.,0,0],[2,0,0],[4,0,0]], [1.5,3,0], [1.5,0,0]), ([[1.,1,1]]*3,[4,5,6],[1,1,1])]:
            point, face, bary = s.closest_triangle_point(np.array([triangle]), np.array(query))
            np.testing.assert_allclose(point, expected, atol=1e-12)
            self.assertTrue(np.isfinite(bary).all())
        triangle = np.array([[[0.,0,0],[4,0,0],[0,4,0]]]); query = np.array([3.,3,2])
        rot = Rotation.from_euler('xyz', [23,-41,72], degrees=True).as_matrix(); offset = np.array([11.,-7,19])
        before, _, weights = s.closest_triangle_point(triangle,query)
        after, _, transformed_weights = s.closest_triangle_point(triangle@rot.T+offset,query@rot.T+offset)
        np.testing.assert_allclose(after,before@rot.T+offset,atol=1e-11)
        np.testing.assert_allclose(transformed_weights,weights,atol=1e-11)

    def test_real_runtime_strings_keep_every_corner_and_contact_position(self):
        for string in self.guitar['strings']:
            line = np.array(string['controlPointsMm']); samples = s.sample_polyline(line, step=2.5)
            self.assertGreater(string['radiusMm'],0)
            self.assertLessEqual(float(np.linalg.norm(np.diff(samples,axis=0),axis=1).max()),2.5+1e-10)
            for corner in line:
                self.assertLess(float(np.linalg.norm(samples-corner,axis=1).min()),1e-10)
                np.testing.assert_allclose(s.line_point(line,corner[0]),corner,atol=1e-10)
            for start,end in zip(line[:-1],line[1:]):
                np.testing.assert_allclose(s.line_point(line,(start[0]+end[0])/2),(start+end)/2,atol=1e-10)
            self.assertLess(float(s.m.polyline_distance(samples,line).max()),1e-10)
        with self.assertRaises(ValueError):
            line = np.array(self.guitar['strings'][0]['controlPointsMm'])
            s.line_point(line,float(line[:,0].min())-1.)

    def test_nearest_contact_uses_original_owned_palmar_skin(self):
        seed = self.context['library']['poses']['C']; rig = self.rig
        points = rig.skin(s.a.world_from_pose(rig,seed)); faces = self.context['faces']['index','tip']
        string = next(v for v in self.guitar['strings'] if v['number']==2)
        query = s.line_point(np.array(string['controlPointsMm']),s.m.fret_x(1)-4)+[0,string['radiusMm'],0]
        point, face, bary = s.closest_triangle_point(points[faces],query)
        np.testing.assert_allclose(bary@points[faces[face]],point,atol=1e-10)
        self.assertGreaterEqual(float(bary.min()),-1e-12)
        self.assertAlmostEqual(float(bary.sum()),1.)
        self.assertLessEqual(float(np.linalg.norm(point-query)),float(np.linalg.norm(points[faces].reshape(-1,3)-query,axis=1).min())+1e-10)
        distal = rig.by_name['finger2-3.L']
        self.assertIn(distal,self.context['dominant'][faces[face]])

    def test_seven_actual_22_bone_seed_frames_and_weighted_skin_are_reproduced(self):
        rig = self.rig
        for key in sorted(self.context['accepted']):
            with self.subTest(chord=key):
                seed = self.context['library']['poses'][key]; pose = copy.deepcopy(seed)
                angles = s.seed_angles(rig,seed)
                for finger in s.m.FINGERS:
                    flex,spread,pip,dip,twist = angles[finger]
                    for segment,angle in enumerate([flex,pip,dip],1):
                        name = f'finger{s.m.NUMBERS[finger]}-{segment}.L'; index = rig.by_name[name]
                        delta = Rotation.from_rotvec(rig.flex_axes[name]*angle)
                        if segment==1:
                            delta = Rotation.from_rotvec(rig.spread_axes[name]*spread)*delta*Rotation.from_rotvec(np.array([0.,1.,0.])*twist)
                        q = (Rotation.from_quat(rig.rest_q[index])*delta).as_quat()
                        self.assertAlmostEqual(abs(float(q @ np.array(seed['bones'][name]['quaternion']))),1.,places=11)
                        pose['bones'][name]['quaternion'] = q.tolist()
                self.assertEqual(pose['root'],seed['root']); self.assertEqual(len(pose['bones']),22)
                before = s.a.world_from_pose(rig,seed); after = s.a.world_from_pose(rig,pose)
                np.testing.assert_allclose(after,before,atol=1e-6,rtol=0)
                np.testing.assert_allclose(rig.skin(after),rig.skin(before),atol=1e-6,rtol=0)

    def test_all_42_contact_topologies_keep_real_strings_frets_fingers_and_barres(self):
        self.assertEqual(len(self.context['chords']),42)
        for chord in self.context['chords'].values():
            contacts = s.gate.contacts(chord)
            tuples = [(c['finger'],c['string'],c['fret'],c['kind'])for c in contacts]
            self.assertEqual(len(tuples),len(set(tuples)),chord['id'])
            for i,fret in enumerate(chord['frets']):
                if fret:
                    self.assertTrue(any(c['string']==6-i and c['fret']==fret and c['finger']==chord['fingers'][i] for c in contacts),chord['id'])
            for barre in chord['barres']:
                actual = {c['string']for c in contacts if c['finger']==barre['finger'] and c['fret']==barre['fret'] and c['kind']=='barre'}
                self.assertEqual(actual,set(range(barre['toString'],barre['fromString']+1)),chord['id'])
            self.assertTrue(all(1<=c['string']<=6 and 1<=c['finger']<=4 and c['fret']>0 for c in contacts))
        self.assertEqual({(c['finger'],c['string'],c['fret']) for c in s.gate.contacts(self.context['chords']['C'])},{(1,2,1),(2,4,2),(3,5,3)})
        self.assertEqual({(c['finger'],c['string'],c['fret']) for c in s.gate.contacts(self.context['chords']['D'])},{(1,3,2),(2,1,2),(3,2,3)})
        f = s.gate.contacts(self.context['chords']['F'])
        self.assertEqual({c['string']for c in f if c['kind']=='barre'},set(range(1,7)))
        self.assertTrue({(3,5,3),(4,4,3),(2,3,2)}<={(c['finger'],c['string'],c['fret'])for c in f})

    def test_all_42_seed_choices_are_deterministic_copies_of_audited_geometry(self):
        alternate = dict(self.context,accepted=list(reversed(sorted(self.context['accepted']))))
        for chord in self.context['chords'].values():
            first,key = s.choose_seed(self.context,chord); second,other = s.choose_seed(alternate,chord)
            self.assertEqual(key,other); self.assertIn(key,self.context['accepted'])
            self.assertEqual(s.transform_hash(first),s.transform_hash(second))
            if chord['id']in self.context['accepted']:
                self.assertEqual(key,chord['id'])
                self.assertEqual(s.transform_hash(first),s.transform_hash(self.context['library']['poses'][key]))
            original = s.transform_hash(self.context['library']['poses'][key])
            first['root']['positionMm'][0]+=100
            self.assertEqual(s.transform_hash(self.context['library']['poses'][key]),original)


    def test_dsus2_releases_former_dm_middle_without_freeing_every_unused_digit(self):
        chord = self.context['chords']['Dsus2']; seed = self.context['library']['poses']['Dm']
        before = s.transform_hash(seed); guitar = s.runtime_guitar(chord,self.temporary.name)
        active,released,reasons = s.controlled_digits(self.context,chord,seed,guitar)
        self.assertEqual(active,['index','ring'])
        self.assertEqual(released,['middle'])
        self.assertIn('formerly-fretted-in-seed',reasons['middle'])
        self.assertNotIn('little',released); self.assertNotIn('thumb',released)
        # Real Dm middle occupies G2, which Dsus2 now assigns to the index.
        # Keeping that old middle chain frozen would obstruct the new owner.
        rig = self.rig; points = rig.skin(s.a.world_from_pose(rig,seed))
        string = next(v for v in guitar['strings']if v['number']==3)
        wire = s.m.fret_x(2)
        segments = s.gate.clip_line(np.array(string['controlPointsMm']),wire-6,wire-1.1)
        gap = s.gate.clearance(points[self.context['faces']['middle','tip']],segments,string['radiusMm'])
        self.assertGreaterEqual(gap,0); self.assertLessEqual(gap,.12)
        self.assertEqual(s.transform_hash(seed),before)

    def test_em7_releases_original_c_index_and_ring_and_keeps_clear_little_fixed(self):
        chord = self.context['chords']['Em7']; seed = self.context['library']['poses']['C']
        before = s.transform_hash(seed); guitar = s.runtime_guitar(chord,self.temporary.name)
        active,released,reasons = s.controlled_digits(self.context,chord,seed,guitar)
        self.assertEqual(active,['middle'])
        self.assertEqual(released,['index','ring'])
        self.assertNotIn('little',released)
        self.assertIn('formerly-fretted-in-seed',reasons['index'])
        self.assertIn('formerly-fretted-in-seed',reasons['ring'])
        # C's actual index still intersects the B path that Em7 requires open.
        rig = self.rig; points = rig.skin(s.a.world_from_pose(rig,seed))
        string = next(v for v in guitar['strings']if v['number']==2)
        line = np.array(string['controlPointsMm'])
        gap = s.gate.clearance(points[rig.finger_triangles['index']],list(zip(line[:-1],line[1:])),string['radiusMm'])
        self.assertLess(gap,0)
        blockers = [v for v in reasons['index']if isinstance(v,dict)]
        self.assertTrue(any(v['initialOpenString']==2 and v['actualFingerSurfaceClearanceMm']<0 for v in blockers))
        self.assertEqual(s.transform_hash(seed),before)


if __name__=='__main__':
    unittest.main(verbosity=2)
