# -*- coding: utf-8 -*-

import pyloco
import numpy


class Plotter(object):

    def get_variable(self, group, indata, outdata, parent_group):

        import pdb; pdb.set_trace()

#    def get_variable(self, data, varpath):
#
#        variables = None
#        
#        for item in varpath.split("/"):
#            if variables is None:
#                variables = data
#            else:
#                variables = variables["groups"][item]["variables"]
#
#        return variables[item] if variables else None

    def guess_dim(self, data, idim):

        index = 0

        for dimname, dim in data["dimensions"]:
            if len(dim['data']) <= 1:
                continue

            if index == idim:
                return dimname, dim

            index += 1

        
    def get_dim(self, data, name):

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

    def traverse(self, group, indata, outdata, parent_group=None,
                 F1=None, F2=None, F3=None, F4=None):

        if F1: F1(group, indata, outdata, parent_group)

        import pdb; pdb.set_trace()
        for g in group.groups.items():
            d = F2(g, indata, outdata, group) if F2 else outdata
            self.traverse(g, indata, d, parent_group=group)
            if F3: F3(g, indata, d, group)

        if F4: F4(group, indata, outdata, parent_group)

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

    def get_variable(self, data, varpath):

        variables = None
        
        for item in varpath.split("/"):
            if variables is None:
                variables = data
            else:
                variables = variables["groups"][item]["variables"]

        return variables[item] if variables else None
    

    @staticmethod
    def plot_contour(plotter, data, opt):

        lv = len(opt.vargs)

        if lv == 0:
            print("Contour plot syntax error: Not enough argument.")
            return -1

        elif lv <= 2:
            zname = opt.vargs.pop(0)
            yname = None
            xname = None

        elif lv > 2:
            zname = opt.vargs.pop(2)
            yname = opt.vargs.pop(1)
            xname = opt.vargs.pop(0)


        indata, outdata = {"name": zname}, {}
        Z = self.traverse(data, indata, outdata, F1=self._get_variable, F2=None, F3=None, F4=None)

        Y = plotter.get_ydim(Z, yname)
        X = plotter.get_xdim(Z, xname)

        #if not yname:


#        forward = {"data": self.split_data(data, "XYD")}
#
#        params = ", " + params if params else ""
#        plot_arg = ("_{data[0]:arg}_, _{data[1]:arg}_,"
#                    "_{data[2]:arg}_%s@contour" % params)
#
#        argv = [
#            "-p", plot_arg,
#        ]
#
#        pyloco.perform("matplot", argv=argv, forward=forward)


    def split_data(self, data, datatypes):

        outdata = []
        dimensions = data["dimensions"]
        import pdb; pdb.set_trace()

        for datatype in datatypes:
            if datatype == "X":
                import pdb; pdb.set_trace()
            elif datatype == "Y":
                import pdb; pdb.set_trace()
            elif datatype == "Z":
                import pdb; pdb.set_trace()
            elif datatype == "T":
                import pdb; pdb.set_trace()
            elif datatype == "D":
                import pdb; pdb.set_trace()
            else:
                raise Exception("Unknown datatype: %s" % datatype)

            outdata.append(output)

        return outdata
