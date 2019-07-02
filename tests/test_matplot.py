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

        argv = [
            "--debug",
            "--read-pickle", picklefile,
            "--subplot", "111@ax",
            "--plot", "_{data[0]:arg}_.dimensions@plot",
        ]

        retval, forward = pyloco.perform(matplot, argv)

        self.assertEqual(retval, 0)
        #self.assertIn("data", forward)
        #self.assertEqual(forward["data"], ['lat', 'lon', 'bnds', 'plev', 'time'])

test_classes = (TaskMatplotTests,)
