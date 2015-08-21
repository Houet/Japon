#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

""" fonction pour gerer l'affichage classique """


from tkinter import *
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import numpy as np
from math import fabs

from fonction_base import *


class InfoSpike(LabelFrame):
    """ small frame with information about filter """
    def __init__(self, parent, info, **kwargs):
        LabelFrame.__init__(self, parent, **kwargs)

        Label(self, text="Method:").grid(column=1, row=1, sticky=W)
        Label(self,
              textvariable=info["method"],
              width=5,
              anchor=E).grid(column=2, row=1, sticky=E)
        Label(self, text="Sp. detected:").grid(column=1, row=2, sticky=W)
        Label(self,
              width=7,
              anchor=E,
              textvariable=info["nb_spike"]).grid(column=2, row=2, sticky=E)
        Label(self, text="Spike time:").grid(column=1, row=3, sticky=W)
        Label(self,
              textvariable=info["time"]).grid(column=2, row=3, sticky=E)
        Label(self, text="Highest val.:").grid(column=1, row=4, sticky=W)
        Label(self,
              textvariable=info["highest value"],
              width=9,
              anchor=E).grid(column=2, row=4, sticky=E)
        Label(self, text="Lowest val.:").grid(column=1, row=5, sticky=W)
        Label(self,
              textvariable=info["lowest value"],
              width=9,
              anchor=E).grid(column=2, row=5, sticky=E)


class ClicPosition(object):
    def __init__(self, window, fig, support_fig, filtre, start, time_s, canvas):
        self.window = window
        self.ind = 0
        self.f = fig
        self.support = support_fig
        self.ax = self.f.get_children()[2]
        self.ax = self.ax.twinx()
        self.ax.yaxis.set_visible(False)
        fig.canvas.mpl_connect("button_press_event", self)
        self.x = None
        self.name = filtre[0]
        self.filtre = filtre[1]
        self.spike = filtre[1].tab_spikes
        self.start = start
        self.time_sample = time_s
        self.canvas = canvas
        if self.spike != [] or self.filtre.methode is not None:
            if self.name == "Filter 1":
                self.canvas.bind_all("<Right>", self.get_next_spike)
                self.canvas.bind_all("<Left>", self.get_next_spike)
            else:
                self.canvas.bind_all("<q>", self.get_next_spike)
                self.canvas.bind_all("<d>", self.get_next_spike)
        self.dico = {"method": StringVar(self.window, self.filtre.methode),
                     "nb_spike": IntVar(self.window,
                                        self.filtre.number_spikes),
                     "time": IntVar(self.window, 0),
                     "highest value": IntVar(self.window, None),
                     "lowest value": IntVar(self.window, None),
                     }
        self.info = InfoSpike(self.window.infoframe,
                              self.dico,
                              text=self.name,
                              width=15)
        if self.filtre.methode != "":
            self.info.grid(column=self.name.split(" ")[1],
                           row=3,
                           sticky=W,
                           padx=5)

    def indicator(self, x):
        """ place an indicator on the spike selected """
        correction = 0
        if self.filtre.methode != "Slope":
            correction = 10
        try:
            del self.ax.lines[-1]
        except IndexError:
            pass
        except AttributeError:
            pass
        self.indic = self.ax.axvline(x + correction/self.time_sample, color="b")
        self.support.draw()

        tab_info = self.filtre.info_spike[self.ind]

        self.dico["time"].set((tab_info["time"] + int(self.start*self.time_sample))/self.time_sample)
        self.dico["highest value"].set(tab_info["highest value"])
        self.dico["lowest value"].set(tab_info["lowest value"])
        return

    def get_next_spike(self, event):
        """ return next spike ordered by time """
        range_next = (self.ind + 1, len(self.spike), 1)
        if event.keysym == "Left":
            range_next = (self.ind - 1, 0, -1)
        if event.keysym == "q":
            range_next = (self.ind - 1, 0, -1)
        for i in range(range_next[0], range_next[1], range_next[2]):
            if self.spike[i] == 1:
                self.ind = i

                self.indicator(self.ind/self.time_sample + self.start)
                break
        return

    def __call__(self, event):
        if not event.inaxes:
            return
        self.x = int((event.xdata - self.start)*self.time_sample)
        if self.filtre.methode != "Slope":
            self.x -= 10

        hitbox = 10
        for i in range(hitbox):
            if 1 in self.spike[self.x-i: self.x+i]:
                self.indice = self.spike[self.x-i: self.x+i].index(1)
                
                self.ind = self.x + (self.indice - i)
                self.indicator(self.ind/self.time_sample + self.start)
                break

        # else:
        #     try:
        #         del self.ax.lines[-1]
        #     except IndexError:
        #         pass


