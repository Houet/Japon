#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

""" SDGI programm, require spike.py and configure.py """

from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showwarning

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from webbrowser import open as wbopen
from spike import *
from configure import *


class Interface(Frame):
    """ Spike Detection Graphic Interface """
    def __init__(self, window, **kwargs):
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.window = window

        # variable
        self.datafile = ""
        self.data_extrated = (None, None)
        self.fig = None
        self.v = IntVar(self, 40)
        self.tp = IntVar(self, 1000)
        self.ax = DoubleVar(self, 100)
        self.aex = DoubleVar(self, 150)
        self.st = IntVar(self, 1)
        infotext = "None\n\nNone\n\nNone\n\nNone\n\nNone"
        self.information = StringVar(self, infotext)

        # menu bar creation
        self.menubar = Menu(self)

        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="File",
                               accelerator="Ctrl + O",
                               command=self.search_file)
        self.menu1.bind_all("<Control-o>", self.search_file)
        self.menu1.add_command(label="Stream",
                               accelerator="Ctrl + S",
                               command=self.search_stream)
        self.menu1.bind_all("<Control-s>", self.search_stream)
        self.menubar.add_cascade(label="Open", menu=self.menu1)

        self.menubar.add_command(label="Configure", command=self.settings)
        self.menubar.add_command(label="Help", command=self.url_open)
        window.config(menu=self.menubar)

        # right main frame (for settings)
        self.frame1 = Frame(self, padx=10, pady=10)
        self.frame1.pack(side=RIGHT, fill=Y)

        # Left main frame (for drawing)
        self.drawingframe = Frame(self, width=10*100+10, height=6*100)
        self.drawingframe.pack(side=LEFT)

        # Right frame children
        self.frame1_3 = LabelFrame(self.frame1, text="Infos", width=29)
        self.frame1_3.pack()

        self.frame1_1 = LabelFrame(self.frame1, text="Settings", width=29)
        self.frame1_1.pack(fill=X, pady=8)

        self.frame1_2 = Frame(self.frame1,
                              width=50,
                              height=50,
                              padx=10,
                              pady=10)
        self.frame1_2.pack(side=BOTTOM, fill=Y)

        # frame 1 settings part
        self.th = Scale(self.frame1_1,
                        orient=HORIZONTAL,
                        from_=20,
                        to=80,
                        resolution=10,
                        tickinterval=5,
                        variable=self.v,
                        label="Threshold:",
                        length=200)
        self.th.grid(column=1, columnspan=2, row=1, sticky=(N, S, E, W))

        self.timescale = Scale(self.frame1_1,
                               orient=HORIZONTAL,
                               from_=1000,
                               to=10000,
                               resolution=1000,
                               label="Time Period:",
                               length=200,
                               variable=self.tp)
        self.timescale.grid(column=1, columnspan=2, row=2, sticky=(N, S, E, W))

        Label(self.frame1_1,
              text="Begin time:").grid(column=1, row=3, sticky=W)
        self.axebegin = Spinbox(self.frame1_1,
                                from_=0,
                                to=500,
                                increment=10,
                                textvariable=self.ax,
                                width=6)
        self.axebegin.grid(column=2, row=3, sticky=E)

        Label(self.frame1_1, text="End time:").grid(column=1, row=4, sticky=W)
        self.axeend = Spinbox(self.frame1_1,
                              from_=0,
                              to=500,
                              increment=10,
                              textvariable=self.aex,
                              width=6)
        self.axeend.grid(column=2, row=4, sticky=E)

        # frame 2 button part
        Button(self.frame1_2,
               text="Refresh",
               command=self.print_graph,
               width=15).pack()
        Button(self.frame1_2,
               text="Save",
               command=self.save_fig,
               width=15).pack()
        Button(self.frame1_2,
               text="Quit",
               command=self.quit,
               width=15).pack()

        # frame 3 infos part
        Label(self.frame1_3,
              text="Current Threshold:\n\nCurrent Period time:\n\n\
Data name:\n\nData length:\n\nCurrent step:",
              justify="left",
              width=18).pack(side=LEFT)
        self.info = Label(self.frame1_3,
                          textvariable=self.information,
                          justify="right",
                          width=11)
        self.info.pack()

        # padding
        for child in self.frame1_1.winfo_children():
            child.grid_configure(padx=5, pady=5)
        for child in self.frame1_2.winfo_children():
            child.pack_configure(padx=5, pady=5)

    def print_graph(self):
        """
        print graph on the interface
        frame = were to print graph
        data = data to work width
        th = threshold for data analysis
        """

        for w in self.drawingframe.winfo_children():
            w.destroy()

        axe = (self.ax.get(), self.aex.get())
        if axe[0] != axe[1]:
            try:
                self.fig = draw_curb(self.data_extrated[1],
                                     self.v.get(),
                                     tp=self.tp.get(),
                                     axis=axe,
                                     st=self.st.get())

                canvas = FigureCanvasTkAgg(self.fig, master=self.drawingframe)
                canvas.show()
                canvas.get_tk_widget().pack()

                name_data = self.datafile.split("/")[-1]
                if len(name_data) >= 10:
                    name_data = "... {}".format(name_data[-8:])
                text = "{} mV\n\n{} \
ms\n\n{}\n\n{} s\n\n{} ms".format(self.th.get(),
                                  self.timescale.get(),
                                  name_data,
                                  self.axeend["to"],
                                  self.st.get())
                self.information.set(text)
            except ValueError:
                showwarning(title="Warning !",
                            message="Wrong file ...",
                            parent=self.window)
        else:
            showwarning(title="Warning !",
                        message="Begin time = End time",
                        parent=self.window)
        return

    def search_file(self, *args):
        """
        allow to find file in
        your PATH
        """
        self.datafile = askopenfilename(filetypes=[("text file", ".txt")],
                                        parent=self.window,
                                        title="Open a file")
        if self.datafile != "":
            try:
                self.data_extrated = import_data(self.datafile)
                self.axeend["to"] = len(self.data_extrated[1])/1000
                self.axebegin["to"] = len(self.data_extrated[1])/1000
                self.print_graph()
            except ValueError:
                showwarning(title="Warning !",
                            message="Wrong file ...",
                            parent=self.window)
        return

    def search_stream(self, *args):
        """ allow to find stream in your path """
        showinfo(title="Info",
                 message="Not available yet ...",
                 parent=self.window)
        return

    def save_fig(self):
        """ save the current plotting figure """
        try:
            self.fig.savefig("{}_th={}_tp={}.png"
                             .format(self.datafile.split(".")[0],
                                     self.th.get(),
                                     self.timescale.get()))
            showinfo(title="Info",
                     message="Plot save !",
                     parent=self.window)
        except AttributeError:
            showwarning(title="Error",
                        message="No plot to save...",
                        parent=self.window)
        return

    def settings(self):
        """ allow to change settings and to configure interface """
        wind = Toplevel(self.window)
        wind.geometry('+300+100')
        wind.title("Settings")
        wind.focus()
        conf = Configure(wind,
                         self.th["resolution"],
                         self.timescale["resolution"],
                         self.axebegin["increment"],
                         self.st.get())
        wind.mainloop()
        if conf.rendu != ():
            self.th["resolution"] = conf.rendu[0]
            self.timescale.configure(from_=conf.rendu[1],
                                     to=conf.rendu[1]*10,
                                     resolution=conf.rendu[1])
            self.axebegin["increment"] = conf.rendu[2]
            self.axeend["increment"] = conf.rendu[2]
            self.st.set(conf.rendu[3])
        return

    def url_open(self):
        """ open a url """
        return wbopen("https://github.com/Houet/Japon")


if __name__ == "__main__":
    root = Tk()
    root.title("Spike Detection Graphic Interface")
    fenetre = Interface(root)
    root.mainloop()
