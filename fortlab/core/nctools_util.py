# -*- coding: utf-8 -*-
  
def normpath(path, type=None):

    split = [p.strip() for p in path.split("/") if p.strip()]

    if type in ("variable", "attribute"):
        newpath = "/".join(split)
    elif type in ("group",): 
        newpath = "/".join(split) + "/"
    else:
        newpath = "/".join([p.strip() for p in path.strip().split("/")])

    return "/" + newpath 

def traverse(group, indata, outdata, parent_group=None,
             F1=None, F2=None, F3=None, F4=None):

    if F1: F1(group, indata, outdata, parent_group)

    for g in group["groups"].items():
        d = F2(g, indata, outdata, group) if F2 else outdata
        traverse(g, indata, d, parent_group=group)
        if F3: F3(g, indata, d, group)

    if F4: F4(group, indata, outdata, parent_group)

def get_variables(group, varpaths, outdata, parent_group):

    if varpaths:
        for vname, var in group["vars"].items():
            vpath = group["path"] + vname
            if vpath in varpaths:
                outdata[vpath] = var

def get_dimension(group, dimpaths, outdata, parent_group):

    if dimpaths:
        for vname, var in group["dims"].items():
            vpath = group["path"] + vname
            if vpath in dimpaths:
                outdata[vpath] = var

def get_var(group, name):

    outvar = normpath(name)
    indata, outdata = [outvar], {}
    traverse(group, indata, outdata, F1=get_variables)
    return outdata[outvar]

def get_dim(group, name):

    outdim = normpath(name)
    indata, outdata = [outdim], {}
    traverse(group, indata, outdata, F1=get_dimension)
    return outdata[outdim]

def get_slice_from_dims(var, dims):

    data = var["data"]
    slices = []

    for dname in var["dimensions"]:
        if dname in dims:
            slices.append(":")

        else:
            slices.append("0")

    # TODO : change order of dimension
    return eval("data[%s]" % ",".join(slices))
