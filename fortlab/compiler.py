"""fortlab compiler module
"""

from __future__ import unicode_literals

import sys
import inspect
from pyloco import Task
from langlab import GenericCompiler, compflag

class Compiler(Task):
    "a short task description"

    _name_ = "compiler"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("command", help="application build command")
        self.add_data_argument("outfile", help="output file")

        self.add_option_argument("--workdir", help="working directory")

        self.register_forward("data", help="traced data")

    def perform(self, targs):

        cfg = compflag(targs.command, fort_compilers, workdir=targs.workdir)

        if len(cfg.sections())>0:
            with open(targs.outfile, 'w') as f:
                cfg.write(f)

        self.add_forward(data=cfg)

class GenericFortranCompiler(GenericCompiler):
    file_exts = ['f', 'f90', 'f95', 'f03', 'f08', '.ftn', 'F', 'F90', 'F95', 'F03', 'F08', '.FTN' ]

    def get_discard_opts_noarg(self):
        return super(GenericFortranCompiler, self).get_discard_opts_noarg()

    def get_discard_opts_arg(self):
        return super(GenericFortranCompiler, self).get_discard_opts_arg()

class IntelFortranCompiler(GenericFortranCompiler):
    compid = 'ifort'
    compnames = ['ifort']
    openmp_opt = [ r'-openmp' ]
    fpp = '-fpp'

    discard_opts_arg = [ '-module' ]

    def get_discard_opts_noarg(self):
        return super(IntelFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(IntelFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

class GnuFortranCompiler(GenericFortranCompiler):
    compid = 'gfortran'
    compnames = ['gfortran']
    openmp_opt = [ r'-fopenmp' ]
    fpp = '-cpp'

    discard_opts_arg = [ '-J' ]

    def get_discard_opts_noarg(self):
        return super(GnuFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(GnuFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

class PgiFortranCompiler(GenericFortranCompiler):
    compid = 'pgfortran'
    compnames = ['pgfortran', 'pgf77', 'pgf90', 'pgf95', 'pghpf']
    openmp_opt = [ r'-mp' ]
    fpp = '-Mpreprocess'

    discard_opts_arg = [ '-module' ]

    def get_discard_opts_noarg(self):
        return super(PgiFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(PgiFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

class PathscaleFortranCompiler(GenericFortranCompiler):
    compid = 'path90'
    compnames = ['path90', 'path95']
    openmp_opt = [ r'-mp' ]

    def get_discard_opts_noarg(self):
        return super(PathscaleFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(PathscaleFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

class NagFortranCompiler(GenericFortranCompiler):
    compid = 'nagfor'
    compnames = ['nagfor']
    openmp_opt = [ r'-openmp' ]
    fpp = '-cpp'

    def get_discard_opts_noarg(self):
        return super(NagFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(NagFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

class IbmxlFortranCompiler(GenericFortranCompiler):
    compid = 'xlf'
    compnames = ['xlf', 'xlf90', 'xlf95', 'xlf2003', 'xlf2008']
    openmp_opt = [ r'-qsmp' ]
    fpp = '-WF,-qfpp'

    def get_discard_opts_noarg(self):
        return super(IbmxlFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(IbmxlFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

class CrayFortranCompiler(GenericFortranCompiler):
    compid = 'crayftn'
    compnames = ['crayftn', 'ftn']
    openmp_opt = [ r'-omp', r'-h\s+omp' ]
    # fpp is enabled by default

    discard_opts_arg = [ '-J' ]

    def get_discard_opts_noarg(self):
        return super(IbmxlFortranCompiler, self).get_discard_opts_noarg() + self.discard_opts_noarg

    def get_discard_opts_arg(self):
        return super(IbmxlFortranCompiler, self).get_discard_opts_arg() + self.discard_opts_arg

#class IntelFortranCompiler(GenericFortranCompiler):
#    # space: False-no space, True-space required, None - any
#    # args: None-none, [|]-optional string, 
#    OPTIONS = { \
#        '-mmic': { 'args': None, 'default': False },
#        '-falias': { 'args': None, 'default': True },
#        '-fast': { 'args': None, 'default': False },
#        '-arch': { 'args': '[CORE-AVX2|CORE-AVX-I|AVX|SSE4.2|SSE4.1|SSSE3|SSE3|SSE2|SSE|IA32]', 'default': 'SSE2', 'space': True },
#        '-ax': { 'args': '[COMMON-AVX512|MIC-AVX512|CORE-AVX512|CORE-AVX2|CORE-AVX-I|AVX|SSE4.2|SSE4.1|SSSE3|SSE3|SSE2]', 'default': False, 'space': False },
#        '-m32': { 'args': None, 'default': False },
#        '-m64': { 'args': None, 'default': False },
#        '-xHost': { 'args': None, 'default': False },
#        '-ip': { 'args': None, 'default': False },
#        '-ipo': { 'args': '\d+', 'default': False, 'space': False },
#        '-no-ipo': { 'args': None, 'default': True },
#        '-mkl': { 'args': '[|=parallel|=sequential|=cluster]', 'default': False, 'space': False },
#        '-pad': { 'args': None, 'default': False },
#        '-no-pad': { 'args': None, 'default': False },
#        '-qopt-prefetch': { 'args': '[|=0|=1|=2|=3|=4]', 'default': False, 'space': False },
#        '-qno-opt-prefetch': { 'args': None, 'default': False },
#        '-simd': { 'args': None, 'default': True },
#        '-no-simd': { 'args': None, 'default': False },
#        '-unroll': { 'args': '[|=\d+]', 'default': False, 'space': False },
#        '-vec': { 'args': None, 'default': True },
#        '-no-vec': { 'args': None, 'default': False },
#        '-qopt-report': { 'args': '[|=0|=1|=2|=3|=4|=5]', 'default': False, 'space': False },
#        '-parallel': { 'args': None, 'default': False },
#        '-qopenmp': { 'args': None, 'default': False },
#        '-qno-openmp': { 'args': None, 'default': True },
#        '-fma': { 'args': None, 'default': True },
#        '-no-fma': { 'args': None, 'default': False },
#        '-fp-model': { 'args': '[precise|strict|source|fast=1|fast=2|except|no-except]', 'default': 'fast=1', 'space': True },
#        '-ftz': { 'args': None, 'default': True },
#        '-no-ftz': { 'args': None, 'default': False },
#        '-prec-div': { 'args': None, 'default': True },
#        '-no-prec-div': { 'args': None, 'default': False },
#        '-prec-sqrt': { 'args': None, 'default': True },
#        '-no-prec-sqrt': { 'args': None, 'default': False },
#        '-finline': { 'args': None, 'default': False },
#        '-fno-inline': { 'args': None, 'default': True },
#
#    }
#    pass
#


fort_compilers = []

for key in dir():
    obj = getattr(sys.modules[__name__], key)
    try:
        if issubclass(obj, GenericCompiler):
            fort_compilers.append(obj)
    except:
        pass
