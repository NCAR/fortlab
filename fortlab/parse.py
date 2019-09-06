# -*- coding: utf-8 -*-

from pyloco import Task
import pcpp

class Parse(Task):
    "parse Fortran source code"

    _name_ = "parse"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("path", type=str, required=True, help="input source file")

        self.add_option_argument("-D", "--macro", nargs="*", type=dict,
                param_parse=True, help="Fortran macro definition.")

        # TODO: need to test if nargs works with list type
        self.add_option_argument("-I", "--include", nargs="*", type=list,
                param_parse=True, help="Fortran source include paths.")
        self.add_option_argument("-a", "--alias", metavar="alias", type=dict,
                param_parse=True, nargs="*", help="path alias.")
        self.add_option_argument("--fpp", action="store_true", help="run preprocessor")

        self.register_forward("ast", type=str, help="output abstract syntax tree")

    def perform(self, targs):

        assert os.path.isfile(targs.path), "'%s' does not exist." % targs.path

        # collect macros
        if targs.macro:
            import pdb; pdb.set_trace()

        # collect includes
        if targs.include:
            import pdb; pdb.set_trace()

        # handle alias
        if targs.alias:
            import pdb; pdb.set_trace()

        root, ext = os.path.splitext(targs.path)

        # preprocess
        if targs.fpp or (ext and ext.startswith(".F")):
            import pdb; pbd.set_trace()

        else:

        # parse

        self.add_forward(ast=tree)
