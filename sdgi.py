#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a graphical interface for data analysis.
Data required are date coming from brain signal.
This programm detected spike in data and plot some interesting thing
such as : moving average, number of spike/period of time, etc, 
additional documentation can be find here: https://github.com/Houet/Japon
"""


from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showwarning

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from webbrowser import open as wbopen

from sdgi_fonction import *


class Filtre(object):
    """ filtre de detection de spike """
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
        methode = { 
                    "Slope": self.get_spike_slope,
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
        debut = sum(data[:20])/20
        for i in range(10, len(data)-11):
            debut += (data[i+10 +1] - data[i-10 +1])/20
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
            if data[i  + pas] > self.moving_average[i] + self.threshold:
                for j in range(5):
                    if data[i + pas + j] < self.moving_average[i + j] - self.threshold:
                        tab[i]=1
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
        tab_y = [self.tab_spikes[i:i + self.time_period].count(1) 
                for i in range(0, len(self.tab_spikes), self.time_period)]
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
        # slope implique un décalage de 10 ms, donc l'offset permet de rattraper
        # cela, et vaut donc 0 quand la methode est slope
        offset = 0
        if self.methode != "Slope":
            data = data[10:-11]
            offset = 10
        tab = []
        for i in range(len(self.tab_spikes)):
            if self.tab_spikes[i] == 1:
                try :
                    tab.append({
                            "time": (i + offset)/1000,
                             "highest value": max(data[i - 5: i + 5]),
                            "lowest value": min(data[i - 5: i + 5]),
                            })
                except ValueError:
                    # print("i", i)
                    essai = min(len(data[:i]), len(data[i:]), 5)
                    # print("essai avec :", essai)
                    tab.append({
                            "time": (i + offset)/1000,
                             "highest value": max(data[i - essai: i + essai]),
                            "lowest value": min(data[i - essai: i + essai]),
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


class Sdgi(Frame):
    """ Spike Detection Graphic Interface """
    def __init__(self, window, **kwargs):
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.window = window
        
        self.fname = StringVar(self, None)
        self.fshortname = StringVar(self, None)
        self.flenght = StringVar(self, None)

        self.time = {
                    "start": DoubleVar(self, 0),
                    "end": DoubleVar(self, 0),
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
        self.menubar.add_command(label="Open",
                                 command=self.open,
                                 accelerator="Ctrl + O")
        self.menubar.add_command(label="Help", command=self.help)
        self.window.config(menu=self.menubar)
        self.menubar.bind_all("<Control-o>", self.open)

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
              text="File lenght:").grid(column=1, row=2, sticky=W)

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
            child.grid_configure(padx=5, pady=5)

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
        self.start_time.grid(column=2, row=1, sticky=E)

        Label(self.optionframe,
              text="Ending time:").grid(column=1, row=2, sticky=W)      
        self.end_time = Entry(self.optionframe,
                                textvariable=self.time["end"],
                                justify="right",
                                width=8)
        self.end_time.grid(column=2, row=2, sticky=E)

        self.filter_check1 = Checkbutton(self.optionframe,
                                   text="Filter 1",
                                   justify="left",
                                   var=self.options["f1"])
        self.filter_check1.grid(column=1, row=3, sticky=W)
        self.filter_check2 = Checkbutton(self.optionframe,
                                   text="Filter 2",
                                   var=self.options["f2"])
        self.filter_check2.grid(column=2, row=3, sticky=W)
        self.ma = Checkbutton(self.optionframe,
                              text="Moving average",
                              var=self.options["mov"])
        self.ma.grid(column=2, row=4, sticky=W)
        self.ma_up1 = Checkbutton(self.optionframe,
                                 text="Filter 1 Threshold up",
                                 var=self.options["mov_up_1"])
        self.ma_up1.grid(column=1, row=5, sticky=W)
        self.ma_down1 = Checkbutton(self.optionframe,
                                   text="Filter 1 Threshold down",
                                   var=self.options["mov_down_1"])
        self.ma_down1.grid(column=1, row=6, sticky=W)
        self.ma_up2 = Checkbutton(self.optionframe,
                                 text="Filter 2 Threshold up",
                                 var=self.options["mov_up_2"])
        self.ma_up2.grid(column=2, row=5, sticky=W)
        self.ma_down2 = Checkbutton(self.optionframe,
                                   text="Filter 2 Threshold down",
                                   var=self.options["mov_down_2"])
        self.ma_down2.grid(column=2, row=6, sticky=W)

        self.fr = Checkbutton(self.optionframe,
                              text="Firing rate",
                              var=self.firing_rate)
        self.fr.grid(column=1, row=4, sticky=W)

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
               command=self.quit,
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
            self.data = load_file(self.fname.get())[1]
        except FileNotFoundError:
            pass
        else:
            self.fshortname.set(self.fname.get().split("/")[-1])
            self.flenght.set(len(self.data)/1000)
            self.time["start"].set(0)
            self.time["end"].set(self.flenght.get())
            self.refresh()
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
        for w in self.plotframe.winfo_children():
            w.destroy()
        
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
        except FilterError as f:
            showwarning(title="Error",
                        message="Can't plot {}".format(f),
                        parent=self.window)
        except FileError:
            showwarning(title="Error",
                        message="Wrong file...",
                        parent=self.window)
        else:
            canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)
            canvas.show()
            canvas.get_tk_widget().pack()

            ClicPosition(self.fig,
                        ("filter 1", filtre1),
                        self.time["start"].get(),
                        self.plotframe,
                        0)

            ClicPosition(self.fig,
                        ("filter 2", filtre2),
                        self.time["start"].get(),
                        self.plotframe,
                        -80)

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

        axe = [int(self.time["start"].get()*1000),
               int(self.time["end"].get()*1000)]
        d_use = self.data[axe[0]:axe[1]]

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
                   numero,
                   filtre1.get_spike(d_use),
                   filtre2.get_spike(d_use),
                   filtre1.moving_average,
                   self.filter1["threshold"].get(),
                   self.filter2["threshold"].get(),
                   **self.options)

        self.spike_detected["filter1_nb"].set(filtre1.number_spikes)
        self.spike_detected["filter2_nb"].set(filtre2.number_spikes)
        
        if numero == 211:
            if self.filter1["method"].get() != "":
                plot_graphe(fig, axe,
                            "Filter 1",
                            filtre1.firing_rate(),
                            filtre1.time_period,
                            212,
                            "y")
            else:
                plot_graphe(fig,
                            axe,
                            "Filter 2",
                            filtre2.firing_rate(),
                            filtre2.time_period,
                            212,
                            "g")

        if numero == 311:
            plot_graphe(fig,
                        axe,
                        "Filter 1",
                        filtre1.firing_rate(),
                        filtre1.time_period,
                        312,
                        "y")
            plot_graphe(fig,
                        axe,
                        "Filter 2",
                        filtre2.firing_rate(),
                        filtre2.time_period,
                        313,
                        "g")

        return fig


if __name__ == "__main__":
    root = Tk()
    root.title("Spike Detection Graphical Interface")
    fenetre = Sdgi(root)
    root.mainloop()