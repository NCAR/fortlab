# -*- coding: utf-8 -*-

import netCDF4
import pyloco
import numpy

# NOTE: pyloco pickle file format should support multiple subformat for example netcdf saving format


#def numpy_reader(path):
#
#    return numpy.load(path)

class NetcdfRead(pyloco.Task):
    """Read a Netcdf data file and convert data to a Python dictionary

'netcdfread' tasks read a data file in netcdf format and convert data in
the file to a Python dictionary

Examples
---------
"""
    _name_ = "netcdfread"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("data", required=True, help="netcdf data file")

        self.register_forward("data", help="Netcdf data in Python dictionary")

    def _get_dimensions(self, group):

        dim = {}

        for dimension in group.dimensions.values():
            _d = {}
            _d["size"] = dimension.size   
            _d["isunlimited"] = dimension.isunlimited()
            dim[dimension.name] = _d

        return dim

    def _get_variables(self, group):

        var = {}

        for variable in group.variables.values():
            _v = {}

            for _n in dir(variable):
                _a = getattr(variable, _n)

                if not _n.startswith("_") and not callable(_a):
                    _v[_n] = _a

            _v["data"] = variable[:]
            name = _v.pop("name")
            var[name] = _v

        return var

    def _collect_group(self, group, data):

        data["dimensions"] = self._get_dimensions(group)
        data["variables"] = self._get_variables(group)
        data["groups"] = {}

    def _build_data(self, group, data):

        self._collect_group(group, data)

        for g in group.groups.items():
            data["group"][g.name] = d = {}
            self._build_data(g, d)

#    def write_pickle(self, pickler, data):
#
#        for key, value in data.items():
#
#            if isinstance(value, numpy.ndarray):
#
#                path, pathid = pickler.attach_reader(numpy_reader)               
#                numpy.save(path, value)
#                data[key] = pathid
#
#            elif isinstance(value, dict):
#                self.write_pickle(pickler, value)
#
#        return data

    def perform(self, targs):

        # dimensions, variables, attributes, groups
        data = {}

        rootgrp = netCDF4.Dataset(targs.data, "r")

        self._build_data(rootgrp, data)

        self.add_forward(data=data)
