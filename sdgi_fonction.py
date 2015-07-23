#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from math import ceil

from tkinter import *


class FileError(ValueError):
    """ exception raise when trying to use wrong file """
    pass


class FilterError(ValueError):
    """ execption raise when trying to plot a non define filter """
    def __init__(self, filtre):
        self.filtre = filtre
    def __str__(self):
        return self.filtre


class TimeperiodError(ValueError):
    """ exception raise when time period value is unvalid """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "{}".format(self.value)


class ClicPosition():
    def __init__(self, fig, filtre, start, canvas, offset):
        fig.canvas.mpl_connect("button_press_event", self)
        self.x = None
        self.name = filtre[0]
        self.filtre = filtre[1]
        self.spike = filtre[1].tab_spikes
        self.start = start
        self.canvas = canvas
        self.label = Label(self.canvas)
        self.offset = offset
        
    def __call__(self, event):
        if not event.inaxes:
            return
        self.x = int((event.xdata - self.start)*1000)
        if self.filtre.methode != "Slope":
            self.x -= 10

        if 1 in self.spike[self.x-5: self.x+5]:
            indice = self.spike[self.x-5: self.x+5].index(1)
            
            tab_info = self.filtre.info_spike[self.x + (indice-5)]
            self.label.destroy()
            texte = "Filter: {}\nTime: {}\nHighest val: {highest value}\n\
Lowest value: {lowest value}".format(self.name,
                                     (tab_info["time"] + int(self.start*1000))/1000,
                                     **tab_info)
            self.label = Label(self.canvas, text=texte, relief=RIDGE, bg="white")
            if event.x < 400:
                self.label.place(x=event.x + 10, y=(600 - event.y) + self.offset)
            else:
                self.label.place(x=event.x - 170, y=(600 - event.y) + self.offset)
        else:
            self.label.destroy()


def load_file(fname):
    """
    import data
    fname = file to import

    return first line and list of data
    time of data could be acces with index
    """
    with open(fname, "r") as f:
        data = [line.split(",") for line in f]
        header = data.pop(0)
    return header, [float(i[1]) for i in data]


def plot(dat, axe, fig_number, filter1, filter2, mm, th1, th2,
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

    X = [i/1000 for i in range(len(dat))]
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
    mm_up_1 = [ i + th1 for i in mm]
    mm_down_1 = [ i - th1 for i in mm]
    mm_up_2 = [ i + th2 for i in mm]
    mm_down_2 = [ i - th2 for i in mm]

    ax1 = fig.add_subplot(fig_number)
    ax1.set_ylabel("Amplitude ($\mu$V)")
    ax1.grid(True)
    try:
        ax1.axis([axe[0]/1000, axe[1]/1000, min(d_use)-10, max(d_use)+10])
    except ValueError:
        raise FileError
    ax1.plot(x_use, d_use, "r")

    ax2 = ax1.twinx()
    ax2.axis([axe[0]/1000, axe[1]/1000, 0, 1])

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
        ax1.plot(x_use[10:-11], mm, "b", ls="--")



    return fig


def plot_graphe(fig, axis, name, spike, tp, num_fig, color):
    """"""
    bx = fig.add_subplot(num_fig)
    Y, signal = spike
    try:
        X2 = [i*tp/1000 + signal + axis[0]/1000 for i in range(len(Y))]
        bx.bar(X2, Y, color=color, width=tp/1000)
        bx.axis([axis[0]/1000, axis[1]/1000, 0, max(Y) + 2])
    except ValueError:
        raise TimeperiodError(tp)
    bx.set_xlabel("Time (s)")
    bx.set_ylabel("{}\nFiring rate".format(name))
    bx.grid(True)
    return fig