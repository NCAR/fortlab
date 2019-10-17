# -*- coding: utf-8 -*-

import os
import inspect

import fparser.common.readfortran
import fparser.two.parser
import fparser.two.Fortran2003
import fparser.two.Fortran2008
import fparser.two.utils

from pyloco import Task
from pcpp.cmd import CmdPreprocessor
from langlab import toast, Tree, Proxy, Node

class Parse(Task):
    "parse Fortran source code"

    _name_ = "parse"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("path", type=str, required=True, help="input source file")
        self.add_option_argument("-I", "--include", action="append", metavar="path",
                help="Path to search for unfound #include's")
        self.add_option_argument("--fpp", action="store_true", help="run preprocessor")

        self.register_forward("ast", type=Tree, help="output abstract syntax tree")

        self.parse_known_args = True

    def perform(self, targs):

        assert os.path.isfile(targs.path), "'%s' does not exist." % targs.path

        root, ext = os.path.splitext(targs.path)
        prepfile = root + ".prep" + ext

        # preprocess
        if targs.fpp or (ext and ext.startswith(".F")):
            includes = []
            if targs.include:
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
        ast = toast(tree, FortProxy())

        self.add_forward(ast=ast)

def _node_attr(node):
    return {
        "node": node,
        "string": node
        }

def _Name_attr(node):
    return {
        "name": node.string,
        "string": node.string
        }

def _default_attr(node):

    if hasattr(node, "tofortran"):
        if isinstance(node, fparser.two.utils.BlockBase):
            #import pdb; pdb.set_trace()
            return {"string": ""}

        else:
            return {"string": node.tofortran()}

    else:
        return {"string": str(node)}

def _debug(node):
    import pdb; pdb.set_trace()
    return {}


data_attrs = {
    "str": _node_attr,
    "Name": _Name_attr,
}

class FortProxy(Proxy):

    def get_rootnode(self, tree):
        return tree

    def get_nodename(self, node):
        return node.__class__.__name__

    def get_nodeid(self, node):
        return id(node)

    def get_nodedata(self, node, data):

        name = node.__class__.__name__

        if name in data_attrs:
            attrs = data_attrs[name]
            if callable(attrs):
                data.update(attrs(node))

            else:
                for attr in attrs:
                    data[attr] = getattr(node, attr, None)
        else:
            data.update(_default_attr(node))
 
    def get_subnodes(self, node):

        if hasattr(node, "content"):
            return list(node.content)

        elif hasattr(node, "items"):
            return list(node.items)
#            subnodes = []
#
#            for i in node.items:
#                if isinstance(i, fparser.two.utils.Base):
#                    subnodes.append(i)
#                else:
#                    subnodes.append(Item(i))
#
#            return subnodes

        else:
            return []

    def get_source(self, node):

        #import pdb; pdb.set_trace()
        return node["string"]
        #return node.tofortran()

    def is_equivalent(self, n1, n2):

        return n1 == n2

#
#all_nodes = {}
#
#
#for key in dir(fparser.two.utils):
#    obj = getattr(fparser.two.utils, key)
#    if (inspect.isclass(obj) and issubclass(obj, fparser.two.utils.Base) and
#        obj is not fparser.two.utils.Base):
#        lenv = {}
#        exec("class %s(Node):\n    pass" % key, None, lenv)
#        all_nodes[key] = lenv[key]
#
#for key in dir(fparser.two.Fortran2003):
#    obj = getattr(fparser.two.Fortran2003, key)
#    if inspect.isclass(obj) and issubclass(obj, fparser.two.utils.Base):
#        lenv = {}
#        exec("class %s(Node):\n    pass" % key, None, lenv)
#        all_nodes[key] = lenv[key]
#
#for key in dir(fparser.two.Fortran2008):
#    obj = getattr(fparser.two.Fortran2008, key)
#    if inspect.isclass(obj) and issubclass(obj, fparser.two.utils.Base):
#        lenv = {}
#        exec("class %s(Node):\n    pass" % key, None, lenv)
#        all_nodes[key] = lenv[key]
