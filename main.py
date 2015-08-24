#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showwarning

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from webbrowser import open as wbopen
from multiprocessing import Process, Pipe, Queue
from threading import Thread

from fonction_base import *
from fonction_file import *
from fonction_stream import *


class Sdgi(Frame):
    """ Spike Detection Graphic Interface """
    def __init__(self, window, pipe_entry, **kwargs):
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.window = window

        self.communication = pipe_entry
        
        self.fname = StringVar(self, None)
        self.fshortname = StringVar(self, None)
        self.flenght = IntVar(self, None)

        self.unitx = StringVar(self, "S")
        self.unity = StringVar(self, chr(956) + "V")

        self.time = {
                    "start": DoubleVar(self, 0),
                    "end": DoubleVar(self, 0),
                    }
        self.amplitude = {
                          "start": IntVar(self, 0),
                          "end": IntVar(self, 0),
                         }
        self.options = {
                        "f1": BooleanVar(self, False),
                        "f2": BooleanVar(self, False),
                        "mov": BooleanVar(self, False),
                        "mov_up_1": BooleanVar(self, False),
                        "mov_down_1": BooleanVar(self, False),
                        "mov_up_2": BooleanVar(self, False),
                        "mov_down_2": BooleanVar(self, False),
                        }
        self.firing_rate = BooleanVar(self, False)
        self.fr_adjust = BooleanVar(self, False)
        self.occur = BooleanVar(self, False)
        self.filter1 = {
                        "method": StringVar(self, "Slope"),
                        "threshold": IntVar(self, 40),
                        "time_period": IntVar(self, 1000),
                        "step": IntVar(self, 1),
                        }
        self.filter2 = {
                        "method": StringVar(self, None),
                        "threshold": IntVar(self, 40),
                        "time_period": IntVar(self, 1000),
                        "step": IntVar(self, 1),
                        }
        self.spike_detected = {
                                "filter1_nb":IntVar(self, 0),
                                "filter2_nb":IntVar(self, 0),
                                }

        ########################################################################
        ####################            menu bar            ####################
        ########################################################################
        
        self.menubar = Menu(self)
        self.sousmenu = Menu(self.menubar, tearoff=0)
        self.sousmenu.add_command(label="File",
                                 command=self.open,
                                 accelerator="Ctrl + O")
        self.sousmenu.add_command(label="Stream",
                                  command=self.open_stream,
                                  accelerator="Ctrl + S")
        self.menubar.add_cascade(label="Open", menu=self.sousmenu)

        self.menubar.add_command(label="Stream",
                                 command=self.open_stream)

        self.menu_setting = Menu(self.menubar, tearoff=0)
        self.menu_time = Menu(self.menu_setting, tearoff=0)
        self.menu_time.add_radiobutton(label=(chr(956) + "S"),
                                       variable=self.unitx)
        self.menu_time.add_radiobutton(label="mS", variable=self.unitx)
        self.menu_time.add_radiobutton(label="S", variable=self.unitx)
        
        self.menu_ampl = Menu(self.menu_setting, tearoff=0)
        self.menu_ampl.add_radiobutton(label=(chr(956) + "V"),
                                       variable=self.unity)
        self.menu_ampl.add_radiobutton(label="mV", variable=self.unity)
        self.menu_ampl.add_radiobutton(label="V", variable=self.unity)

        self.menu_setting.add_cascade(label="Time",
                                      menu=self.menu_time)
        self.menu_setting.add_cascade(label="Amplitude",
                                      menu=self.menu_ampl)
        self.menubar.add_cascade(label="Settings", menu=self.menu_setting)
        
        self.menubar.add_command(label="Help", command=self.help)
        self.window.config(menu=self.menubar)
        self.menubar.bind_all("<Control-o>", self.open)
        self.menubar.bind_all("<Control-s>", self.open_stream)

        ########################################################################
        ####################       frame for drawing        ####################
        ########################################################################
        
        self.plotframe = Frame(self, width=8*100+10, height=6*100)
        self.plotframe.grid(column=1, row=1, rowspan=4)

        ########################################################################
        ####################     frame for information      ####################
        ########################################################################
        
        self.infoframe = LabelFrame(self, text="Infos", width=30)
        self.infoframe.grid(column=2, row=1, padx=5, sticky=N)

        Label(self.infoframe,
              text="File name:").grid(column=1, row=1, sticky=W)
        Label(self.infoframe,
              text="File length:").grid(column=1, row=2, sticky=W)

        Label(self.infoframe,
              textvariable=self.fshortname).grid(column=2, row=1, sticky=E)
        Label(self.infoframe,
              textvariable=self.flenght).grid(column=2, row=2, sticky=E)

        InfoFiltre(self.infoframe,
                   self.filter1,
                   self.spike_detected["filter1_nb"],
                   text="Filter 1",
                   width=15).grid(column=1, row=3, sticky=W)

        InfoFiltre(self.infoframe,
                   self.filter2,
                   self.spike_detected["filter2_nb"],
                   text="Filter 2",
                   width=15).grid(column=2, row=3, sticky=E)

        for child in self.infoframe.winfo_children():
            child.grid_configure(padx=5, pady=3)

        ########################################################################
        ####################       frame for options        ####################
        ########################################################################

        self.optionframe = LabelFrame(self, text="Display Options", width=30)
        self.optionframe.grid(column=2, row=2, sticky=N, padx=5)

        Label(self.optionframe,
              text="Starting time:").grid(column=1, row=1, sticky=W)        
        self.start_time = Entry(self.optionframe,
                                textvariable=self.time["start"],
                                justify="right",
                                width=8)
        self.start_time.grid(column=2, row=1, sticky=W)

        Label(self.optionframe,
              text="Ending time:").grid(column=1, row=2, sticky=W)      
        self.end_time = Entry(self.optionframe,
                                textvariable=self.time["end"],
                                justify="right",
                                width=8)
        self.end_time.grid(column=2, row=2, sticky=W)

        Label(self.optionframe,
              text="Amplitude:").grid(column=3, row=1, sticky=W)
        self.ampl_start = Entry(self.optionframe,
                                textvariable=self.amplitude["start"],
                                justify="right",
                                width=10)
        self.ampl_start.grid(column=4, row=1, sticky=W)

        self.ampl_end = Entry(self.optionframe,
                                textvariable=self.amplitude["end"],
                                justify="right",
                                width=10)
        self.ampl_end.grid(column=4, row=2, sticky=W)

        self.filter_check1 = Checkbutton(self.optionframe,
                                   text="Filter 1",
                                   justify="left",
                                   var=self.options["f1"])
        self.filter_check1.grid(column=1, columnspan=2, row=3, sticky=W)
        self.filter_check2 = Checkbutton(self.optionframe,
                                   text="Filter 2",
                                   var=self.options["f2"])
        self.filter_check2.grid(column=3, columnspan=2, row=3, sticky=W)
        self.ma_up1 = Checkbutton(self.optionframe,
                                 text="Filter 1 Threshold up",
                                 var=self.options["mov_up_1"])
        self.ma_up1.grid(column=1, columnspan=2, row=4, sticky=W)
        self.ma_down1 = Checkbutton(self.optionframe,
                                   text="Filter 1 Threshold down",
                                   var=self.options["mov_down_1"])
        self.ma_down1.grid(column=1, columnspan=2, row=5, sticky=W)
        self.ma_up2 = Checkbutton(self.optionframe,
                                 text="Filter 2 Threshold up",
                                 var=self.options["mov_up_2"])
        self.ma_up2.grid(column=3, columnspan=2, row=4, sticky=W)
        self.ma_down2 = Checkbutton(self.optionframe,
                                   text="Filter 2 Threshold down",
                                   var=self.options["mov_down_2"])
        self.ma_down2.grid(column=3, columnspan=2, row=5, sticky=W)
        self.ma = Checkbutton(self.optionframe,
                              text="Moving average",
                              var=self.options["mov"])
        self.ma.grid(column=3, columnspan=2, row=6, sticky=W)

        self.fr = Checkbutton(self.optionframe,
                              text="Firing rate",
                              var=self.firing_rate)
        self.fr.grid(column=1, columnspan=2, row=6, sticky=W)

        self.fr_scale = Checkbutton(self.optionframe,
                                    text="Equal F.R. Scale",
                                    var=self.fr_adjust)
        self.fr_scale.grid(column=1, columnspan=2, row=7, sticky=W)

        self.graphe = Checkbutton(self.optionframe,
                                  text="More",
                                  var=self.occur)
        self.graphe.grid(column=3, columnspan=2, row=7, sticky=W)

        for child in self.optionframe.winfo_children():
            child.grid_configure(padx=3, pady=3)

        ########################################################################
        ####################       frame for filters        ####################
        ########################################################################

        self.filterframe = LabelFrame(self, text="Spikes Filters", width=30)
        self.filterframe.grid(column=2, row=3, sticky=N)
        
        SettingFiltre(self.filterframe,
                      self.filter1,
                      text="Filter 1",
                      width=15).pack(side=LEFT)

        SettingFiltre(self.filterframe,
                      self.filter2,
                      text="Filter 2",
                      width=15).pack(side=LEFT)

        for child in self.filterframe.winfo_children():
            child.pack_configure(padx=5, pady=5)

        ########################################################################
        ####################       frame for button         ####################
        ########################################################################

        self.buttonframe = Frame(self, width=30)
        self.buttonframe.grid(column=2, row=4, sticky=N)

        Button(self.buttonframe,
               text="Refresh",
               command=self.refresh,
               width=15,
               height=4).grid(column=1, row=1, rowspan=2)
        Button(self.buttonframe,
               text="Save",
               command=self.save,
               width=15).grid(column=2, row=1)
        Button(self.buttonframe,
               text="Quit",
               command=self.window.destroy,
               width=15).grid(column=2, row=2)

        for child in self.buttonframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    ############################################################################
    ############################################################################
    ######################        menu method         ##########################
    ############################################################################
    ############################################################################

    def open(self, *args):
        """
        open a file on your computer
        return data
        """
        self.fname.set(askopenfilename(filetypes=[("text file", ".txt")],
                                       parent=self.window,
                                       title="Open a file"))
        try:
            self.data, self.time_sample = load_file(self.fname.get())[1:]
            self.time_sample = 1 / self.time_sample
        except FileNotFoundError:
            pass
        else:
            self.fshortname.set(self.fname.get().split("/")[-1])
            self.flenght.set(len(self.data) / self.time_sample)
            self.time["start"].set(0)
            self.time["end"].set(self.flenght.get())
            self.amplitude["start"].set(min(self.data) - 10)
            self.amplitude["end"].set(max(self.data) + 10)
            self.refresh()
        return

    def open_stream(self, *args):
        """ open a stream """
        wind_info = Toplevel(self.window)
        wind_info.geometry("+300+100")
        wind_info.focus()
        wind_info.title("Stream")
        filtre_stream = Choose(wind_info)
        wind_info.mainloop()

        if not filtre_stream.name.get() in ["Search", None, ""]:
            self.communication.send([1,
                                     filtre_stream.ret,
                                     filtre_stream.name.get(),
                                     filtre_stream.sampling.get()])

        return

    def help(self):
        """ return https://github.com/Houet/Japon """
        return wbopen("https://github.com/Houet/Japon")
    
    ############################################################################
    ############################################################################
    ######################       button method        ##########################
    ############################################################################
    ############################################################################

    def refresh(self):
        """ """
        for widget in self.window.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()

        for w in self.plotframe.winfo_children():
            w.destroy()

        try:
            self.cl1.info.destroy()
            del(self.cl1)
            self.cl2.info.destroy()
            del(self.cl2)
        except AttributeError:
            pass

        
        filtre1 = Filtre(self.filter1["method"].get(),
                         self.filter1["threshold"].get(),
                         self.filter1["time_period"].get(),
                         self.filter1["step"].get())

        filtre2 = Filtre(self.filter2["method"].get(),
                         self.filter2["threshold"].get(),
                         self.filter2["time_period"].get(),
                         self.filter2["step"].get())
        
        try:
            self.fig = self.plot(filtre1, filtre2)
        except AttributeError:
            showwarning(title="Error",
                        message="No data to plot...",
                        parent=self.window)
        except TimeperiodError as t:
            showwarning(title="Error",
                        message="Incorrect value for time period:{}".format(t),
                        parent=self.window)
        except IndexError:
            showwarning(title="Error",
                        message="Incorrect value for step",
                        parent=self.window)
        except FilterError as f:
            showwarning(title="Error",
                        message="Can't plot {}".format(f),
                        parent=self.window)
        except FileError:
            showwarning(title="Error",
                        message="Issue with axis or uncompatible file...",
                        parent=self.window)
        else:
            canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)
            canvas.show()
            canvas.get_tk_widget().pack()

            self.cl1 = ClicPosition(self,
                        self.fig,
                        canvas,
                        ("Filter 1", filtre1),
                        self.time["start"].get(),
                        self.time_sample,
                        self.plotframe)

            
            self.cl2 = ClicPosition(self,
                        self.fig,
                        canvas,
                        ("Filter 2", filtre2),
                        self.time["start"].get(),
                        self.time_sample,
                        self.plotframe)

            if self.occur.get():
                wind = Toplevel(self.window)
                wind.geometry("+300+100")
                wind.focus()
                oc = Frame(wind)
                oc.pack(side=LEFT)
                occurence(filtre1, oc)
                ft = Frame(wind)
                ft.pack(side=LEFT)
                fourier(len(self.data), 1.0 / self.time_sample, self.data, ft)
                wind.mainloop()

        return

    def save(self):
        """ save plot """
        try:
            self.fig.savefig("{}.png".format(self.fname.get()))
            showinfo(title="Info",
                     message="Plot save !",
                     parent=self.window)
        except AttributeError:
            showwarning(title="Error",
                        message="No plot to save...",
                        parent=self.window)
        return

    ############################################################################
    ############################################################################
    ######################        other method         #########################
    ############################################################################
    ############################################################################

    def plot(self, filtre1, filtre2):
        """ plot the figure """

        axe = [int(self.time["start"].get() * self.time_sample),
               int(self.time["end"].get() * self.time_sample)]
        d_use = self.data[axe[0]:axe[1]]

        axe.append(self.amplitude["start"].get())
        axe.append(self.amplitude["end"].get())

        numero = 111
        if self.firing_rate.get():
            numero = 311
            if self.filter2["method"].get() == "":
                if self.filter1["method"].get() != None:
                    numero = 211
            elif self.filter1["method"].get() == "":
                if self.filter2["method"].get() != None:
                    numero = 211

        fig = plot(self.data,
                   axe,
                   self.time_sample,
                   numero,
                   filtre1.get_spike(d_use),
                   filtre2.get_spike(d_use),
                   filtre1.moving_average,
                   self.filter1["threshold"].get(),
                   self.filter2["threshold"].get(),
                   self.unitx.get(),
                   self.unity.get(),
                   **self.options)

        self.spike_detected["filter1_nb"].set(filtre1.number_spikes)
        self.spike_detected["filter2_nb"].set(filtre2.number_spikes)
        
        if numero == 211:
            if self.filter1["method"].get() != "":
                plot_graphe(fig, axe[:2],
                            "Filter 1",
                            filtre1.firing_rate(),
                            filtre1.time_period,
                            212,
                            0,
                            self.time_sample,
                            "y",
                            self.unitx.get())
            else:
                plot_graphe(fig,
                            axe[:2],
                            "Filter 2",
                            filtre2.firing_rate(),
                            filtre2.time_period,
                            212,
                            0,
                            self.time_sample,
                            "g",
                            self.unitx.get())
        max_scale = 0
        if numero == 311:  
            if self.fr_adjust.get() == True:
                max_scale = max(max(filtre1.firing_rate()[0]),
                                max(filtre2.firing_rate()[0]))
            plot_graphe(fig,
                        axe[:2],
                        "Filter 1",
                        filtre1.firing_rate(),
                        filtre1.time_period,
                        312,
                        max_scale,
                        self.time_sample,
                        "y",
                        self.unitx.get())
            plot_graphe(fig,
                        axe[:2],
                        "Filter 2",
                        filtre2.firing_rate(),
                        filtre2.time_period,
                        313,
                        max_scale,
                        self.time_sample,
                        "g",
                        self.unitx.get())

        return fig


if __name__ == "__main__":
    ruler, slave = Pipe()
    sentinelle = Process(target=stream_handler, args=(slave,))
    sentinelle.start() 

    root = Tk()
    root.title("Spike Detection Graphical Interface")
    
    fenetre = Sdgi(root, ruler)
    root.mainloop()
    sentinelle.terminate()
