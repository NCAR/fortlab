# -*- coding: utf-8 -*-

import pyloco
from nctools_util import GroupProxy, DimProxy, VarProxy


class NCPlot(pyloco.taskclass("matplot")):
#class NCPlot(pyloco.taskclass("/home/youngsung/data/repos/github/fortlab/fortlab/plot/matplot/matplot.py")):
    """Read a NCD data and generate plot(s)

'ncplot' task reads a NCD data and generates plots.

Examples
---------
"""
    _name_ = "ncplot"
    _version_ = "0.1.0"
    _install_requires = ["matplot"]

    def __init__(self, parent):

        super(NCPlot, self).__init__(parent)

        self.set_data_argument("data", required=True,
                help="data input in NetCDF-dictionary format")

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
    def plot_contourf(plotter, opt, targs):

        return NCPlot.plot_contour(plotter, opt, targs, fill=True)

    @staticmethod
    def plot_contour(plotter, opt, targs, fill=False):

        plotfunc = "contourf" if fill else "contour"
        opt.context[0] = plotfunc
        targs.plot.append(opt)
