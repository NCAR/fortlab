# -*- coding: utf-8 -*-

import pyloco
import numpy
from nctools_util import normpath, traverse, get_var, get_dim, get_slice_from_dims

class Plotter(object):

    def guess_dim(self, data, idim):

        index = 0

        import pdb; pdb.set_trace()
        for dimname in data["dimensions"]:
            if len(dim['data']) <= 1:
                continue

            if index == idim:
                return dimname, dim

            index += 1

        
    def get_dim(self, data, name):

        import pdb; pdb.set_trace()
        for dimname, dim in data["dimensions"]:
            if dimname == name:
                return dimname, dim

    def _get_dim(self, data, name, idx):

        if name is None:
            return self.guess_dim(data, idx)
        else:
            return self.get_dim(data, name)

    def get_xdim(self, data, name):

        return self._get_dim(data, name, 0)

    def get_ydim(self, data, name):

        return self._get_dim(data, name, 1)

    def get_zdim(self, data, name):

        return self._get_dim(data, name, 2)

    def get_tdim(self, data, name):

        return self._get_dim(data, name, 3)

class NCPlot(pyloco.Task):
    """Read a NCD data and generate plot(s)

'ncplot' task reads a NCD data and generates plots.

Examples
---------
"""
    _name_ = "ncplot"
    _version_ = "0.1.0"
    _install_requires = ["matplot", "numpy"]

    def __init__(self, parent):


        self._cache = {}
        self._names = {}

        self.add_data_argument("data", required=True, help="NCD data")

        self.add_option_argument("-p", "--plot", type=str, action="append",
                help="plot configuration", metavar="plot", param_parse=True)

        self.register_forward("data",
                help="T.B.D.")

    def perform(self, targs):

        indata = targs.data

        if targs.plot:
            plotter = Plotter()

            for opt in targs.plot:
                if len(opt.context) == 0:
                    plot = self.plot_contour

                elif len(opt.context) ==1:
                    plot = getattr(self, "plot_"+opt.context[0])

                elif len(opt.context) ==2:
                    import pdb; pdb.set_trace()

                else:
                    print("More than two contexts: %s" % str(opt.context))
                    continue

                opt.context = []
                plot(plotter, indata, opt)
        else:
            print("No plot is specified.")
            return -1

        #self.add_forward(data=outdata)
    

    @staticmethod
    def plot_contour(plotter, data, opt):

        lv = len(opt.vargs)

        if lv <= 2:
            print("Contour plot syntax error: Not enough argument.")
            return -1

        else:
            zname = opt.vargs.pop(2)
            yname = opt.vargs.pop(1)
            xname = opt.vargs.pop(0)


        _Z = get_var(data, zname)
        Y = get_dim(data, yname)
        X = get_dim(data, xname)
        Z = get_slice_from_dims(_Z, (xname, yname))

        forward = {"data": [X["variable"]["data"], Y["variable"]["data"], Z]}

#        params = ", " + params if params else ""
        plot_arg = ("_{data[0]:arg}_, _{data[1]:arg}_,"
                    "_{data[2]:arg}_@contour")

        argv = [
            "-p", plot_arg,
        ]

        pyloco.perform("matplot", argv=argv, forward=forward)
