import unittest

import skimage.io as io
from skimage.transform import resize
import os
import sys
import kdtree as kd
import numpy as np

class testKDTree(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_build_tree(self):
        
        tree = kd.KDTree([[0,10],[4,8],[-5,5]], max_leaf_size=1)
        tree.bulk_insert(np.array([[5,4,3,"foo"],[0,6,-2,"bar"]]))
        key,content = tree.get_neighbours(np.array([5,4,3]))
        self.assertEqual(content,"foo")
        key,content = tree.get_neighbours(np.array([0,6,-2]))
        self.assertEqual(content,"bar")
        key,content = tree.get_neighbours(np.array([0,6,-5]))
        self.assertEqual(content,"bar")
        #import ipdb; ipdb.set_trace()
        # self.assertFalse(os.path.exists('a'))
        # self.assertTrue(os.path.exists('a'))
        # self.assertTrue('already a backup server' in c.stderr)
        # self.assertIn('fun', 'disfunctional')
        # self.assertNotIn('crazy', 'disfunctional')
        # with self.assertRaises(Exception):
        #       raise Exception('test')
        #
        # Unconditionally fail, for example in a try block that should raise
        # self.fail('Exception was not raised')
