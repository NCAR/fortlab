import pyloco

class FortLab(pyloco.Manager):
    _name_ = "fortlab"
    _version_ = "0.1.0"
    _description_ = "Fortran Research Laboratory"
    _long_description_ = """fortlab : a collection of tools for Fortran Research.
"""
    _author_='Youngsung Kim'
    _author_email_ ='youngsun@ucar.edu'
    _license_ ='MIT'
    _url_='https://github.com/NCAR/fortlab'
    pyloco.Manager.load_default_task("fortparse.py", "fortdeps.py")
