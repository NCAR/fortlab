# -*- coding: utf-8 -*-

import netCDF4
import pyloco
import numpy

class NetcdfVars(pyloco.Task):
    """Read a Netcdf data file and convert data to a Python dictionary
for selected variables

'netcdfread' tasks read a data file in netcdf format and convert data in
the file to a Python dictionary

Examples
---------
"""
    _name_ = "netcdfvars"
    _version_ = "0.1.0"
    _install_requires_ = ["netcdfread"]

    def __init__(self, parent):

        self.add_data_argument("data", required=True, help="netcdf data file")

        self.add_option_argument("-v", "--variable", action="append", type=str, help="a variable name")
        self.add_option_argument("-l", "--list", action="store_true", help="list variables in a netcdf file")

        self.register_forward("data", help="Netcdf variables in Python dictionary")

    def perform(self, targs):

        retval, fwd = pyloco.perform("netcdfread", targs.data)

        indata = fwd["data"]
        variables = indata["variables"]
        groups = indata["groups"]
        dimensions = indata["dimensions"]

        outdata = {}

        if targs.list:
            # TODO: support group hierachy
            for name in indata["groups"]:
                print("[%s]" % name) 

            for name in indata["variables"]:
                print(name) 

            return

        if targs.variable:
            for name in targs.variable:
                vardata = {}
                outdata[name] = vardata
                vardata.update(variables[name])
                vardims = []
                for dimname in vardata["dimensions"]:
                    vardims.append(variables[dimname])
                vardata["dimensions"] = vardims

        self.add_forward(data=outdata)