def plot(dat, axe, time_sample, fig_number, filter1, filter2, mm, th1, th2,
         unitx, unity,
         f1=False, f2=False, mov=False,
         mov_up_1=False, mov_down_1=False, mov_up_2=False, mov_down_2=False):
    """
    trace la figure comme il faut
    fig = figure sur laquelle tracer
    """

    fig = Figure(figsize=(8, 6),
                 dpi=100,
                 tight_layout=True,
                 facecolor="0.90")

    X = [i / time_sample for i in range(len(dat))]
    x_use = X[axe[0]:axe[1]]

    if len(filter1) != len(x_use):
        x_use_1 = x_use[10:-11]
    else:
        x_use_1 = x_use

    if len(filter2) != len(x_use):
        x_use_2 = x_use[10:-11]
    else:
        x_use_2 = x_use

    d_use = dat[axe[0]:axe[1]]
    mm_up_1 = [i + th1 for i in mm]
    mm_down_1 = [i - th1 for i in mm]
    mm_up_2 = [i + th2 for i in mm]
    mm_down_2 = [i - th2 for i in mm]

    ax1 = fig.add_subplot(fig_number)
    ax1.set_xlabel("Time ({})".format(unitx))
    ax1.set_ylabel("Amplitude ({})".format(unity))
    ax1.grid(True)
    try:
        ax1.axis([axe[0] / time_sample,
                 axe[1] / time_sample,
                 axe[2],
                 axe[3]])
    except ValueError:
        raise FileError
    ax1.plot(x_use, d_use, "r")

    ax2 = ax1.twinx()
    ax2.axis([axe[0] / time_sample, axe[1] / time_sample, 0, 1])
    ax2.yaxis.set_visible(False)

    try:
        if f1.get():
            ax2.plot(x_use_1, filter1, "y")

        if mov_up_1.get():
            ax1.plot(x_use[10:-11], mm_up_1, "b")

        if mov_down_1.get():
            ax1.plot(x_use[10:-11], mm_down_1, "b")
    except ValueError:
        raise FilterError("Filter 1")

    try:
        if f2.get():
            ax2.plot(x_use_2, filter2, "g")

        if mov_up_2.get():
            ax1.plot(x_use[10:-11], mm_up_2, "k")

        if mov_down_2.get():
            ax1.plot(x_use[10:-11], mm_down_2, "k")
    except ValueError:
        raise FilterError("Filter 2")

    if mov.get():
        ax1.plot(x_use[10:-11], mm, "b")

    return fig


def plot_graphe(fig, axis, name, spike, tp, num_fig, max_scale,
                time_sample, color, unitx):
    """"""
    bx = fig.add_subplot(num_fig)
    Y, signal = spike
    axis_top = max(Y)
    if max_scale != 0:
        axis_top = max_scale
    try:
        X2 = [i*tp/time_sample + signal + axis[0]/time_sample 
              for i in range(len(Y))]
        bx.bar(X2, Y, color=color, width=tp/time_sample)
        bx.axis([axis[0]/time_sample, axis[1]/time_sample, 0, axis_top + 2])
    except ValueError:
        raise TimeperiodError(tp)
    bx.set_xlabel("Time ({})".format(unitx))
    bx.set_ylabel("{}\nFiring rate".format(name))
    bx.grid(True)
    return fig


def occurence(filtre, master):
    """ return the number of occurence number spike/period """

    fig = Figure(figsize=(5, 3), tight_layout=True)
    ax = fig.add_subplot(111)
    fr = filtre.firing_rate()[0]
    mag = [fr.count(i) for i in range(1, max(fr) + 1)]
    frq = [i for i in range(1, max(fr) + 1)]
    ax.bar(frq, mag, align="center", color="yellow")
    ax.set_xlabel("Number spike/period ({} points)".format(filtre.time_period))
    ax.set_ylabel("Number of occurence")
    ax.axis([0.5, max(fr) + 0.5, 0, max(mag) + 2])

    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.show()
    canvas.get_tk_widget().pack()
    return


def fourier(N, T, y, master):
    """
    plot fft for signal

    N = sample point number
    T = sampling spacing
    y = data
    fig = fig to plot on
    """
    fig = Figure(figsize=(5, 3), tight_layout=True)
    x = np.linspace(0.0, N*T, N)
    yf = np.fft.fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
    ax = fig.add_subplot(111)
    ax.plot(xf[1:], 2.0/N*np.abs(yf[0:N/2][1:]))

    ax.set_title("Fast Fourier Transform")
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.show()
    canvas.get_tk_widget().pack()
    return
