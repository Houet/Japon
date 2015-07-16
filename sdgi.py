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
                        "threshold": IntVar(self, 40),
                        "time_period": IntVar(self, 1000),
                        "method": StringVar(self, None),
                        "step": IntVar(self, None),
                        }

        self.thf1_var = IntVar(self, 40)
        self.tpf1_var = IntVar(self, 1000)
        self.method1_var = StringVar(self, "Slope")
        self.step1_var = IntVar(self, 1)
        self.thf2_var = IntVar(self, 40)
        self.tpf2_var = IntVar(self, 1000)
        self.method2_var = StringVar(self, None)
        self.step2_var = IntVar(self, None)

        self.spike_detected = {
                                "filter1_nb":IntVar(self, 0),
                                "fil1_tab": None,
                                "filter2_nb":IntVar(self, 0),
                                "fil2_tab": None,
                                }

        ####################            menu bar            ####################
        self.menubar = Menu(self)
        self.menubar.add_command(label="Open", command=self.open)
        self.menubar.add_command(label="Help", command=self.help)
        self.window.config(menu=self.menubar)

        ####################       frame for drawing        ####################
        self.plotframe = Frame(self, width=8*100+10, height=6*100)
        self.plotframe.grid(column=1, row=1, rowspan=4)

        ####################     frame for information      ####################
        self.infoframe = LabelFrame(self, text="Infos", width=30)
        self.infoframe.grid(column=2, row=1, padx=5, sticky=N)

        Label(self.infoframe, text="File name:").grid(column=1, row=1, sticky=W)
        Label(self.infoframe, text="File lenght:").grid(column=1, row=2, sticky=W)

        Label(self.infoframe, textvariable=self.fshortname).grid(column=2, row=1, sticky=E)
        Label(self.infoframe, textvariable=self.flenght).grid(column=2, row=2, sticky=E)

        self.filter_one = LabelFrame(self.infoframe, text="Filter 1", width=15)
        self.filter_one.grid(column=1, row=3, sticky=W)
        Label(self.filter_one, text="Method:").grid(column=1, row=1, sticky=W)
        Label(self.filter_one, textvariable=self.method1_var, width=5, anchor=E).grid(column=2, row=1, sticky=E)
        Label(self.filter_one, text="Threshold:").grid(column=1, row=2, sticky=W)
        Label(self.filter_one, textvariable=self.thf1_var).grid(column=2, row=2, sticky=E)
        Label(self.filter_one, text="Time period:").grid(column=1, row=3, sticky=W)
        Label(self.filter_one, textvariable=self.tpf1_var).grid(column=2, row=3, sticky=E)
        Label(self.filter_one, text="Step:").grid(column=1, row=4, sticky=W)
        Label(self.filter_one, textvariable=self.step1_var).grid(column=2, row=4, sticky=E)
        Label(self.filter_one, text="Spike(s) detected:").grid(column=1, row=5, sticky=W)
        Label(self.filter_one, textvariable=self.spike_detected["filter1_nb"]).grid(column=2, row=5, sticky=E)
        
        self.filter_two = LabelFrame(self.infoframe, text="Filter 2", width=15)
        self.filter_two.grid(column=2, row=3, sticky=E)
        Label(self.filter_two, text="Method:").grid(column=1, row=1, sticky=W)
        Label(self.filter_two, textvariable=self.method2_var, width=5, anchor=E).grid(column=2, row=1, sticky=E)
        Label(self.filter_two, text="Threshold:").grid(column=1, row=2, sticky=W)
        Label(self.filter_two, textvariable=self.thf2_var).grid(column=2, row=2, sticky=E)
        Label(self.filter_two, text="Time period:").grid(column=1, row=3, sticky=W)
        Label(self.filter_two, textvariable=self.tpf2_var).grid(column=2, row=3, sticky=E)
        Label(self.filter_two, text="Step:").grid(column=1, row=4, sticky=W)
        Label(self.filter_two, textvariable=self.step2_var).grid(column=2, row=4, sticky=E)
        Label(self.filter_two, text="Spike(s) detected:").grid(column=1, row=5, sticky=W)
        Label(self.filter_two, textvariable=self.spike_detected["filter2_nb"]).grid(column=2, row=5, sticky=E)

        for child in self.infoframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        ####################       frame for options        ####################
        self.optionframe = LabelFrame(self, text="Display Options", width=30)
        self.optionframe.grid(column=2, row=2, sticky=N, padx=5)

        Label(self.optionframe, text="Starting time:").grid(column=1, row=1, sticky=W)        
        self.start_time = Entry(self.optionframe,
                                textvariable=self.time["start"],
                                justify="right",
                                width=8)
        self.start_time.grid(column=2, row=1, sticky=E)

        Label(self.optionframe, text="Ending time:").grid(column=1, row=2, sticky=W)      
        self.end_time = Entry(self.optionframe,
                                textvariable=self.time["end"],
                                justify="right",
                                width=8)
        self.end_time.grid(column=2, row=2, sticky=E)

        self.filter1 = Checkbutton(self.optionframe,
                                   text="Filter 1",
                                   justify="left",
                                   var=self.options["f1"])
        self.filter1.grid(column=1, row=3, sticky=W)
        self.filter2 = Checkbutton(self.optionframe,
                                   text="Filter 2",
                                   var=self.options["f2"])
        self.filter2.grid(column=2, row=3, sticky=W)
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

        ####################       frame for filters        ####################
        self.filterframe = LabelFrame(self, text="Spikes Filters", width=30)
        self.filterframe.grid(column=2, row=3, sticky=N)

        self.setf1 = LabelFrame(self.filterframe, text="Filter 1", width=15)
        self.setf1.pack(side=LEFT)
        Label(self.setf1, text="Threshold:").grid(column=1, row=1, sticky=W)
        self.thf1 = Entry(self.setf1,
                          textvariable=self.thf1_var,
                          width=5,
                          justify="right")
        self.thf1.grid(column=2, row=1)

        Label(self.setf1, text="Time Period:").grid(column=1, row=2, sticky=W)
        self.tpf1 = Entry(self.setf1,
                          textvariable=self.tpf1_var,
                          width=5,
                          justify="right")
        self.tpf1.grid(column=2, row=2)

        Label(self.setf1, text="Method:").grid(column=1, row=3, sticky=W)
        self.method1 = Menubutton(self.setf1,
                                  textvariable=self.method1_var,
                                  width=6, relief=RAISED)
        self.method1.menu = Menu(self.method1, tearoff=0)
        self.method1["menu"] = self.method1.menu
        self.method1.menu.add_radiobutton(label=None, variable=self.method1_var, command=self.add_step)
        self.method1.menu.add_radiobutton(label="Slope", variable=self.method1_var, command=self.add_step)
        self.method1.menu.add_radiobutton(label="Upper", variable=self.method1_var, command=self.add_step)
        self.method1.menu.add_radiobutton(label="Lower", variable=self.method1_var, command=self.add_step)
        self.method1.menu.add_radiobutton(label="Both", variable=self.method1_var, command=self.add_step)
        self.method1.grid(column=2, row=3, padx=5, pady=5)

        Label(self.setf1, text="Step:").grid(column=1, row=4, sticky=W)
        self.stf1 = Entry(self.setf1,
                          textvariable=self.step1_var,
                          width=5,
                          justify="right")
        self.stf1.grid(column=2, row=4)

        self.setf2 = LabelFrame(self.filterframe, text="Filter 2", width=15)
        self.setf2.pack(side=LEFT)
        Label(self.setf2, text="Threshold:").grid(column=1, row=1, sticky=W)
        self.thf2 = Entry(self.setf2,
                          textvariable=self.thf2_var,
                          width=5,
                          justify="right")
        self.thf2.grid(column=2, row=1)

        Label(self.setf2, text="Time Period:").grid(column=1, row=2, sticky=W)
        self.tpf2 = Entry(self.setf2,
                          textvariable=self.tpf2_var,
                          width=5,
                          justify="right")
        self.tpf2.grid(column=2, row=2)

        Label(self.setf2, text="Method:").grid(column=1, row=3, sticky=W)
        self.method2 = Menubutton(self.setf2, textvariable=self.method2_var, width=6, relief=RAISED)
        self.method2.menu = Menu(self.method2, tearoff=0)
        self.method2["menu"] = self.method2.menu
        self.method2.menu.add_radiobutton(label=None, variable=self.method2_var, command=self.add_step)
        self.method2.menu.add_radiobutton(label="Slope", variable=self.method2_var, command=self.add_step)
        self.method2.menu.add_radiobutton(label="Upper", variable=self.method2_var, command=self.add_step)
        self.method2.menu.add_radiobutton(label="Lower", variable=self.method2_var, command=self.add_step)
        self.method2.menu.add_radiobutton(label="Both", variable=self.method2_var, command=self.add_step)
        self.method2.grid(column=2, row=3, padx=5, pady=5)

        Label(self.setf2, text="Step:").grid(column=1, row=4, sticky=W)
        self.stf2 = Entry(self.setf2,
                          textvariable=self.step2_var,
                          width=5,
                          justify="right",
                          state="disabled")
        self.stf2.grid(column=2, row=4)

        for child in self.filterframe.winfo_children():
            child.pack_configure(padx=5, pady=5)
        for child in self.setf1.winfo_children():
            child.grid_configure(padx=5)
        for child in self.setf2.winfo_children():
            child.grid_configure(padx=5)

        ####################       frame for button         ####################
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

    ######################        menu method         ##########################

    def open(self):
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
            self.time["end"].set(self.flenght.get())
            self.refresh()
        return

    def help(self):
        """ return https://github.com/Houet/Japon """
        return wbopen("https://github.com/Houet/Japon")
    
    ######################       button method        ##########################

    def refresh(self):
        """ """
        for w in self.plotframe.winfo_children():
            w.destroy()
        try:
            self.fig = self.plot()
        except AttributeError:
            showwarning(title="Error",
                        message="No data to plot...",
                        parent=self.window)
        except ValueError:
            showwarning(title="Error",
                        message="Issue with filter...",
                        parent=self.window)
        else:
            canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)
            canvas.show()
            canvas.get_tk_widget().pack()
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

    ######################        other method         #########################

    def add_step(self):
        """ change the apparence of step entry widget """
        if self.method1_var.get() == "Slope":
            self.step1_var.set(1)
            self.stf1["state"] = "normal"
        else:
            self.step1_var.set(None)
            self.stf1["state"] = "disabled"

        if self.method2_var.get() == "Slope":
            self.step2_var.set(1)
            self.stf2["state"] = "normal"
        else:
            self.step2_var.set(None)
            self.stf2["state"] = "disabled"

    def filter_method(self):
        """ return method to use to apply filter """
        axe = [int(self.time["start"].get()*1000), int(self.time["end"].get()*1000)]
        d_use = self.data[axe[0]:axe[1]]

        th1 = self.thf1_var.get()

        if self.method1_var.get() == "Slope":
            self.spike_detected["fil1_tab"] = filtre(spike_detection(d_use, th1, step=self.step1_var.get()))
        elif self.method1_var.get() == "Upper":
            self.spike_detected["fil1_tab"] = filtre(get_upper(d_use, mm(d_use, th1)[1]))
        elif self.method1_var.get() == "Lower":
            self.spike_detected["fil1_tab"] = filtre(get_lower(d_use, mm(d_use, th1)[2]))
        elif self.method1_var.get() == "Both":
            self.spike_detected["fil1_tab"] = filtre(get_double_ekips(d_use, mm(d_use, th1)))
        else:
            self.spike_detected["fil1_tab"] = []  

        th2 = self.thf2_var.get()

        if self.method2_var.get() == "Slope":
            self.spike_detected["fil2_tab"] = filtre(spike_detection(d_use, th2, step=self.step2_var.get()))
        elif self.method2_var.get() == "Upper":
            self.spike_detected["fil2_tab"] = filtre(get_upper(d_use, mm(d_use, th2)[1]))
        elif self.method2_var.get() == "Lower":
            self.spike_detected["fil2_tab"] = filtre(get_lower(d_use, mm(d_use, th2)[2]))
        elif self.method2_var.get() == "Both":
            self.spike_detected["fil2_tab"] = filtre(get_double_ekips(d_use, mm(d_use, th2)))
        else:
            self.spike_detected["fil2_tab"] = []

        self.spike_detected["filter1_nb"].set(self.spike_detected["fil1_tab"].count(1))
        self.spike_detected["filter2_nb"].set(self.spike_detected["fil2_tab"].count(1))   

        return

    def plot(self):
        """ plot the figure """

        axe = [int(self.time["start"].get()*1000), int(self.time["end"].get()*1000)]
        d_use = self.data[axe[0]:axe[1]]

        self.filter_method()

        numero = 111
        if self.firing_rate.get():
            numero = 311
            if self.method2_var.get() == "":
                if self.method1_var.get() != None:
                    numero = 211
            elif self.method1_var.get() == "":
                if self.method2_var.get() != None:
                    numero = 211

        fig = plot(self.data,
                   axe,
                   numero,
                   self.spike_detected["fil1_tab"],
                   self.spike_detected["fil2_tab"],
                   self.thf1_var.get(),
                   self.thf2_var.get(),
                   **self.options)

        if numero == 211:
            if self.method1_var.get() != "":
                if len(self.spike_detected["fil1_tab"]) != 0:
                    plot_graphe(fig, axe, "Filter 1", self.spike_detected["fil1_tab"], self.tpf1_var.get(), 212, "y")
            else:
                if len(self.spike_detected["fil2_tab"]) != 0:
                    plot_graphe(fig, axe, "Filter 2", self.spike_detected["fil2_tab"], self.tpf2_var.get(), 212, "g")

        if numero == 311:
            if len(self.spike_detected["fil1_tab"]) != 0:
                plot_graphe(fig, axe, "Filter 1", self.spike_detected["fil1_tab"], self.tpf1_var.get(), 312,"y")
            if len(self.spike_detected["fil2_tab"]) != 0:
                plot_graphe(fig, axe, "Filter 2", self.spike_detected["fil2_tab"], self.tpf2_var.get(), 313, "g")
        return fig


if __name__ == "__main__":
    root = Tk()
    root.title("Spike Detection Graphical Interface")
    fenetre = Sdgi(root)
    root.mainloop()