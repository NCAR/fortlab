"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import unittest

import pyloco

here, myname = os.path.split(__file__)
datadir = os.path.join(here, "data")
rootdir = os.path.realpath(os.path.join(here, ".."))

class TaskMatplotTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pickle(self):

        matplot = os.path.join(rootdir, "fortlab", "plot", "matplot.py")
        picklefile = os.path.join(datadir, "netcdfread.ppf")
        imgfile = os.path.join(datadir, "img.png")

        argv = [
            "--debug",
            "--read-pickle", picklefile,
            "--subplot", "111@ax",
            "--noshow",
            "--save", imgfile,
            "--plot", "_{data[0]:arg}_['variables']['lat']['data']@plot",
        ]

        retval, forward = pyloco.perform(matplot, argv)

        self.assertEqual(retval, 0)
        self.assertTrue(os.path.exists(imgfile))
        os.remove(imgfile)
        #self.assertIn("data", forward)
        #self.assertEqual(forward["data"], ['lat', 'lon', 'bnds', 'plev', 'time'])

test_classes = (TaskMatplotTests,)
