#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from math import ceil


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


def spike_detection(rs, th, step=1):
    """
    record spike position from a signal
    rs = recorded signal
    step = time between two comparison in ms
    th = detection threshold

    return a list where
    1 is when a spike is detected
    0 when not detected
    """
    toreturn = [0 for i in range(len(rs))]
    for t in range(1, len(rs), step):
        if rs[t] - rs[t - 1] < - th:
            toreturn[t - 1] = 1
            continue
    return toreturn


def mm(data, th):
    """
    return 
    the moving average of data
    moving average + threshold
    moving average - threshold
    """
    tab = []
    tabth = []
    tab_th = []
    debut = sum(data[:20])/20
    for i in range(10, len(data)-11):
        debut += (data[i+10 +1] - data[i-10 +1])/20
        tab.append(debut)
        tabth.append(debut + th)
        tab_th.append(debut - th)
    return tab, tabth, tab_th


def get_upper(data, mm):
    """
    gets spikes using moving average
    """
    tab = []
    for i in range(len(mm)):
        if data[i+10] > mm[i]:
            tab.append(1)
        else:
            tab.append(0)
    return tab

def get_lower(data, mm):
    """
    gets spikes using moving average
    """
    tab = []
    for i in range(len(mm)):
        if data[i+10] < mm[i]:
            tab.append(1)
        else:
            tab.append(0)
    return tab

def get_double_ekips(data, mm):
    """
    get spike which are higher than moving average + threshold
    and smaller than moving average - threshold
    """
    tab = [0 for i in range(len(mm[0]))]
    for i in range(len(mm[0])-10):
        if data[i+10] > mm[1][i]:
            for j in range(5):
                if data[i+10+j] < mm[2][i+j]:
                    tab[i]=1
                    break
    return tab


def filtre(sp):
    """
    transform 01110 signal into 01000 signal
    detect one 'true' spike instead of three
    """
    tab = [0 for i in sp]
    for i in range(1, len(sp)):
        if sp[i] != sp[i-1] and sp[i] == 1:
                tab[i] = 1
    return tab


def number_spike(sp, tp=100):
    """
    sum the number of spike in a time period
    sp = spike recorded as given by spike_detection function
    tp = time period given

    return a list
    number spike /period 1, 2, etc
    """
    return [sp[i:i + tp].count(1) for i in range(0, len(sp), tp)]


def plot(dat, axe, fig_number, filter1, filter2, th1, th2, f1=False, f2=False, mov=False, mov_up_1=False, mov_down_1=False, mov_up_2=False, mov_down_2=False):
    """
    trace la figure comme il faut 
    fig =  figure sur laquelle tracer
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

    ax1 = fig.add_subplot(fig_number)
    ax1.set_ylabel("Amplitude ($\mu$V)")
    ax1.grid(True)
    ax1.axis([axe[0]/1000, axe[1]/1000, min(d_use)-10, max(d_use)+10])
    ax1.plot(x_use, d_use, "r")

    ax2 = ax1.twinx()
    ax2.axis([axe[0]/1000, axe[1]/1000, 0, 1])

    if f1.get():
        ax2.plot(x_use_1, filter1, "y")

    if f2.get():
        ax2.plot(x_use_2, filter2, "g")

    if mov.get():
        ax1.plot(x_use[10:-11], mm(d_use, th1)[0], "b", ls="--")

    if mov_up_1.get():
        ax1.plot(x_use[10:-11], mm(d_use, th1)[1], "b")

    if mov_down_1.get():
        ax1.plot(x_use[10:-11], mm(d_use, th1)[2], "b")

    if mov_up_2.get():
        ax1.plot(x_use[10:-11], mm(d_use, th2)[1], "k")

    if mov_down_2.get():
        ax1.plot(x_use[10:-11], mm(d_use, th2)[2], "k")

    return fig


def plot_graphe(fig, axis, name, spike, tp, num_fig, color):
    """"""
    bx = fig.add_subplot(num_fig)
    Y = number_spike(spike, tp)
    X2 = [i*tp/1000 + axis[0]/1000 for i in range(len(Y))]
    bx.bar(X2, Y, color=color, width=tp/1000)
    bx.axis([axis[0]/1000, axis[1]/1000, 0, max(Y) + 2])
    bx.set_xlabel("Time (s)")
    bx.set_ylabel("{}\nFiring rate".format(name))
    bx.grid(True)
    return fig