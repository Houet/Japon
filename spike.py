#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


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


def spike_detection(rs, th, step=4):
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
    data = import_data(dt)[1]
    spike = spike_detection(data, th, st)

    X = [i/tp for i in range(len(data))]

    f = Figure(figsize=(8, 5), dpi=100)

    ax1 = f.add_subplot(211)
    ax1.plot(X, data, "r")
    ax1.set_ylabel("Amplitude ($\mu$V)")
    ax1.axis([axis[0], axis[1], -200, 200])
    ax1.grid(True)
    ax2 = ax1.twinx()
    ax2.plot(X, spike, "b")
    ax2.axis([axis[0], axis[1], 0, 1])

    b = f.add_subplot(212)
    b.bar(range(len(data)//tp), number_spike(spike, tp),
          color="g", width=1)
    b.axis([axis[0], axis[1], 0, 30])
    b.set_xlabel("Time (s)")
    b.grid(True)
    return f


if __name__ == "__main__":
    """ draw curb using matplotlib """

    data = import_data("data.txt")[1]
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
    plt.bar(range(len(data)//1000), number_spike(spike, 1000),
            color="g", width=1)
    plt.axis([100, 150, 0, 30])
    plt.grid(True)
    plt.title("Number spike by period")
    plt.show()
