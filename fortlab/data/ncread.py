# -*- coding: utf-8 -*-

import netCDF4
import pyloco

def normpath(path, type=None):

    split = [p.strip() for p in path.split("/") if p.strip()]

    if type in ("variable", "attribute"):
        newpath = "/".join(split)
    elif type in ("group",): 
        newpath = "/".join(split) + "/"
    else:
        newpath = "/".join([p.strip() for p in path.strip().split("/")])

    return "/" + newpath 

class NCRead(pyloco.Task):
    """Read a netcdf data file and convert data to a Python dictionary

'netcdfread' tasks read a data file in netcdf format and convert data in
the file to a Python dictionary

Examples
---------
"""
    _name_ = "ncread"
    _version_ = "0.1.0"
    _install_requires = ["netCDF4", "nctools_util"]

    def __init__(self, parent):

        self.add_data_argument("data", required=True, help="netcdf data file")

        self.add_option_argument("-v", "--variable", action="append",
                type=str, help="a variable name to collect", metavar="name")
        self.add_option_argument("-l", "--list", action="store_true",
                help="list variables in a netcdf file")
        self.add_option_argument("-i", "--info", action="append",
                help="data information", metavar="name")

        self.register_forward("data",
                help="netcdf variables in Python dictionary")

    def _get_dimensions(self, group, indata):

        dim = {}

        for dimension in group.dimensions.values():
            _d = {}
            _d["size"] = dimension.size   
            _d["isunlimited"] = dimension.isunlimited()
            dim[dimension.name] = _d

        if "dims" in indata:
            dims = indata["dims"]

        else:
            dims = {}
            indata["dims"] = dims

        dims[group.path] = dim
        return dim

    def _get_variables(self, group, indata):

        var = {}

        for variable in group.variables.values():

            if variable.name in indata["dims"][group.path]:
                pass

            elif "only" in indata and group.path+variable.name not in indata["only"]:
                continue

            _v = {}

            for _n in dir(variable):
                _a = getattr(variable, _n)

                if not _n.startswith("_") and not callable(_a):
                    _v[_n] = _a

            _v["data"] = variable[:]
            name = _v.pop("name")

            if name in indata["dims"][group.path]:
                indata["dims"][group.path][name]["variable"] = _v

            else:
                var[name] = _v

        return var

    def _get_ncattrs(self, group, indata):

        attrs = {}

        for attr in group.ncattrs():
            attrs[attr] = getattr(group, attr)

        return attrs

    def _collect_group(self, group, indata, outdata, parent_group):

        outdata["dims"] = self._get_dimensions(group, indata)
        outdata["vars"] = self._get_variables(group, indata)
        outdata["ncattrs"] = self._get_ncattrs(group, indata)

        outdata["cmptypes"] = group.cmptypes
        outdata["vltypes"] = group.vltypes
        outdata["enumtypes"] = group.enumtypes

        if outdata["cmptypes"] or outdata["vltypes"] or outdata["enumtypes"]:
            raise NotImplementedError("'cmptypes', 'vltypes', and 'enumtypes' are not supported yet.")

        outdata["outdata_model"] = group.data_model
        outdata["parent"] = group.parent
        outdata["path"] = group.path

        if outdata["parent"]:
            print("DEBUG: parent")
            import pdb; pdb.set_trace()

        outdata["groups"] = {}

    def _get_groupdict(self, group, indata, outdata, parent_group):

        outdata["group"][group.name] = d = {}
        return d

    def traverse(self, group, indata, outdata, parent_group=None,
                 F1=None, F2=None, F3=None, F4=None):

        if F1: F1(group, indata, outdata, parent_group)

        for g in group.groups.items():
            d = F2(g, indata, outdata, group) if F2 else outdata
            self.traverse(g, indata, d, parent_group=group)
            if F3: F3(g, indata, d, group)

        if F4: F4(group, indata, outdata, parent_group)

    def _desc_vars(self, group, indata, outdata, parent_group):

        dimnames = group.dimensions.keys()

        if "only" in indata and group.path in indata["only"]:
            print(group)

        for varname in group.variables.keys():
            if varname in dimnames:
                continue

            if "only" not in indata or group.path+varname in indata["only"]:
                var = group.variables[varname]
                dims = ["%s:%d"%d for d in zip(var.dimensions, var.shape)]
                print("%s :\t(%s) %s"%(group.path+var.name, ", ".join(dims), str(var.dtype)))

                if "verbose" in indata and indata["verbose"]:
                    for _n in dir(var):
                        _a = getattr(var, _n)

                        if not _n.startswith("_") and not callable(_a):
                            print("    - %s: %s" % (_n, str(_a)))
                    print("")

    def _desc_path(self, group, outdata, parent_group):
        print("\n[%s]" % group.path)

    def perform(self, targs):

        rootgrp = netCDF4.Dataset(targs.data, "r")

        if targs.list:
            attrs = {"verbose": False}
            self.traverse(rootgrp, attrs, {}, F1=self._desc_vars, F2=self._desc_path)

        if targs.info:
            info = [normpath(s, type=None) for s in targs.info]
            attrs = {"verbose": True, "only": info}
            self.traverse(rootgrp, attrs, {}, F1=self._desc_vars, F2=self._desc_path)

        indata = {}
        outdata = {}

        if targs.variable:
            variables = [normpath(s, type="variable") for s in targs.variable]
            indata["only"] = variables
            self.traverse(rootgrp, indata, outdata, F1=self._collect_group,
                          F2=self._get_groupdict)
        else:
            self.traverse(rootgrp, indata, outdata, F1=self._collect_group,
                          F2=self._get_groupdict)

        self.add_forward(data=outdata)
