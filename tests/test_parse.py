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
          integer Y, Z

          Y = 1
          Z = X
          print *, "%s"
          print *, " X = ", X
          print *, " Y = ", Y
          print *, " Z = ", Z
       end program hello
""" % greeting

srcname = "helloworld"
srcfile = srcname + ".f90"
outfile = srcname + ".exe"

class TaskFortParseTests(pyloco.TestCase):

    def __init__(self, *vargs, **kwargs):

        super(TaskFortParseTests, self).__init__(*vargs, **kwargs)

        self.tempdir = tempfile.mkdtemp()
        self.srcpath = os.path.join(self.tempdir, srcfile)
        self.outpath = os.path.join(self.tempdir, outfile)

        with open(self.srcpath, "w") as fsrc:
            fsrc.write(helloworld_f)

        with langlab.workdir(self.tempdir) as cwd:

            argv = [
                self.srcpath,
                "--fpp",
                "-I", self.tempdir,
                "-D", "X=1",
            ]

            ret, fwd = fortlab.perform("parse", argv=argv)

            self.assertEqual(ret, 0)
            self.assertIsInstance(fwd["ast"], langlab.Tree)

            self.ast = fwd["ast"]

        self.command = ("%s -o %s %s -D X=1" %
                        ("gfortran", self.outpath, self.srcpath))

    def setUp(self):

        pass

    def tearDown(self):

        pass

    def ttest_build_ast(self):

        #self.ast.show()
        root, ext = os.path.splitext(self.srcpath)
        path = root + ".ast" + ext 

        with open(path, "w") as f:
            f.write(self.ast.tosource())

        ret, fwd = fortlab.perform("parse", forward={"path": path})

        os.remove(path)

        self.assertEqual(ret, 0)
        self.assertIsInstance(fwd["ast"], langlab.Tree)

        ast = fwd["ast"]
        self.assertEqual(self.ast, ast)

    def ttest_trace(self):

        tracefile = os.path.join(self.tempdir, "trace.log")

        argv = [
            self.command,
            tracefile,
        ]

        ret, fwd = fortlab.perform("compiler", argv=argv)
        self.assertEqual(ret, 0)
        self.assertIn(self.srcpath, fwd["data"].sections())

    def ttest_referer(self):

        argv = [
            "--debug"
        ]

        forward = {
            "tree": self.ast,
            "node": self.ast[self.ast.root],
        }

        ret, fwd = fortlab.perform("referer", argv=argv, forward=forward)
        self.assertEqual(ret, 0)
        self.assertIn("ids", fwd)
        for name in fwd["ids"]:
            self.assertIn(name.data["name"], ("Y", "Z"))

    def test_resolve(self):

        argv = [
            "--debug"
        ]

        forward = {
            "tree": self.ast,
            "node": self.ast[self.ast.root],
        }

        ret, fwd = fortlab.perform("referer", argv=argv, forward=forward)
        self.assertEqual(ret, 0)
        self.assertIn("ids", fwd)
        for name in fwd["ids"]:
            self.assertIn(name.data["name"], ("Y", "Z"))

    def __del__(self):

        shutil.rmtree(self.tempdir)

test_classes = (TaskFortParseTests,)
