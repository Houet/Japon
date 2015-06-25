#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt


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
            toreturn[t] = 1
            continue
    return toreturn


if __name__ == "__main__":
    """ draw curb using matplotlib """

    data = import_data("data.txt")[1]
    spike = spike_detection(data, 40)
    X = [i/1000 for i in range(len(data))]

    ax1 = plt.subplot(211)
    ax1.plot(X, data, "r")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude ($\mu$V)")
    ax1.axis([100.0, 150, -200, 200])
    ax2 = ax1.twinx()
    ax2.plot(X, spike, "b")
    ax2.axis([100.0, 150, 0, 1])
    plt.title("spike position")
    plt.show()
