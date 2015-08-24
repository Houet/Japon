#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

""" fonction de base pour le programme sdgi main """

from tkinter import *
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FileError(ValueError):
    """ exception raise when trying to use wrong file """
    pass


class FilterError(ValueError):
    """ exception raise when trying to plot a non define filter """
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


class Filtre(object):
    """ Spike detection filter """
    def __init__(self, method=None, threshold=40, time_period=1000, step=1):
        """ methode could be: slope, upper, lower or both """
        self.methode = method
        self.threshold = threshold
        self.time_period = time_period
        self.step = step
        self.tab_spikes = []
        self.number_spikes = self.tab_spikes.count(1)
        self.info_spike = []
        self.moving_average = []

    def get_spike(self, data):
        """ return a tab with 1 when spike is detected, 0 otherwise """
        methode = {"Slope": self.get_spike_slope,
                   "Upper": self.get_spike_upper,
                   "Lower": self.get_spike_lower,
                   "Both": self.get_spike_both,
                   }
        self.ma(data)
        if self.methode != "":
            self.tab_spikes = methode[self.methode](data)
            self.tab_spikes = self.filtre()
        self.number_spikes = self.tab_spikes.count(1)
        self.info_spike = self.get_info(data)
        return self.tab_spikes

    def ma(self, data):
        """
        return
        the moving average of data
        """
        debut = sum(data[:20]) / 20
        for i in range(10, len(data) - 11):
            debut += (data[i + 10 + 1] - data[i - 10 + 1]) / 20
            self.moving_average.append(debut)
        return

    def get_spike_slope(self, data):
        """ get spike with slope method """
        toreturn = [0 for i in range(len(data))]
        for t in range(self.step + 1, len(data)):
            if data[t] - data[t - self.step] < - self.threshold:
                toreturn[t - self.step] = 1
                continue
        return toreturn

    def get_spike_upper(self, data):
        """ get spike with upper method """
        pas = (len(data) - len(self.moving_average)) // 2
        tab = [0 for i in range(len(self.moving_average))]
        for i in range(1, len(self.moving_average)):
            if data[i + pas] > self.moving_average[i] + self.threshold:
                tab[i] = 1
        return tab

    def get_spike_lower(self, data):
        """ get spike with lower method """
        pas = (len(data) - len(self.moving_average)) // 2
        tab = [0 for i in range(len(self.moving_average))]
        for i in range(1, len(self.moving_average)):
            if data[i + pas] < self.moving_average[i] - self.threshold:
                tab[i] = 1
        return tab

    def get_spike_both(self, data):
        """ get spike with both method """
        pas = (len(data) - len(self.moving_average)) // 2
        tab = [0 for i in range(len(self.moving_average))]
        for i in range(1, len(self.moving_average) - pas):
            if data[i + pas] > self.moving_average[i] + self.threshold:
                for j in range(5):
                    if data[i + pas + j] < self.moving_average[i + j] - self.threshold:
                        tab[i] = 1
                        break
        return tab

    def filtre(self):
        """
        transform 01110 signal into 01000 signal
        detect one 'true' spike instead of three
        """
        tab = [0 for i in self.tab_spikes]
        for i in range(1, len(self.tab_spikes)):
            if self.tab_spikes[i] != self.tab_spikes[i-1]:
                if self.tab_spikes[i] == 1:
                    tab[i] = 1
        return tab

    def firing_rate(self):
        """
        sum the number of spike in a time period

        return a list and a signal
        number spike /period 1, 2, etc
        signal is the offset made by moving average,
        len moving average is [10: ..] so you have to be aware of this.
        """
        try:
            tab_y = [self.tab_spikes[i:i + self.time_period].count(1)
                     for i in range(0, len(self.tab_spikes), self.time_period)]
        except ValueError:
            raise TimeperiodError(self.time_period)
        signal = 0
        if self.methode != "Slope" and self.time_period <= 10:
            signal = 0.01
        return tab_y, signal

    def get_info(self, data):
        """
        provide information about spike
        such as spike highest value
        spike lowest value
        time du spike
        """
        # prise en compte du fait que la detection par une methode autre que
        # slope implique un décalage de 10 ms, donc l'offset permet de
        # rattraper cela, et vaut donc 0 quand la methode est slope
        offset = 0
        if self.methode != "Slope":
            data = data[10: -11]
            offset = 10
        tab = []
        for i in range(len(self.tab_spikes)):
            if self.tab_spikes[i] == 1:
                try:
                    tab.append({"time": (i + offset),
                                "highest value": max(data[i - 5: i + 5]),
                                "lowest value": min(data[i - 5: i + 5]),
                                })
                except ValueError:
                    essai = min(len(data[:i]), len(data[i:]), 5)
                    tab.append({"time": (i + offset),
                                "highest value":
                                max(data[i - essai: i + essai]),
                                "lowest value":
                                min(data[i - essai: i + essai]),
                                })
            else:
                tab.append(0)
        return tab


