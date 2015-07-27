#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from math import ceil
from threading import Thread

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

class Indicator():
    def __init__(self, position, master):
        self.un = Canvas(master, width=8, height=8, bg="blue")
        self.deux = Canvas(master, width=8, height=8, bg="blue")
        self.trois = Canvas(master, width=1, height=540, bg="blue")

    def __call__(self, position, master):
        self.trois = Canvas(master, width=1, height=540, bg="blue")
        self.trois.place(x=position-1, y=15, in_=master)
        self.un = Canvas(master, width=8, height=8, bg="blue")
        self.un.place(x=position, y=15, anchor=CENTER, in_=master)
        self.deux = Canvas(master, width=8, height=8, bg="blue")
        self.deux.place(x=position, y=553, anchor=CENTER, in_=master)

    def destroy(self):
        self.un.destroy()
        self.deux.destroy()
        self.trois.destroy()


class ClicPosition():
    def __init__(self, fig, filtre, start, canvas, offset):
        self.ind = 0
        self.f = fig
        self.ax = self.f.get_children()[2]
        fig.canvas.mpl_connect("button_press_event", self)
        self.x = None
        self.name = filtre[0]
        self.filtre = filtre[1]
        self.spike = filtre[1].tab_spikes
        self.start = start
        self.canvas = canvas
        self.label = Label(self.canvas)
        if self.spike != []:
            if self.name == "filter 1":
                self.label.bind_all("<Right>", self.get_next_spike)
                self.label.bind_all("<Left>", self.get_next_spike)
            else:
                self.label.bind_all("<q>", self.get_next_spike)
                self.label.bind_all("<d>", self.get_next_spike)
        self.offset = offset
        self.indicator = Canvas(self.canvas)
        self.indicator2 = Indicator(0, self.canvas)
        # line, = self.ax.plot([i/1000 for i in range(len(self.spike))],
        #                self.spike,
        #                "b")
        # self.ax.draw_artist(line)

    def get_next_spike(self, event):
        """ return next spike ordered by time """
        range_next = (self.ind + 1, len(self.spike), 1)
        if event.keysym == "Left":
            range_next = (self.ind - 1, 0, -1)
        if event.keysym =="q":
            range_next = (self.ind - 1, 0, -1)
        for i in range(range_next[0], range_next[1], range_next[2]):
            if self.spike[i] == 1:
                self.ind = i
                
                self.indicator2.destroy()
                # self.indicator = Canvas(self.canvas, width=8, height=8, bg="blue")
                # self.indicator.place(x=(self.ind*700)/len(self.spike) + 81,
                #                      y=15,
                #                      anchor=CENTER,
                #                      in_= self.canvas)
                self.indicator2((self.ind*700)/len(self.spike) + 81, self.canvas)

                tab_info = self.filtre.info_spike[self.ind]
                self.label.destroy()
                texte = "Filter: {}\nTime: {}\nHighest val: {highest value}\n\
Lowest value: {lowest value}".format(self.name,
                                     (tab_info["time"] + int(self.start*1000))/1000,
                                     **tab_info)
                self.label = Label(self.canvas, text=texte, relief=RIDGE, bg="white")
                coord = [(self.ind*700)/len(self.spike) + 90, 300]
                if coord[0] > 400:
                    coord[0] -= 180
                self.label.place(x=coord[0], y=coord[1])
                break
        return
 
    def __call__(self, event):
        if not event.inaxes:
            return
        self.x = int((event.xdata - self.start)*1000)
        if self.filtre.methode != "Slope":
            self.x -= 10

        hitbox = 10
        if 1 in self.spike[self.x-hitbox: self.x+hitbox]:
            self.indice = self.spike[self.x-hitbox: self.x+hitbox].index(1)
            self.ind = self.x + (self.indice-hitbox)

            self.indicator.destroy()
            self.indicator = Canvas(self.canvas, width=8, height=8, bg="blue")
            self.indicator.place(x=(self.ind*700)/1000 + 81,
                                 y=15,
                                 anchor=CENTER)

            tab_info = self.filtre.info_spike[self.x + (self.indice-hitbox)]
            self.label.destroy()
            texte = "Filter: {}\nTime: {}\nHighest val: {highest value}\n\
Lowest value: {lowest value}".format(self.name,
                                     (tab_info["time"] + int(self.start*1000))/1000,
                                     **tab_info)
            self.label = Label(self.canvas, text=texte, relief=RIDGE, bg="white")
            coord = [event.x + 10, (600 - event.y) + self.offset]
            if event.x > 400:
                coord[0] = event.x - 170
            if event.y > 300:
                coord[1] += 75
                
            self.label.place(x=coord[0], y=coord[1])
        else:
            self.label.destroy()
            self.indicator.destroy()


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
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude ($\mu$V)")
    ax1.grid(True)
    try:
        ax1.axis([axe[0]/1000, axe[1]/1000, axe[2], axe[3]])
    except ValueError:
        raise FileError
    ax1.plot(x_use, d_use, "r")

    ax2 = ax1.twinx()
    ax2.axis([axe[0]/1000, axe[1]/1000, 0, 1])
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
        ax1.plot(x_use[10:-11], mm, "b", ls="--")

    return fig


def plot_graphe(fig, axis, name, spike, tp, num_fig, max_scale, color):
    """"""
    bx = fig.add_subplot(num_fig)
    Y, signal = spike
    axis_top = max(Y)
    if max_scale != 0:
        axis_top = max_scale
    try:
        X2 = [i*tp/1000 + signal + axis[0]/1000 for i in range(len(Y))]
        bx.bar(X2, Y, color=color, width=tp/1000)
        bx.axis([axis[0]/1000, axis[1]/1000, 0, axis_top + 2])
    except ValueError:
        raise TimeperiodError(tp)
    bx.set_xlabel("Time (s)")
    bx.set_ylabel("{}\nFiring rate".format(name))
    bx.grid(True)
    return fig