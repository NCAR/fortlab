# -*- coding: utf-8 -*-

import os

import fparser.common.readfortran
import fparser.two.parser
#import fparser.two.Fortran2003
#import fparser.two.utils

from pyloco import Task
from pcpp.cmd import CmdPreprocessor

class Parse(Task):
    "parse Fortran source code"

    _name_ = "parse"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("path", type=str, required=True, help="input source file")
        self.add_option_argument("-I", "--include", action="append", metavar="path",
                help="Path to search for unfound #include's")
        self.add_option_argument("--fpp", action="store_true", help="run preprocessor")

        self.register_forward("ast", type=str, help="output abstract syntax tree")

        self.parse_known_args = True

    def perform(self, targs):

        assert os.path.isfile(targs.path), "'%s' does not exist." % targs.path

        root, ext = os.path.splitext(targs.path)
        prepfile = root + ".prep" + ext

        # preprocess
        if targs.fpp or (ext and ext.startswith(".F")):
            includes = []
            for inc in targs.include:
                includes.append("-I")
                includes.append(inc)

            prep = CmdPreprocessor(["dummy", targs.path, "-o", prepfile, "--line-directive"] + includes + self.unknown_args)
            prep.args.output.flush()

        else:
            prepfile = targs.path
                        
        # parse
        reader = fparser.common.readfortran.FortranFileReader(prepfile, ignore_comments=False)
        reader.id = targs.path
        tree = fparser.two.parser.ParserFactory().create(std="f2008")(reader)

        self.add_forward(ast=tree)