class InfoFiltre(LabelFrame):
    """ small frame with information about filter """
    def __init__(self, parent, info, nb_spike, **kwargs):
        LabelFrame.__init__(self, parent, **kwargs)

        Label(self, text="Method:").grid(column=1, row=1, sticky=W)
        Label(self,
              textvariable=info["method"],
              width=5,
              anchor=E).grid(column=2, row=1, sticky=E)
        Label(self, text="Threshold:").grid(column=1, row=2, sticky=W)
        Label(self, textvariable=info["threshold"]).grid(column=2,
                                                         row=2,
                                                         sticky=E)
        Label(self, text="Time period:").grid(column=1, row=3, sticky=W)
        Label(self, textvariable=info["time_period"]).grid(column=2,
                                                           row=3,
                                                           sticky=E)
        Label(self, text="Step:").grid(column=1, row=4, sticky=W)
        Label(self, textvariable=info["step"]).grid(column=2, row=4, sticky=E)
        Label(self, text="Spike(s) detected:").grid(column=1, row=5, sticky=W)
        Label(self, textvariable=nb_spike).grid(column=2, row=5, sticky=E)


class SettingFiltre(LabelFrame):
    """ small frame where you can set your filter """
    def __init__(self, parent, filtre,  **kwargs):
        LabelFrame.__init__(self, parent, **kwargs)
        self.filtre = filtre

        Label(self, text="Threshold:").grid(column=1, row=1, sticky=W)
        Entry(self,
              textvariable=filtre["threshold"],
              width=5,
              justify="right").grid(column=2, row=1)

        Label(self, text="Time Period:").grid(column=1, row=2, sticky=W)
        Entry(self,
              textvariable=filtre["time_period"],
              width=5,
              justify="right").grid(column=2, row=2)

        Label(self, text="Method:").grid(column=1, row=3, sticky=W)
        self.method = Menubutton(self,
                                 textvariable=filtre["method"],
                                 width=6,
                                 relief=RAISED)
        self.method.menu = Menu(self.method, tearoff=0)
        self.method["menu"] = self.method.menu
        self.method.menu.add_radiobutton(label=None,
                                         variable=filtre["method"],
                                         command=self.action)
        self.method.menu.add_radiobutton(label="Slope",
                                         variable=filtre["method"],
                                         command=self.action)
        self.method.menu.add_radiobutton(label="Upper",
                                         variable=filtre["method"],
                                         command=self.action)
        self.method.menu.add_radiobutton(label="Lower",
                                         variable=filtre["method"],
                                         command=self.action)
        self.method.menu.add_radiobutton(label="Both",
                                         variable=filtre["method"],
                                         command=self.action)
        self.method.grid(column=2, row=3, padx=5, pady=5)

        Label(self, text="Step:").grid(column=1, row=4, sticky=W)
        self.step_entry = Entry(self,
                                textvariable=filtre["step"],
                                width=5,
                                justify="right")
        self.step_entry.grid(column=2, row=4)
        self.action()

        for child in self.winfo_children():
            child.grid_configure(padx=5)

    def action(self):
        """ change the apparence of step entry widget """
        if self.filtre["method"].get() == "Slope":
            self.step_entry.configure(state="normal")
        else:
            self.step_entry.configure(state="disabled")


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
        try:
            time_sample = float(data[1][0]) - float(data[0][0])
        except IndexError:
            raise FileError

    return header, [float(i[1]) for i in data], time_sample
