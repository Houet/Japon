#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from math import ceil


def import_data(datafile):
    """
    import data
    datafile = file to import

    return first line and list of data
    time of data could be acces with index
    """
    with open(datafile, "r") as f:
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


def number_spike(sp, tp=100):
    """
    sum the number of spike in a time period
    sp = spike recorded as given by spike_detection function
    tp = time period given

    return a list
    number spike /period 1, 2, etc
    """
    return [sp[i:i + tp].count(1) for i in range(0, len(sp), tp)]


# def get_spike_nb(sp):
#     """
#     donne le nombre de spike en tenant compte que
#     01110 n'est qu'une seule spike

#     return a list
#     """
#     tab = [0 for i in range(len(sp))]
#     i = 0
#     while i <= len(sp):
#         if sp[i] == 1:
#             while sp[i] == 1:
#                 tab[i]


def graphe(dlist):
    """
    plot number of occurence of number spike per period
    dlist = number of spike by period (list)

    return a tuple
    number of spike/period, number of occurence
    """
    frq = []
    mag = []
    for i in range(1, max(dlist) + 1):
        frq.append(i)
        mag.append(dlist.count(i))

    return frq, mag


def draw_curb(dt, th=40, st=1, tp=1000, axis=(100, 150)):
    """
    draw curb using matplotlib
    dt = data file to import
    th = threshold to work with
    st = step to work with
    tp = time period
    axis = x axes for drawing

    return the figure to draw
    """
    spike = spike_detection(dt, th, st)

    X = [i/1000 for i in range(len(dt))]

    f = Figure(figsize=(10, 6), dpi=100, tight_layout=True, facecolor="0.90")

    ax1 = f.add_subplot(311)
    ax1.plot(X, dt, "r")
    ax1.set_ylabel("Amplitude ($\mu$V)")
    wind = dt[int(axis[0]*1000):int(axis[1]*1000)]
    ax1.axis([axis[0], axis[1], min(wind)-5, max(wind)+5])
    ax1.grid(True)
    ax2 = ax1.twinx()
    ax2.plot(X, spike, "b")
    ax2.axis([axis[0], axis[1], 0, 1])

    b = f.add_subplot(312)
    Y = number_spike(spike, tp)
    X2 = [i*tp/1000 for i in range(len(Y))]
    b.bar(X2, Y, color="g", width=tp/1000)
    b.axis([axis[0], axis[1], 0, max(Y) + 2])
    b.set_xlabel("Time (s)")
    b.set_ylabel("Firing rate")
    b.grid(True)

    frq, mag = graphe(Y)
    c = f.add_subplot(313)
    c.bar(frq, mag, align="center", color="yellow")
    c.set_xlabel("Number spike/period ({}ms)".format(tp))
    c.set_ylabel("Number of occurence")
    c.axis([0.5, max(frq) + 0.5, 0, max(mag) + 2])
    return f, spike.count(1)


if __name__ == "__main__":
    """ draw curb using matplotlib """

    data = import_data("data2.txt")[1]
    spike = spike_detection(data, 40, 1)

    X = [i/1000 for i in range(len(data))]

    ax1 = plt.subplot(311)
    ax1.plot(X, data, "r")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude ($\mu$V)")
    ax1.axis([100.0, 150, -200, 200])
    ax1.grid(True)
    ax2 = ax1.twinx()
    ax2.plot(X, spike, "b")
    ax2.axis([100.0, 150, 0, 1])
    plt.title("Spike position")

    plt.subplot(313)
    Y = number_spike(spike, 1000)
    print(Y)
    X2 = [i for i in range(len(Y))]
    plt.bar(X2, Y, color="g", width=1)
    # plt.axis([100, 150, 0, 30])
    plt.grid(True)
    plt.title("Number spike by period")
    plt.show()
