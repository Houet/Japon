#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

""" fonction pour gerer les stream """

import time
import sys

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
        self.sampling = DoubleVar(self, 0.001)
        self.unitx = StringVar(self, "S")
        self.unity = StringVar(self, chr(956) + "V")
        self.short_name = StringVar(self, "Search")
        self.filtre = {"method": StringVar(self, "Slope"),
                       "threshold": IntVar(self, 40),
                       "time_period": IntVar(self, 1000),
                       "step": IntVar(self, 1),
                       }
        self.ret = None

        f = SettingFiltre(self, self.filtre, text="Set filter: ")
        f.grid(column=3, columnspan=2, row=1, rowspan=4)
        
        Label(self, text="Stream:").grid(column=1, row=1, sticky=W)
        Button(self,
               textvariable=self.short_name,
               width=9,
               command=self.search,
               relief=SUNKEN,
               bg="white").grid(column=2, row=1, sticky=E, padx=5)
        Label(self, text="Sampling Rate:").grid(column=1, row=2, sticky=W)
        Entry(self, textvariable=self.sampling, width=9, justify="right").grid(column=2, row=2, padx=5)

        Label(self, text="Time:").grid(column=1, row=3, sticky=W)
        self.menu_unitx = Menubutton(self,
                                     width=9,
                                     textvariable=self.unitx,
                                     relief=RAISED)
        self.menu_time = Menu(self.menu_unitx, tearoff=0)
        self.menu_time.add_radiobutton(label=(chr(956) + "S"),
                                       variable=self.unitx)
        self.menu_time.add_radiobutton(label="mS", variable=self.unitx)
        self.menu_time.add_radiobutton(label="S", variable=self.unitx)
        self.menu_unitx["menu"] = self.menu_time
        self.menu_unitx.grid(column=2, row=3)
        
        Label(self, text="Amplitude:").grid(column=1, row=4, sticky=W)
        self.menu_unity = Menubutton(self,
                                     width=9,
                                     textvariable=self.unity,
                                     relief=RAISED)
        self.menu_ampl = Menu(self.menu_unity, tearoff=0)
        self.menu_ampl.add_radiobutton(label=(chr(956) + "V"),
                                       variable=self.unity)
        self.menu_ampl.add_radiobutton(label="mV", variable=self.unity)
        self.menu_ampl.add_radiobutton(label="V", variable=self.unity)
        self.menu_unity["menu"] = self.menu_ampl
        self.menu_unity.grid(column=2, row=4)

        Button(self,
               text="Ok",
               width=8,
               command=self.__call__).grid(column=2, columnspan=2, row=5, pady=3)

        # for child in self.winfo_children():
        #     child.grid_configure(pady=3)

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

        self.unitx = self.unitx.get()
        self.unity = self.unity.get()
        if self.unitx != "S" and self.unitx != "mS":
            self.unitx = "$\mu$S"
        if self.unity != "V" and self.unity != "mV":
            self.unity = "$\mu$V"

        self.quit()
        self.master.destroy()


def ma_fonction(grand_master, filtre, data, sampling, unitx, unity):
    if data == "":
        return
    with open(data, "r") as f:
        header = f.readline()
        sampling = 1 / sampling
        fig = Figure(tight_layout=False)
        ax = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        ax.set_xlabel("Time ({})".format(unitx))
        ax.set_ylabel("Amplitude ({})".format(unity))
        ax2.set_xlabel("Time ({})".format(unitx))
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
                    ax.plot(x[-fen_size:], y[-fen_size:], "b")
                    sp = [i*500 - 230 for i
                          in filtre.get_spike(y[-fen_size:])]
                    if filtre.methode != "Slope":
                        ax.plot(x[-fen_size+10:-10], sp, "r")
                    else:
                        ax.plot(x[-fen_size:], sp, "r")

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

    root = Tk(screenName="Stream")
    ma_fonction(root, *signal[1:])
    root.mainloop()
    return
