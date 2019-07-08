# -*- coding: utf-8 -*-

import pyloco
import numpy


class Plotter(object):

    def get_variable(self, data, varpath):

        variables = None
        
        for item in varpath.split("/"):
            if variables is None:
                variables = data
            else:
                variables = variables["groups"][item]["variables"]

        return variables[item] if variables else None

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

        self.add_option_argument("-l", "--list", action="store_true",
                help="list variables in a netcdf file")
        self.add_option_argument("-s", "--summary", action="store_true",
                help="variable information")

        self.register_forward("data",
                help="netcdf variables in Python dictionary")

    def _desc(self, names, data, verbose=False, namepath="/"):

        dimensions = data["dimensions"]
        variables = data["variables"]
        groups = data["groups"]

        for name in names:
            if name in dimensions:
                continue

            var = variables[name]

            long_name = var.get(self.aliases["name"], "no descriptive name is found")
            units = var.get(self.aliases["unit"], "unit-unknown")
            dims = var.get(self.aliases["dimension"], "dimension-unknown")
            print("{0}:\t{1} ({2}, {3})".format(name, long_name, units, dims))

            if verbose:
                for attr, value in var.items():
                    if attr in ("data", self.aliases["name"], self.aliases["unit"], self.aliases["dimension"]):
                        continue
                    print("    - {0}: {1}".format(attr, str(value)))
                print("")

        for gname, group in groups.items():
            newpath = "%s/%s" % (namepath, gname)
            print("\n[%s]" % newpath)
            self._desc(group["variables"].keys(), group, verbose=verbose, namepath=newpath)

    def perform(self, targs):

        indata = targs.data

        if targs.list:

            print("\n[root group]")
            self._desc(indata["variables"].keys(), indata) 

            return

        if targs.summary:

            if not targs.variable or any([v=="*" for v in targs.variable]):
                svars = indata["variables"].keys()

            else:
                svar = targs.variable

            for svar in svars:
                group = None
                name = None
                for item in svar.split("/"):
                    name = item
                    if group is None:
                        group = indata
                    else:
                        import pdb; pdb.set_trace()
                        group = group["groups"][item]
            
                if name and group:
                    self._desc([name], group, verbose=True) 

            return

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

        Z = plotter.get_variable(data, zname)
        Y = plotter.get_ydim(Z, yname)
        X = plotter.get_xdim(Z, xname)

        #if not yname:

        import pdb; pdb.set_trace()        

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
