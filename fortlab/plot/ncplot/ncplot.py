# -*- coding: utf-8 -*-

import pyloco
import numpy
from nctools_util import normpath, traverse, get_var, get_dim, get_slice_from_dims

# TODO: use eval in the beginning
# - add first name as a Var Dim or Group proxy

class ProxyBase(object):

    def __new__(cls, data):

        obj = super(ProxyBase, cls).__new__(cls)
        obj._data = data
        return obj

    def __getattr__(self, attr):

        if attr in self._data:
            return self._data[attr]

        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self.__class__.__name__, attr))


class VarProxy(ProxyBase):
    pass


class DimProxy(ProxyBase):
    pass


class GroupProxy(ProxyBase):

    def __getattr__(self, attr):

        if attr in self._data["vars"]:
            return VarProxy(self._data["vars"][attr])

        elif attr in self._data["dims"]:
            return DimProxy(self._data["dims"][attr])

        elif attr in self._data and attr not in ("vars", "dims", "groups"):
            return self._data[attr]

        elif attr in self._data["groups"]:
            return GroupProxy(self._data["groups"][attr])

        else:
            raise AttributeError("'GroupProxy' object has no attribute '%s'" % attr)

#class Plotter(object):
#
#    def guess_dim(self, data, idim):
#
#        index = 0
#
#        import pdb; pdb.set_trace()
#        for dimname in data["dimensions"]:
#            if len(dim['data']) <= 1:
#                continue
#
#            if index == idim:
#                return dimname, dim
#
#            index += 1
#
#        
#    def get_dim(self, data, name):
#
#        import pdb; pdb.set_trace()
#        for dimname, dim in data["dimensions"]:
#            if dimname == name:
#                return dimname, dim
#
#    def _get_dim(self, data, name, idx):
#
#        if name is None:
#            return self.guess_dim(data, idx)
#        else:
#            return self.get_dim(data, name)
#
#    def get_xdim(self, data, name):
#
#        return self._get_dim(data, name, 0)
#
#    def get_ydim(self, data, name):
#
#        return self._get_dim(data, name, 1)
#
#    def get_zdim(self, data, name):
#
#        return self._get_dim(data, name, 2)
#
#    def get_tdim(self, data, name):
#
#        return self._get_dim(data, name, 3)

#class NCPlot(pyloco.Task):
class NCPlot(pyloco.taskclass("matplot")):
#class NCPlot(pyloco.taskclass("/home/youngsung/data/repos/github/fortlab/fortlab/plot/matplot/matplot.py")):
    """Read a NCD data and generate plot(s)

'ncplot' task reads a NCD data and generates plots.

Examples
---------
"""
    _name_ = "ncplot"
    _version_ = "0.1.0"
    _install_requires = ["matplot", "numpy"]

    def __init__(self, parent):

        super(NCPlot, self).__init__(parent)

        self.set_data_argument("data", required=True, help="NCD data")

        #self.add_option_argument("-t", "--title", help="plot title")
        #self.add_option_argument("-p", "--plot", type=str, action="append",
        #        help="plot configuration", metavar="plot", param_parse=True)
        #self.add_option_argument("-s", "--save-image", type=str,
        #        help="save image file", metavar="path")
        #self.register_forward("data", help="T.B.D.")

    def pre_perform(self, targs):

        for k, g in targs.data["groups"].items():
            self._env[k] = GroupProxy(g)

        for k, a in targs.data.items():
            if k not in ("vars", "dims", "groups"):
                self._env[k] = a

        for k, d in targs.data["dims"].items():
            self._env[k] = DimProxy(d)

        for k, v in targs.data["vars"].items():
            self._env[k] = VarProxy(v)

        super(NCPlot, self).pre_perform(targs)
    
    @staticmethod
    def _matplot(argv, forward, targs, data):

        env = dict(__builtins__)
        del env["eval"]
        del env["exec"]

        for k, g in data["groups"].items():
            env[k] = GroupProxy(g)

        for k, a in data.items():
            if k not in ("vars", "dims", "groups"):
                env[k] = a

        for k, d in data["dims"].items():
            env[k] = DimProxy(d)

        for k, v in data["vars"].items():
            env[k] = VarProxy(v)

        if targs.title:
            title = eval(targs.title, env)
            argv.extend(["-t", "'%s'" % title])

        if targs.save_image:
            argv.extend(["-s", "'%s'" % targs.save_image])

        #pyloco.perform("matplot", argv=argv, forward=forward)
        super(self.__class__, self).perform(targs)
        #pyloco.perform("matplot", argv=argv, forward=forward)

    @staticmethod
    def plot_contourf(plotter, opt, targs):
        return NCPlot.plot_contour(plotter, opt, targs, fill=True)

    @staticmethod
    def plot_contour(plotter, opt, targs, fill=False):

        data = targs.data

        lv = len(opt.vargs)

        if lv <= 2:
            zname = opt.vargs.pop(0)
            _Z = get_var(data, zname)
            xname, yname = _Z["dimensions"][-2:]
        else:
            zname = opt.vargs.pop(2)
            _Z = get_var(data, zname)
            yname = opt.vargs.pop(1)
            xname = opt.vargs.pop(0)

        Y = get_dim(data, yname)
        X = get_dim(data, xname)
        Z = get_slice_from_dims(_Z, (yname, xname))

        # "X,Y,Z"
        plotfunc = "contourf" if fill else "contour"
        plotter.update_env(X=X["variable"]["data"], Y=Y["variable"]["data"], Z=Z)
        newopt = pyloco.Option("X", "Y", "Z", context=([plotfunc] + opt.context[1:]))
        targs.plot.append(newopt)
