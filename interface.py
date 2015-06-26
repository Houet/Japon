#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from tkinter import *
import tkinter as tk
from spike import *
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


class Interface(Frame):
    """ Spike Detection Graphic Interface """
    def __init__(self, window, datafile, **kwargs):
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.datafile = datafile

        # création de la premiere frame (partie droite de l'interface)
        self.frame1 = Frame(self, padx=10, pady=10)
        self.frame1.pack(side=RIGHT, fill=Y)

        # création de la deuxième frame (partie gauche de l'interface)
        self.drawingframe = Frame(self, width=8*96, height=5*96)
        self.drawingframe.pack(side=LEFT, fill=Y)

        self.attente = Canvas(self.drawingframe, width=8*96, height=5*96)
        self.attente.create_text(4*96, 5*48, text="Data loading ... Please press 'Voir' button to see them")
        self.attente.pack(fill=BOTH)

        # sous frames contenues dans frame de droite 
        self.frame1_1 = Frame(self.frame1, bg="blue", width=50, height=50)
        self.frame1_1.pack(side=TOP)

        self.th = Scale(self.frame1_1, from_=80, to=20, resolution=10,
                tickinterval=10, showvalue=0, command=self.print_graph)
        self.th.grid(column=1, row=1, sticky=E)

        self.thresh = Label(self.frame1_1, text="Threshold")
        self.thresh.grid(column=2, row=1)

        self.timescale = Scale(self.frame1_1, from_=10000, to=1000,
              resolution=1000)
        self.timescale.grid(column=1, row=2, sticky=E)

        self.timelabel = Label(self.frame1_1, text="Time")
        self.timelabel.grid(column=2, row=2)

        self.frame1_2 = Frame(self.frame1, bg="green", width=50, height=50, padx=10, pady=10)
        self.frame1_2.pack(side=BOTTOM, anchor="se", fill=Y)

        self.voir = Button(self.frame1_2, text="Voir", command=self.print_graph)
        self.voir.pack(anchor="se", ipadx=10)
        self.quitter = Button(self.frame1_2, text="Quitter", command=self.quit).pack(anchor="se")

        for child in self.frame1_1.winfo_children(): child.grid_configure(padx=5, pady=5)
        for child in self.frame1_2.winfo_children(): child.pack_configure(padx=5, pady=5)


    def print_graph(self, *args):
        """
        print graph on the interface
        frame = were to print graph
        data = data to work width
        th = threshold for data analysis
        """
        for w in self.drawingframe.winfo_children():
            w.destroy()

        f = draw_curb(self.datafile, self.th.get())

        canvas = FigureCanvasTkAgg(f, master=self.drawingframe)
        canvas.show()
        canvas.get_tk_widget().pack(expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, self.drawingframe)
        toolbar.update()
        canvas._tkcanvas.pack(expand=1)
        return


root = Tk()
root.title("Spike Detection Graphic Interface")

fenetre = Interface(root, "data.txt")

# fin du getsionnaire graphique
root.mainloop()
