# -*- coding: utf-8 -*-

import netCDF4
import pyloco
import numpy


class NCRead(pyloco.Task):
    """Read a netcdf data file and convert data to a Python dictionary

'netcdfread' tasks read a data file in netcdf format and convert data in
the file to a Python dictionary

Examples
---------
"""
    _name_ = "ncread"
    _version_ = "0.1.0"
    _install_requires = ["netCDF4", "numpy"]

    def __init__(self, parent):

        self.aliases = {
            "name": "long_name",
            "unit": "units",
            "dimension": "dimensions"
        }

        alias_str = ", ".join([k+"="+v for k,v in self.aliases.items()])

        self.add_data_argument("data", required=True, help="netcdf data file")

        self.add_option_argument("-v", "--variable", action="append",
                type=str, help="a variable name", metavar="name")
        self.add_option_argument("-l", "--list", action="store_true",
                help="list variables in a netcdf file")
        self.add_option_argument("-s", "--summary", action="store_true",
                help="variable information")
        self.add_option_argument("-a", "--alias", action="append", metavar="attr=name",
                help="change variable attribute names. Defaults are (%s)" % alias_str, param_parse=True)

        self.register_forward("data",
                help="netcdf variables in Python dictionary")

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

        # dimensions, variables, attributes, groups
        indata = {}

        rootgrp = netCDF4.Dataset(targs.data, "r")
        self._build_data(rootgrp, indata)

        dimensions = indata["dimensions"]
        variables = indata["variables"]
        groups = indata["groups"]

        if targs.alias:
            for alias in targs.alias:
                self.aliases.update(alias.kwargs)

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

        outdata = {}

        if targs.variable:
            out_vars = targs.variable

        else:
            out_vars = variables.keys() 

        for name in out_vars:
            vardata = {}
            vardims = []

            for dimname in variables[name]["dimensions"]:
                if dimname not in variables:
                    vardims = None
                    print("INFO: Variable '%s' is not collected due to not "
                          "having '%s' dimension data." % (name, dimname))
                    break
                else:
                    vardims.append(variables[dimname])

            if vardims:
                vardata["dimensions"] = vardims
                vardata.update(variables[name])
                outdata[name] = vardata

        self.add_forward(data=outdata)
