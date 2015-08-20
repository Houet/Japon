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

import sys


class Choose(Frame):
    """ choose your filtre for stream """
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.master = master
        self.name = StringVar(self, None)
        self.sampling = DoubleVar(self, 0.001)
        self.short_name = StringVar(self, "Search")
        self.filtre = {"method": StringVar(self, "Slope"),
                       "threshold": IntVar(self, 40),
                       "time_period": IntVar(self, 1000),
                       "step": IntVar(self, 1),
                       }
        self.ret = None

        f = SettingFiltre(self, self.filtre, text="Set filter: ")
        f.grid(column=1, columnspan=2, row=1)
        Label(self, text="Stream:").grid(column=1, row=2, sticky=W)
        Button(self,
               textvariable=self.short_name,
               width=9,
               command=self.search,
               relief=SUNKEN,
               bg="white").grid(column=2, row=2, sticky=E)
        Label(self, text="Sampling Rate:").grid(column=1, row=3, sticky=W)
        Entry(self, textvariable=self.sampling, width=5, justify="right").grid(column=2, row=3, sticky=E)
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


def ma_fonction(grand_master, filtre, data, sampling):
    if data == "":
        return
    with open(data, "r") as f:
        header = f.readline()
        sampling = 1 / sampling
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

                if i != 0 and i % filtre.time_period == 0:
                    filtre.get_spike(y[i - filtre.time_period:i])
                    ax2.set_xlim(0, i/sampling)
                    ax2.bar((i - filtre.time_period)/sampling,
                            filtre.tab_spikes.count(1),
                            color="green",
                            width=filtre.time_period/sampling)
                    ax2.grid(True)

                if i != 0 and i % fen_size == 0:
                    ax.axis([(i-10*fen_size)/sampling,
                            (i+2*fen_size)/sampling, -200, 200])
                    ax.plot(x[-fen_size-1:], y[-fen_size-1:], "b")
                    sp = [i*500 - 230 for i
                          in filtre.get_spike(y[-fen_size-1:])]
                    ax.plot(x[-fen_size-1:], sp, "r")

                    spike_detected += filtre.number_spikes

                    signal = 0
                    if filtre.methode != "Slope" and filtre.time_period <= 10:
                        signal = 0.01

                    canvas.draw()
                # time.sleep(0.001)
                i += 1
        except RuntimeError:
            pass
    return


def stream_handler(pipe_entry):
    """ fonction which is supposed to handle the stream """
    flag = False
    while not flag:
        try:
            signal = pipe_entry.recv()
            if signal[0] == 1:
                flag = True
        except RuntimeError:
            pass
        except KeyboardInterrupt:
            sys.exit(0)

    root = Tk()
    root.title("Stream")
    ma_fonction(root, *signal[1:])
    root.mainloop()
    return
