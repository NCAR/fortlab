"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import pyloco
import tempfile
import shutil
import langlab
import fortlab

here, myname = os.path.split(__file__)

greeting = "Hello, World!"

helloworld_f = """! helloworld.c test program
       program hello
          print *, "%s"
       end program hello
""" % greeting

srcname = "helloworld"
srcfile = srcname + ".f90"
outfile = srcname + ".exe"

class TaskFortParseTests(pyloco.TestCase):

    def __init__(self, *vargs, **kwargs):

        super(TaskFortParseTests, self).__init__(*vargs, **kwargs)

        self.gfortran = langlab.which("gfortran")

    def setUp(self):

        assert self.gfortran is not None
        self.tempdir = tempfile.mkdtemp()
        self.srcpath = os.path.join(self.tempdir, srcfile)
        self.outpath = os.path.join(self.tempdir, outfile)

        with open(self.srcpath, "w") as fsrc:
            fsrc.write(helloworld_f)


    def tearDown(self):

        shutil.rmtree(self.tempdir)

    def test_shell_compile(self):

        with langlab.workdir(self.tempdir) as cwd:

            argv = [ "--cwd", self.tempdir]
            argv.append("%s -o %s %s" % (self.gfortran, self.outpath, self.srcpath))

            ret, fwd = langlab.perform("buildapp", argv=argv)
            self.assertEqual(ret, 0)
            self.assertEqual(fwd["stdout"], "")
            self.assertEqual(fwd["stderr"], "")

            argv = [ "--cwd", self.tempdir]
            argv.append(self.outpath)

            ret, fwd = langlab.perform("runapp", argv=argv)
            self.assertEqual(ret, 0)
            self.assertEqual(fwd["stdout"].strip(), greeting)
            self.assertEqual(fwd["stderr"], "")

            argv = [ "--cwd", self.tempdir]
            argv.append("rm -rf %s" % self.outpath)

            ret, fwd = langlab.perform("cleanapp", argv=argv)
            self.assertEqual(ret, 0)
            self.assertEqual(fwd["stdout"], "")
            self.assertEqual(fwd["stderr"], "")

            self.assertTrue(not os.path.isfile(self.outpath))

test_classes = (TaskFortParseTests,)
