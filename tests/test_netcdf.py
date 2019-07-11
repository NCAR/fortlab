"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import unittest

import pyloco

here, myname = os.path.split(__file__)
datadir = os.path.join(here, "data")
rootdir = os.path.realpath(os.path.join(here, ".."))
ncread = os.path.join(rootdir, "fortlab", "data", "ncread.py")
nctoolsutil = os.path.join(rootdir, "fortlab", "core", "nctools_util.py")
datafile = os.path.join(datadir, "sresa1b_ncar_ccsm3-example.nc")

class TaskNetcdfTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read(self):


        # data source : https://www.unidata.ucar.edu/software/netcdf/examples/sresa1b_ncar_ccsm3-example.nc
        #datafile = os.path.join(datadir, "sresa1b_ncar_ccsm3-example.nc")
        #datafile = os.path.join(rootdir, "..", "pyloco_task_netcdfread", "cesm1.nc")

        argv = [datafile, "-v", "/pr", "--import", nctoolsutil]

        retval, forward = pyloco.perform(ncread, argv)

        self.assertEqual(retval, 0)
        self.assertIn("data", forward)
        self.assertIn("dims", forward["data"])
        self.assertIn("vars", forward["data"])
        self.assertIn("groups", forward["data"])


    def test_pickle(self):

        # data source : https://www.unidata.ucar.edu/software/netcdf/examples/sresa1b_ncar_ccsm3-example.nc
        picklefile = os.path.join(datadir, "test.ppf")

        argv = [datafile, "--write-pickle", picklefile, "-v", "/pr", "--import", nctoolsutil]

        retval, forward = pyloco.perform(ncread, argv)

        self.assertEqual(retval, 0)
        self.assertIn("data", forward)
        self.assertIn("dims", forward["data"])
        self.assertIn("vars", forward["data"])
        self.assertIn("groups", forward["data"])

        argv = ["--read-pickle", picklefile, "--forward", "data=list(_{data[0]:arg}_['dims'].keys())"]
        retval, forward = pyloco.perform("input", argv)

        self.assertEqual(retval, 0)
        self.assertIn("data", forward)
        self.assertEqual(forward["data"], ['lat', 'lon', 'bnds', 'plev', 'time'])

test_classes = (TaskNetcdfTests,)
