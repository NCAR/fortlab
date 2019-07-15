# -*- coding: utf-8 -*-

import pyloco
#import numpy
#import matplotlib
#import matplotlib.pyplot as pyplot


class WeatherPlot(pyloco.Task):
    """weather plotting task


Examples
---------
"""
    _name_ = "weatherplot"
    _version_ = "0.1.0"
    _install_requires_ = "matplot"

    def __init__(self, parent):

        self.plotname = "contour"
        self.timename = "time"
        self.latname = "lat"
        self.lonname = "lon"
        self.vertname = "plev"

        self.add_data_argument("data", help="data input")

        self.add_option_argument("-p", "--plot", default=self.plotname,
                help="plot type(default=%s)" % self.plotname)
        self.add_option_argument("-s", "--summary", action="store_true", help="data summary")
        self.add_option_argument("-n", "--name", param_parse=True, help="list of variable names")
        self.add_option_argument("-t", "--time", param_parse=True, help="time range(default=start time)")
        self.add_option_argument("-l", "--latitude", param_parse=True, help="latitude range")
        self.add_option_argument("-o", "--longitude", param_parse=True, help="longitude range")
        self.add_option_argument("-a", "--altitude", param_parse=True, help="vertical levels(default=first level)")

        self.add_option_argument("-d", "--dimension-name", param_parse=True,
            help="variable name for dimension(default=(time=%s, lat=%s, lon=%s, vert=%s))" %
            (self.timename, self.latname, self.lonname, self.vertname)
        )

#    def _eval(self, opt):
#
#        for i in range(len(opt.vargs)):
#            opt.vargs[i] = eval(opt.vargs[i], self._env) 
#
#        for k, v in opt.kwargs.items():
#            opt.kwargs[k] = eval(v, self._env) 

    def perform(self, targs):

        indata = []

        variables = None
        # select variables
        if targs.name:
            variables = []
            for v in targs.name:
                variables.extend(v.vargs)

        # read netcdf variable(s)
        for name, value in targs.data.items():
            if isinstance(variables,list) and name not in variables:
                continue

            vardata = {"dimensions": []}
            indata.append(vardata)

            for d in value['dimensions']:
                dname = d['dimensions'][0]
                vardata[dname]= d['data']
                vardata["dimensions"].append(dname)

            vardata["data"] = value['data']

        if targs.summary:
            for var in indata:
                import pdb; pdb.set_trace()
                # name, desc, dimensions, vaule related
            return

        namemap = {}

        # normalize name
        if targs.dimension_name:
            for dname in targs.dimension_name:
                for key, newname in dname.kwargs.items():
                    if key == "time":
                        self.timename = newname
                    elif key == "lat":
                        self.latname = newname
                    elif key == "lon":
                        self.lonname = newname
                    elif key == "alt":
                        self.vertname = newname
                    else:
                        raise Exception("Unknown dimension name: %s" % key)

        # remove unused data

        if targs.time:
            import pdb; pdb.set_trace()

        if targs.latitude:
            import pdb; pdb.set_trace()

        if targs.longitude:
            import pdb; pdb.set_trace()

        if targs.altitude:
            import pdb; pdb.set_trace()


        # plots
        if targs.plot == "contour":

            for vardata in indata:
                data = vardata["data"]
                dims = vardata["dimensions"]
                lat = vardata["lat"]
                lon = vardata["lon"]
                time = vardata.get("time", None)
                alt = vardata.get("alt", None)
                import pdb; pdb.set_trace()

        #self.add_forward(data=outdata)
