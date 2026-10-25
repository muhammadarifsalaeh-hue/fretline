"""Analytical fixtures for the geometric contact audit, independent of a pose."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location('contacts', Path(__file__).with_name('refine_c_contacts.py'))
contacts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contacts)

class ContactDistanceFixtures(unittest.TestCase):
    def setUp(self):
        self.triangle = np.array([[[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]]])

    def distance(self, a, b):
        return contacts.segment_triangle_distances(self.triangle, np.array(a, dtype=float), np.array(b, dtype=float))[0]

    def test_crosses_face_interior(self):
        self.assertAlmostEqual(self.distance([.2, .2, -1], [.2, .2, 1]), 0.)

    def test_parallel_above_face(self):
        self.assertAlmostEqual(self.distance([.1, .1, .5], [.4, .1, .5]), .5)

    def test_nearest_vertex(self):
        self.assertAlmostEqual(self.distance([2, 0, 0], [3, 0, 0]), 1.)

    def test_diagonal_to_vertex(self):
        self.assertAlmostEqual(self.distance([-1, 0, 1], [-1, 0, 2]), np.sqrt(2))

    def test_nearest_triangle_edge(self):
        self.assertAlmostEqual(self.distance([.5, .6, .4], [.5, .8, .4]), np.sqrt(.4**2 + .1**2 / 2))

    def test_segment_endpoint_projects_to_face(self):
        self.assertAlmostEqual(self.distance([.2, .2, .3], [.2, .2, 3]), .3)

    def test_shared_endpoint_is_contact(self):
        self.assertAlmostEqual(self.distance([0, 0, 0], [-1, -1, -1]), 0.)

    def test_winding_does_not_change_distance(self):
        expected = self.distance([.3, .4, 1], [.6, .7, 1])
        self.triangle = self.triangle[:, ::-1]
        self.assertAlmostEqual(self.distance([.3, .4, 1], [.6, .7, 1]), expected)

    def test_joint_rigid_transform_preserves_distance(self):
        a, b = np.array([.1, .1, .5]), np.array([.4, .1, .5])
        expected = self.distance(a, b)
        rotation = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
        offset = np.array([9., -8., 3.])
        self.triangle = self.triangle @ rotation.T + offset
        self.assertAlmostEqual(self.distance(a @ rotation.T + offset, b @ rotation.T + offset), expected)

if __name__ == '__main__':
    unittest.main()
