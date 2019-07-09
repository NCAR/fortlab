# -*- coding: utf-8 -*-
  
def normpath(path, type=None):

    split = [p.strip() for p in path.split("/") if p.strip()]

    if type in ("variable", "attribute"):
        return "/" + "/".join(split)
    elif type in ("group",): 
        return "/" + "/".join(split) + "/"
    else:
        return "/".join([p.strip() for p in path.strip().split("/")])
