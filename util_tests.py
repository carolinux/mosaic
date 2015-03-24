import unittest

import skimage.io as io
from skimage.transform import resize
import os
import sys
from util import *

class testUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_divide_and_reassemble(self):
        pic = io.imread("./kitteh.jpg")
        pic = resize(pic, (500,500), mode='nearest')
        print "size "+str(pic.shape)
        for shape in [(10,10),(10,20),(30,30),(33,48)]:
            print shape
            parts = divide_into_parts(pic,*shape)
            pic2 = assemble_from_parts(parts)
            self.assertTrue((pic==pic2).all())
        
        #  Examples:
        # self.assertEqual(fp.readline(), 'This is a test')
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
