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
          print *, " X = ", X
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

    def setUp(self):

        pass

    def tearDown(self):

        pass

    def test_build_ast(self):

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

    def __del__(self):

        shutil.rmtree(self.tempdir)

test_classes = (TaskFortParseTests,)
