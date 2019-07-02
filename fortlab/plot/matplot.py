# -*- coding: utf-8 -*-

import pyloco
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


class MatPlot(pyloco.Task):
    """Plotting task based on matplotlib


Examples
---------
"""
    _name_ = "matplot"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("data", required=False, nargs="*", help="data input")

        self.add_option_argument('-f', metavar='figure creation', help='(E,P) define a figure for plotting.')
        self.add_option_argument('-t', '--title', metavar='title', action='append', help='title  plotting.')
        self.add_option_argument('-p', '--plot', metavar='plot type', action='append', param_parse=True, help='(E,P) plot type for plotting.')
        self.add_option_argument('-s', '--save', metavar='save', action='append', help='file path to save png image.')
        self.add_option_argument('-x', '--xaxis', metavar='xaxis', action='append', help='axes function wrapper for x axis settings.')
        self.add_option_argument('-y', '--yaxis', metavar='yaxis', action='append', help='axes function wrapper for y axis settings.')
        self.add_option_argument('-z', '--zaxis', metavar='zaxis', action='append', help='axes function wrapper for z axis settings.')
        self.add_option_argument('-g', action='store_true', help='grid for ax plotting.')
        self.add_option_argument('-l', action='store_true', help='legend for ax plotting')
        self.add_option_argument('--pandas', metavar='pandas', action='append', help='pandas plots.')
        self.add_option_argument('--legend', metavar='legend', action='append', help='plot legend')
        self.add_option_argument('--grid', metavar='grid', action='append', help='grid for plotting.')
        self.add_option_argument('--subplot', metavar='subplot', action='append', param_parse=True, help='(E,P) define subplot.')
        self.add_option_argument('--figure', metavar='figure function', action='append', help='define Figure function.')
        self.add_option_argument('--axes', metavar='axes', action='append', help='define Axes function.')
        self.add_option_argument('--noshow', action='store_true', default=False, help='prevent showing plot on screen.')
        self.add_option_argument('--noplot', action='store_true', default=False, help='prevent generating plot.')

        #self.register_forward("data", help="Netcdf data in Python dictionary")
        self.env = dict(self._env)
        self.env["matplotlib"] = mpl
        self.env["pyplot"] = plt

    def perform(self, targs):

        subplots = {}
        axes = {}

        # figure setting
        if targs.f:
            self.env['figure'] = eval('pyplot.figure(%s)'%targs.f, self.env)

        else:
            self.env['figure'] = eval('pyplot.figure()', self.env)

        # plot axis
        if targs.subplot:
            for subplot_arg in targs.subplot:
                # split by $; apply variable mapping repeatedly

                if len(subplot_arg.context) == 1:
                    subpname = subplot_arg.context[0]

                    if 'projection' in subplot_arg.kwargs and subplot_arg.kwargs['projection'] == '3d':
                         from mpl_toolkits.mplot3d import Axes3D
                         self.env['Axes3D'] = Axes3D
                    if subplot_arg.vargs:
                        subplots[subpname] = self.env['figure'].add_subplot(*subplot_arg.vargs, **subplot_arg.kwargs)
                    else:
                        subplots[subpname] = self.env['figure'].add_subplot(111, **subplot_arg.kwargs)
                else:
                    UsageError("The synaxt error near '@': %s"%str(subplot_arg))

        # execute figure functions
        if targs.figure:
            for fig_arg in targs.figure:
                s = fig_arg.split("$")

                # syntax: funcname@funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env)

                if len(items) == 1:
                    funcname = items[0][0][0]
                else:
                    UsageError("The synaxt error near '@': %s"%fig_arg)

                getattr(self.env['figure'], funcname)(*vargs, **kwargs)

        if targs.pandas:
            s = targs.pandas.split("$")
            pandas_args = s[0].split("@")
            if len(pandas_args) == 1:
                self.env["ax"] = teval(pandas_args[0], s[1:], self.env)
            elif len(pandas_args) == 2:
                self.env[pandas_args[0].strip()] = teval(pandas_args[1], s[1:], self.env)
            else:
                raise UsageError("pandas option has wrong syntax on using '@': %s"%targs.pandas)

        elif not targs.subplot:
            self.env['ax'] = self.env['figure'].add_subplot(111)

        # plotting
        plots = []
        if targs.plot:
            for plot_arg in targs.plot:

                import pdb; pdb.set_trace()
                if len(plot_arg.context) == 1:
                    axes = [self.env["ax"]]
                    funcname = items[0][0][0]
                elif len(plot_arg.context) == 2:
                    axes = items[0][0]
                    funcname = items[1][0][0]
                else:
                    UsageError("Following option needs one or two items at the left of @: %s"%plot_arg)

                for ax in axes:
                    if hasattr(ax, funcname):
                        plot_handle = getattr(ax, funcname)(*vargs, **kwargs)

                        try:
                            for p in plot_handle:
                                plots.append(p)
                        except TypeError:
                            plots.append(plot_handle)
                    else:
                        # TODO: handling this case
                        pass

                if funcname == 'pie':
                    for ax in axes:
                        self.env[ax].axis('equal')

        if 'plots' in self.env:
            self.env['plots'].extend(plots)
        else:
            self.env['plots'] = plots

        # title setting
        if targs.title:
            for title_arg in targs.title:
                s = title_arg.split("$")

                # syntax: [axname[,axname...]@]funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True])

                if len(items) == 0:
                    axes = [self.env["ax"]]
                elif len(items) == 1:
                    axes = items[0][0]
                else:
                    UsageError("The synaxt error near '@': %s"%title_arg)

                for ax in axes:
                    ax.set_title(*vargs, **kwargs)

        # x-axis setting
        if targs.xaxis:
            for xaxis_arg in targs.xaxis:
                s = xaxis_arg.split("$")

                # syntax: [axname[, axname...]@]funcname@funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True, False])

                if len(items) == 1:
                    axes = [self.env["ax"]]
                    funcname = "set_x"+items[0][0][0]
                elif len(items) == 2:
                    axes = items[0][0]
                    funcname = "set_x"+items[1][0][0]
                else:
                    UsageError("Following option needs one or two items at the left of @: %s"%xaxis_arg)

                for ax in axes:
                    if hasattr(ax, funcname):
                        getattr(ax, funcname)(*vargs, **kwargs)
                    else:
                        # TODO: handling this case
                        pass

       # y-axis setting
        if targs.yaxis:
            for yaxis_arg in targs.yaxis:
                s = yaxis_arg.split("$")

                # syntax: [axname[, axname...]@]funcname@funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True, False])

                if len(items) == 1:
                    axes = [self.env["ax"]]
                    funcname = "set_y"+items[0][0][0]
                elif len(items) == 2:
                    axes = items[0][0]
                    funcname = "set_y"+items[1][0][0]
                else:
                    UsageError("Following option needs one or two items at the left of @: %s"%yaxis_arg)

                for ax in axes:
                    if hasattr(ax, funcname):
                        getattr(ax, funcname)(*vargs, **kwargs)
                    else:
                        # TODO: handling this case
                        pass

        # z-axis setting
        if targs.zaxis:
            for zaxis_arg in targs.zaxis:
                s = zaxis_arg.split("$")

                # syntax: [axname[, axname...]@]funcname@funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True, False])

                if len(items) == 1:
                    axes = [self.env["ax"]]
                    funcname = "set_z"+items[0][0][0]
                elif len(items) == 2:
                    axes = items[0][0]
                    funcname = "set_z"+items[1][0][0]
                else:
                    UsageError("Following option needs one or two items at the left of @: %s"%zaxis_arg)

                for ax in axes:
                    if hasattr(ax, funcname):
                        getattr(ax, funcname)(*vargs, **kwargs)
                    else:
                        # TODO: handling this case
                        pass

        # grid setting
        if targs.g:
            for key, value in self.env.items():
                if isinstance(value, self.env['mpl'].axes.Axes):
                    value.grid()

        if targs.grid:
            for grid_arg in targs.grid:
                s = grid_arg.split("$")

                # syntax: [axname[,axname...]@]funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True])

                if len(items) == 0:
                    axes = [self.env["ax"]]
                elif len(items) == 1:
                    axes = items[0][0]
                else:
                    UsageError("The synaxt error near '@': %s"%grid_arg)

                for ax in axes:
                    ax.grid(*vargs, **kwargs)

        # legend setting
        if targs.l:
            for key, value in self.env.items():
                if isinstance(value, self.env['mpl'].axes.Axes):
                    value.legend()

        if targs.legend:
            for legend_arg in targs.legend:
                s = legend_arg.split("$")

                # syntax: [axname[,axname...]@]funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True])

                if len(items) == 0:
                    axes = [self.env["ax"]]
                elif len(items) == 1:
                    axes = items[0][0]
                else:
                    UsageError("The synaxt error near '@': %s"%legend_arg)

                for ax in axes:
                    ax.legend(*vargs, **kwargs)

        # execute axes functions
        if targs.axes:
            for axes_arg in targs.axes:
                s = axes_arg.split("$")
                # syntax: [axname[, axname...]@]funcname@funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue(s[0], s[1:], self.env, evals=[True, False])

                if len(items) == 1:
                    axes = [self.env["ax"]]
                    funcname = items[0][0][0]
                elif len(items) == 2:
                    axes = items[0][0]
                    funcname = items[1][0][0]
                else:
                    UsageError("Following option needs one or two items at the left of @: %s"%axes_arg)

                for ax in axes:
                    getattr(ax, funcname)(*vargs, **kwargs)

        elif not self.env['plots']:
            if targs.figure:
                pass
            elif targs.data:
                for d in targs.data:
                    if isinstance(d, str):
                        self.env["ax"].plot(eval(d))
                    else: 
                        try:
                            iter(d)
                            self.env["ax"].plot(d)
                        except TypeError as te:
                            pass
            else:
                raise UsageError("There is no data to plot.")

        # saving an image file
        if targs.save:
            for save_arg in targs.save:
                s = save_arg.split("$")
                # savefig(fname, dpi=None, facecolor='w', edgecolor='w',
                # orientation='portrait', papertype=None, format=None,
                # transparent=False, bbox_inches=None, pad_inches=0.1,
                # frameon=None)
                # syntax: funcargs
                # text, varmap, self.env, evals
                items, vargs, kwargs = parse_optionvalue('r'+s[0], s[1:], self.env)

                name = vargs.pop(0)

                if self.env['num_pages'] > 1:
                    root, ext = os.path.splitext(name)
                    name = '%s-%d%s'%(root, self.env['page_num'], ext)

                self.env["figure"].savefig(name, *vargs, **kwargs)

        # displyaing an image on screen
        if not targs.noshow:
            self.env['pyplot'].show()

        self.env["figure"].clear()
        self.env["pyplot"].close(self.env["figure"])
        del self.env['figure']

        #self.add_forward(data=data)
