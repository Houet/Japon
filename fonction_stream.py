#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

""" fonction pour gerer les stream """

import time

from tkinter import *
from tkinter.filedialog import askopenfilename

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from fonction_base import *
from fonction_file import plot_graphe


class Choose(Frame):
    """ choose your filtre for stream """
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.master = master
        self.name = StringVar(self, None)
        self.short_name = StringVar(self, "Search")
        self.filtre = {"method": StringVar(self, "Slope"),
                       "threshold": IntVar(self, 40),
                       "time_period": IntVar(self, 1000),
                       "step": IntVar(self, 1),
                       }
        self.ret = None

        f = SettingFiltre(self, self.filtre)
        f.grid(column=1, columnspan=2, row=1)
        Label(self, text="Stream:").grid(column=1, row=2, sticky=W)
        Button(self,
               textvariable=self.short_name,
               width=9,
               command=self.search,
               relief=SUNKEN,
               bg="white").grid(column=2, row=2, sticky=E)
        Button(self,
               text="Ok",
               width=8,
               command=self.__call__).grid(column=1, columnspan=2, row=4)

        for child in self.winfo_children():
            child.grid_configure(pady=3)

    def search(self):
        self.name.set(askopenfilename(filetypes=[("text file", ".txt")],
                                      parent=self.master,
                                      title="Open a stream"))
        self.short_name.set(self.name.get().split("/")[-1])

    def __call__(self):
        self.ret = Filtre(self.filtre["method"].get(),
                          self.filtre["threshold"].get(),
                          self.filtre["time_period"].get(),
                          self.filtre["step"].get())
        self.quit()
        self.master.destroy()


def ma_fonction(filtre, data, time_sample, grand_master):
    if data == "":
        return
    with open(data, "r") as f:
        header = f.readline()
        fig = Figure(tight_layout=False)
        ax = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude ($\mu$V)")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Firing rate")
        ax.grid(True)
        master = Frame(grand_master)
        master.pack()
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.show()
        canvas.get_tk_widget().pack()
        try:
            spike_detected = 0
            fen_size = 1000
            i = 0
            x = []
            y = []
            for line in f:
                x0, y0 = line.split(",")
                x.append(float(x0))
                y.append(float(y0))
                time.sleep(0.001)
                if i % filtre.time_period == 0:
                    filtre.get_spike(y[i - filtre.time_period:i])
                    ax2.bar((i - filtre.time_period)/time_sample,
                            filtre.tab_spikes.count(1),
                            color="green",
                            width=filtre.time_period/time_sample)

                if i % fen_size == 0:
                    ax.plot(x[-fen_size-1:], y[-fen_size-1:], "b")
                    ax.axis([(i-10*fen_size)/time_sample,
                            (i+2*fen_size)/time_sample, -200, 200])
                    sp = [i*500 - 230 for i
                          in filtre.get_spike(y[-fen_size-1:])]
                    ax.plot(x[-fen_size-1:], sp, "r")

                    spike_detected += filtre.number_spikes

                    signal = 0
                    if filtre.methode != "Slope" and filtre.time_period <= 10:
                        signal = 0.01

                    ax2.set_xlim(0, i/time_sample)
                    ax2.grid(True)
                    canvas.draw()
                i += 1
        except RuntimeError:
            pass
    return
