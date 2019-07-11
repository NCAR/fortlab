"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import unittest

import pyloco

here, myname = os.path.split(__file__)
datadir = os.path.join(here, "data")
rootdir = os.path.realpath(os.path.join(here, ".."))
ncplot = os.path.join(rootdir, "fortlab", "plot", "ncplot.py")
imgfile = os.path.join(datadir, "img.png")

ncread = os.path.join(rootdir, "fortlab", "data", "ncread.py")
nctoolsutil = os.path.join(rootdir, "fortlab", "core", "nctools_util.py")
datafile = os.path.join(datadir, "sresa1b_ncar_ccsm3-example.nc")

class TaskNcPlotTests(unittest.TestCase):

    def __init__(self, *vargs, **kwargs):

        super(TaskNcPlotTests, self).__init__(*vargs, **kwargs)

        self.ncplot_argv = [
            "--debug",
            "--save", "%s" % imgfile
        ]

    def setUp(self):

        if os.path.exists(imgfile):
            os.remove(imgfile)

    def tearDown(self):

        #import pdb; pdb.set_trace()
        if os.path.exists(imgfile):
            os.remove(imgfile)

    def _default_assert(self, retval):

        self.assertEqual(retval, 0)
        self.assertTrue(os.path.exists(imgfile))

    def test_contour(self):

        argv = [datafile, "-v", "/pr", "--import", nctoolsutil]

        retval, forward = pyloco.perform(ncread, argv)

        self.assertEqual(retval, 0)
        self.assertIn("data", forward)
        self.assertIn("dims", forward["data"])
        self.assertIn("vars", forward["data"])
        self.assertIn("groups", forward["data"])


        argv = self.ncplot_argv + [
            "-p", "lon,lat,pr@contour",
        ]

        forward = {
            "data": forward["data"]
        }

        retval, forward = pyloco.perform(ncplot, argv, forward=forward)

        self._default_assert(retval)

    def test_contour_rotate(self):

        argv = [datafile, "-v", "/pr", "--import", nctoolsutil]

        retval, forward = pyloco.perform(ncread, argv)

        self.assertEqual(retval, 0)
        self.assertIn("data", forward)
        self.assertIn("dims", forward["data"])
        self.assertIn("vars", forward["data"])
        self.assertIn("groups", forward["data"])


        argv = self.ncplot_argv + [
            "-p", "lat,lon,pr@contour",
        ]

        forward = {
            "data": forward["data"]
        }

        retval, forward = pyloco.perform(ncplot, argv, forward=forward)

        self._default_assert(retval)

#    def test_figure(self):
#
#        argv = self.argv + [
#            "--figure", "'test'@suptitle",
#        ]
#
#        retval, forward = pyloco.perform(matplot, argv)
#
#        self._default_assert(retval)
#
#    def test_title(self):
#
#        argv = self.argv + [
#            "--title", "'test'",
#            "--plot", "[3,1,2]",
#        ]
#
#        retval, forward = pyloco.perform(matplot, argv)
#
#        #import pdb; pdb.set_trace()
#        self._default_assert(retval)
#
#    def test_bar(self):
#
#        argv = self.argv + [
#            "--title", "'test'",
#            "--plot", "[0,1,2], [3,1,2]@bar",
#        ]
#
#        retval, forward = pyloco.perform(matplot, argv)
#
#        #import pdb; pdb.set_trace()
#        self._default_assert(retval)
#
#    def test_ticks(self):
#
#        argv = self.argv + [
#            "--title", "'test'",
#            "--plot", "[0,1,2], [3,1,2]@bar",
#            "--xaxis", "[0,1,2]@ticks",
#            "--xaxis", "['A', 'B', 'C']@ticklabels",
#        ]
#
#        retval, forward = pyloco.perform(matplot, argv)
#
#        #import pdb; pdb.set_trace()
#        self._default_assert(retval)
#
#    def test_clone(self):
#
#        argv = [
#            "--multiproc", "2",
#            "--clone", "[[1,2,3],[3,5,2]]"
#        ]
#
#        subargv = [matplot] + self.argv + [
#            "--save", "'%d.png'%_pathid_",
#        ]
#
#        retval, forward = pyloco.perform("", argv, subargv)
#
#        #import pdb; pdb.set_trace()
#        self.assertEqual(retval, 0)
#        self.assertTrue(os.path.exists("0.png"))
#        os.remove("0.png")
#        self.assertTrue(os.path.exists("1.png"))
#        os.remove("1.png")
#
#    def test_legend(self):
#
#        argv = self.argv + [
#            "--title", "'test'",
#            "--plot", "[0,1,2], label='PlotA'",
#            "--plot", "[3,1,2], label='PlotB'",
#            "-l",
#        ]
#
#        retval, forward = pyloco.perform(matplot, argv)
#
#        #import pdb; pdb.set_trace()
#        self._default_assert(retval)
#
#
#    def test_pickle(self):
#
#        picklefile = os.path.join(datadir, "netcdfread.ppf")
#
#        argv = self.argv + [
#            "--read-pickle", picklefile,
#            "--subplot", "111@ax",
#            "--plot", "_{data[0]:arg}_['variables']['lat']['data']@plot",
#        ]
#
#        retval, forward = pyloco.perform(matplot, argv)
#
#        self._default_assert(retval)
#
#        #self.assertIn("data", forward)
#        #self.assertEqual(forward["data"], ['lat', 'lon', 'bnds', 'plev', 'time'])


test_classes = (TaskNcPlotTests,)
