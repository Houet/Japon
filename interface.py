#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from webbrowser import open as wbopen
from spike import *


class Interface(Frame):
    """ Spike Detection Graphic Interface """
    def __init__(self, window, **kwargs):
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.window = window
        self.datafile = ""
        self.v = IntVar(self, 40)
        self.tp = IntVar(self, 1000)
        self.ax = IntVar(self, 100)

        #creation de la barre de menu
        self.menubar = Menu(self)

        self.menu1 = Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="File", accelerator="Ctrl + O", command=self.search_file)
        self.menu1.bind("<Return>", self.search_file)
        self.menu1.add_command(label="Stream", accelerator="Ctrl + S")
        self.menubar.add_cascade(label="Open", menu=self.menu1)

        self.menu2 = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Parameters", menu=self.menu2)

        self.menubar.add_command(label="Help", command=self.url_open)

        window.config(menu=self.menubar)

        # création de la premiere frame (partie droite de l'interface)
        self.frame1 = Frame(self, padx=10, pady=10)
        self.frame1.pack(side=RIGHT, fill=Y)

        # création de la deuxième frame (partie gauche de l'interface)
        self.drawingframe = Frame(self, width=10*100, height=6*100)
        self.drawingframe.pack(side=LEFT)

        # sous frames contenues dans frame de droite 
        self.frame1_1 = LabelFrame(self.frame1, text="Options", width=50, height=50)
        self.frame1_1.pack(side=TOP)

        self.th = Scale(self.frame1_1, orient=HORIZONTAL, from_=20, to=80,
                        resolution=10, tickinterval=10, variable=self.v,
                        label="Threshold:", length=200)
        self.th.grid(column=1, columnspan=2, row=1, sticky=(N, S, E, W))

        self.timescale = Scale(self.frame1_1, orient=HORIZONTAL, from_=1000, to=10000,
                               resolution=1000, label="Time Period:",
                               length=200, variable=self.tp)
        self.timescale.grid(column=1, columnspan=2, row=2, sticky=(N, S, E, W))

        self.begin = Label(self.frame1_1, text="Begin time:")
        self.begin.grid(column=1, row=3, sticky=W)
        self.axebegin = Spinbox(self.frame1_1, from_=0, to=460, textvariable=self.ax, width=6)
        self.axebegin.grid(column=2, row=3, sticky=E)

        self.end = Label(self.frame1_1, text="End time:")
        self.end.grid(column=1, row=4, sticky=W)
        self.axeend = Spinbox(self.frame1_1, from_=(int(self.ax.get()) + 50),
                              to=500, width=6)
        self.axeend.grid(column=2, row=4, sticky=E)

        self.frame1_2 = Frame(self.frame1, width=50, height=50, padx=10, pady=10)
        self.frame1_2.pack(side=BOTTOM, anchor="se", fill=Y)

        self.refresh = Button(self.frame1_2, text="Refresh", command=self.print_graph)
        self.refresh.pack(anchor="se")
        self.quitter = Button(self.frame1_2, text="Quit", command=self.quit).pack(anchor="se")

        self.frame1_3 = LabelFrame(self.frame1, text="Infos", width=50, height=50)
        self.frame1_3.pack()

        self.info = Label(self.frame1_3, text="Current Threshold: {} mV\n\nCurrent Time Period: {} ms\n\n\
            Data Name: {}\n\nData Lenght: {}".format(self.th.get(), self.timescale.get(),
                                                    self.datafile, self.axeend["to"]),
            justify="left", width=26)
        self.info.pack(pady=5)


        for child in self.frame1_1.winfo_children(): child.grid_configure(padx=5, pady=5)
        for child in self.frame1_2.winfo_children(): child.pack_configure(padx=5, pady=5)


    def print_graph(self):
        """
        print graph on the interface
        frame = were to print graph
        data = data to work width
        th = threshold for data analysis
        """

        for w in self.drawingframe.winfo_children():
            w.destroy()

        axe = (self.ax.get(), int(self.axeend.get()))
        f = draw_curb(self.datafile, self.v.get(), tp=self.tp.get(), axis=axe)

        canvas = FigureCanvasTkAgg(f, master=self.drawingframe)
        canvas.show()
        canvas.get_tk_widget().pack(expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, self.drawingframe)
        toolbar.update()
        canvas._tkcanvas.pack(expand=1)

        self.info = Label(self.frame1_3, text="Current Threshold: {} mV\n\nCurrent Time Period: {} ms\n\n\
            Data Name: {}\n\nData Lenght: {}".format(self.th.get(), self.timescale.get(),
                                                    self.datafile, self.axeend["to"]),
            justify="left", width=26)
        return

    def search_file(self):
        """
        allow to find file in
        your PATH
        """
        self.datafile = askopenfilename(filetypes=[("text file", ".txt")], parent=self.window, title="Open a file")
        self.axeend["to"] = len(import_data(self.datafile)[1])/1000
        self.print_graph()
        return

    def url_open(self):
        """ open a url """
        return wbopen("https://www.google.co.jp/")


if __name__ == "__main__":
    root = Tk()
    root.title("Spike Detection Graphic Interface")
    fenetre = Interface(root)
    root.mainloop()
