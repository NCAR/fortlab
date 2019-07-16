# -*- coding: utf-8 -*-

import pyloco
import numpy
import matplotlib
import matplotlib.pyplot as pyplot


class Plotter(object):

    def __init__(self, env):
        self._env = env

    def update_env(self, *vargs, **kwargs):

        for varg in vargs:
            self._env.update(varg)

        for k, v in kwargs.items():
            self._env[k] = v

    def remove_env(self, *vargs):

        for varg in vargs:
            del self._env[varg]


class MatPlot(pyloco.Task):
    """matplotlib-based plotting task


Examples
---------
"""
    _name_ = "matplot"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("data", required=False, nargs="*",
                evaluate=True, help="(E) data input")

        self.add_option_argument('-f', metavar='figure creation',
                param_parse=True,
                help='(E,P) define a figure for plotting.')
        self.add_option_argument('-t', '--title', metavar='title',
                param_parse=True,
                help='(E,P) plot title')
        self.add_option_argument('-c', '--eval', metavar='expr',
                action='append', param_parse=True, dest="calc",
                help='(E,P) evaluate an Python expression')
        self.add_option_argument('-p', '--plot', metavar='plot type',
                action='append', param_parse=True,
                help='(E,P) plot type for plotting.')
        self.add_option_argument('-s', '--save', metavar='save',
                param_parse=True, help='(E,P) file path to save png image.')
        self.add_option_argument('-x', '--xaxis', metavar='xaxis',
                action='append', param_parse=True,
                help='(E,P) axes function wrapper for x axis settings.')
        self.add_option_argument('-y', '--yaxis', metavar='yaxis',
                action='append', param_parse=True,
                help='(E,P) axes function wrapper for y axis settings.')
        self.add_option_argument('-z', '--zaxis', metavar='zaxis',
                action='append', param_parse=True,
                help='(E,P) axes function wrapper for z axis settings.')
        self.add_option_argument('-g', action='store_true',
                help='grid for ax plotting.')
        self.add_option_argument('-l', action='store_true',
                help='legend for ax plotting')
        self.add_option_argument('--pandas', metavar='pandas',
                action='append', param_parse=True,
                help='(E,P) pandas plots.')
        self.add_option_argument('--legend', metavar='legend',
                action='append', param_parse=True,
                help='(E,P) plot legend')
        self.add_option_argument('--grid', metavar='grid',
                action='append', param_parse=True,
                help='(E,P) grid for plotting.')
        self.add_option_argument('--subplot', metavar='subplot',
                action='append', param_parse=True,
                help='(E,P) define subplot.')
        self.add_option_argument('--figure', metavar='figure function',
                action='append', param_parse=True,
                help='(E,P) define Figure function.')
        self.add_option_argument('--axes', metavar='axes',
                action='append', param_parse=True,
                help='(E,P) define Axes function.')
        self.add_option_argument('--noshow', action='store_true',
                param_parse=True,
                help='prevent showing plot on screen.')
        self.add_option_argument('--noplot', action='store_true',
                param_parse=True,
                help='prevent generating plot.')

        #self.register_forward("data", help="Netcdf data in Python dictionary")
        self._env["np"] = numpy
        self._env["mpl"] = matplotlib
        self._env["plt"] = pyplot

        self.figure = None
        self.axes = {}
        self.axes3d = None
        self.plots = []

    def pre_perform(self, targs):

        if targs.multiproc:
            vargs = targs.multiproc.vargs

            if len(vargs) == 1:
                vargs.append("spawn")

            elif len(vargs) > 1:
                vargs[1] = "spawn"

        super(MatPlot, self).pre_perform(targs)

    def _eval(self, opt):

        for i in range(len(opt.vargs)):
            opt.vargs[i] = eval(opt.vargs[i], self._env) 

        for k, v in opt.kwargs.items():
            opt.kwargs[k] = eval(v, self._env) 

    def perform(self, targs):

        if targs.plot:
            opts = targs.plot
            plotter = Plotter(self._env)
            targs.plot = []

            for opt in opts:
                if not opt:
                    continue

                fname = opt.context[0] if opt.context else "plot"

                if "." in fname:
                    plotfunc = eval(fname, self._env)
                    plotfunc(plotter, opt, targs)

                elif hasattr(self, fname):
                    getattr(self, fname)(plotter, opt, targs)

                elif fname in self._env:
                    self._env[fname](plotter, opt, targs)

                else:
                    targs.plot.append(opt)

        if targs.calc:
            for calc_arg in targs.calc:
                self._eval(calc_arg)

                for lhs, rhs in calc_arg.kwargs.items():
                    self._env[lhs] = rhs

        # figure setting
        if targs.f:
            self._eval(targs.f)
            vargs = targs.f.vargs
            kwargs = targs.f.kwargs
            self.figure = pyplot.figure(*vargs, **kwargs)

        else:
            self.figure = pyplot.figure()

        # plot axis
        if targs.subplot:
            for subplot_arg in targs.subplot:
                self._eval(subplot_arg)

                if len(subplot_arg.context) == 1:
                    subpname = subplot_arg.context[0]
                    vargs = subplot_arg.vargs
                    kwargs = subplot_arg.kwargs

                    if 'projection' in kwargs and kwargs['projection'] == '3d':
                         from mpl_toolkits.mplot3d import Axes3D
                         self.axes3d = Axes3D
                    if vargs:
                        self.axes[subpname] = self.figure.add_subplot(*vargs, **kwargs)
                    else:
                        self.axes[subpname] = self.figure.add_subplot(111, **kwargs)
                else:
                    UsageError("The synaxt error near '@': %s"%str(subplot_arg))

        if not self.axes:
            self.axes["ax"] = self.figure.add_subplot(111)

        # execute figure functions
        if targs.figure:
            for fig_arg in targs.figure:
                self._eval(fig_arg)
                vargs = fig_arg.vargs
                kwargs = fig_arg.kwargs

                if len(fig_arg.context) == 1:
                    funcname = fig_arg.context[0]

                else:
                    UsageError("The synaxt error near '@': %s" % str(fig_arg))

                getattr(self.figure, funcname)(*vargs, **kwargs)

        # plotting
        plots = []
        if targs.plot:
            for plot_arg in targs.plot:
                self._eval(plot_arg)
                vargs = plot_arg.vargs
                kwargs = plot_arg.kwargs

                nctx = len(plot_arg.context)

                funcname = plot_arg.context[0] if nctx > 0 else "plot"
                axname = plot_arg.context[1] if nctx > 1 else "ax"
                ax = self.axes[axname]

                if hasattr(ax, funcname):
                    plot_handle = getattr(ax, funcname)(*vargs, **kwargs)

                    try:
                        for p in plot_handle:
                            self.plots.append(p)
                    except TypeError:
                        self.plots.append(plot_handle)
                else:
                    # TODO: handling this case
                    pass

                if funcname == 'pie':
                    ax.axis('equal')

        # title setting
        if targs.title:
            self._eval(targs.title)
            vargs = targs.title.vargs
            kwargs = targs.title.kwargs

            if len(targs.title.context) == 0:
                self.axes["ax"].set_title(*vargs, **kwargs)
            elif len(targs.title.context) == 1:
                self.axes[targs.title.context[0]].set_title(*vargs, **kwargs)
            else:
                UsageError("The synaxt error near '@': %s" % str(targs.title))

        # x-axis setting
        if targs.xaxis:
            for xaxis_arg in targs.xaxis:
                self._eval(xaxis_arg)
                vargs = xaxis_arg.vargs
                kwargs = xaxis_arg.kwargs
                funcname = "set_x"+xaxis_arg.context[0]

                if len(xaxis_arg.context) == 1:
                    ax = self.axes["ax"]

                elif len(xaxis_arg.context) == 2:
                    ax = self.axes[xaxis_arg.context[1]]

                else:
                    UsageError("Following option needs one or two items at the left of @: %s" % str(xaxis_arg))

                getattr(ax, funcname)(*vargs, **kwargs)

       # y-axis setting
        if targs.yaxis:
            for yaxis_arg in targs.yaxis:
                self._eval(yaxis_arg)
                vargs = yaxis_arg.vargs
                kwargs = yaxis_arg.kwargs
                funcname = "set_y"+yaxis_arg.context[0]

                if len(yaxis_arg.context) == 1:
                    ax = self.axes["ax"]

                elif len(yaxis_arg.context) == 2:
                    ax = self.axes[yaxis_arg.context[1]]

                else:
                    UsageError("Following option needs one or two items at the left of @: %s" % str(yaxis_arg))

                getattr(ax, funcname)(*vargs, **kwargs)

        # z-axis setting
        if targs.zaxis:
            for zaxis_arg in targs.zaxis:
                self._eval(zaxis_arg)
                vargs = zaxis_arg.vargs
                kwargs = zaxis_arg.kwargs
                funcname = "set_z"+zaxis_arg.context[0]

                if len(zaxis_arg.context) == 1:
                    ax = self.axes["ax"]

                elif len(zaxis_arg.context) == 2:
                    ax = self.axes[zaxis_arg.context[1]]

                else:
                    UsageError("Following option needs one or two items at the left of @: %s" % str(zaxis_arg))

                getattr(ax, funcname)(*vargs, **kwargs)

        # grid setting
        if targs.g:
            for ax in self.axes.values():
                ax.grid()

        if targs.grid:
            for grid_arg in targs.grid:
                self._eval(grid_arg)
                vargs = grid_arg.vargs
                kwargs = grid_arg.kwargs

                if len(grid_arg.context) == 0:
                    ax = self.axes["ax"]

                elif len(grid_arg.context) == 1:
                    ax = self.axes[grid_arg.context[0]]

                else:
                    UsageError("Following option needs one or two items at the left of @: %s" % str(grid_arg))

                ax.grid(*vargs, **kwargs)

        # legend setting
        if targs.l:
            for ax in self.axes.values():
                ax.legend()

        if targs.legend:
            for legend_arg in targs.legend:
                self._eval(legend_arg)
                vargs = legend_arg.vargs
                kwargs = legend_arg.kwargs

                if len(legend_arg.context) == 0:
                    ax = self.axes["ax"]

                elif len(legend_arg.context) == 1:
                    ax = self.axes[legend_arg.context[0]]

                else:
                    UsageError("Following option needs one or two items at the left of @: %s" % str(legend_arg))

                ax.legend(*vargs, **kwargs)

        # execute axes functions
        if targs.axes:
            for axes_arg in targs.axes:
                self._eval(axes_arg)
                vargs = axes_arg.vargs
                kwargs = axes_arg.kwargs
                funcname = axes_arg.context[0]

                if len(axes_arg.context) == 1:
                    ax = self.axes["ax"]

                elif len(axes_arg.context) == 2:
                    ax = self.axes[axes_arg.context[1]]

                else:
                    UsageError("Following option needs one or two items at the left of @: %s" % str(axes_arg))

                getattr(ax, funcname)(*vargs, **kwargs)

        elif not self.plots:
            if targs.figure:
                pass
            elif targs.data:
                for d in targs.data:
                    self.axes["ax"].plot(d)
            else:
                raise UsageError("There is no data to plot.")

        # saving an image file
        if targs.save:
            # savefig(fname, dpi=None, facecolor='w', edgecolor='w',
            # orientation='portrait', papertype=None, format=None,
            # transparent=False, bbox_inches=None, pad_inches=0.1,
            # frameon=None)
            self._eval(targs.save)
            name = targs.save.vargs.pop(0)
            vargs = targs.save.vargs
            kwargs = targs.save.kwargs
            self.figure.savefig(name, *vargs, **kwargs)

        # displyaing an image on screen
        if not targs.noshow:
            pyplot.show()

        self.figure.clear()
        pyplot.close(self.figure)

        #self.add_forward(data=data)
