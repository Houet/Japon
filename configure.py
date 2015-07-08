#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" settings window for SDGI programm (cf interface.py) """

from tkinter import *


class Configure(Frame):
    def __init__(self, window, wth, wtp, wtr, wst, **kwargs):
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.window = window
        self.rendu = ()

        Label(self, text="Threshold resolution:").grid(column=1,
                                                       row=1,
                                                       sticky=W)
        self.wth = Scale(self, from_=1, orient=HORIZONTAL, to=20,
                         resolution=1, length=200)
        self.wth.grid(column=2, row=1, columnspan=2)
        self.wth.set(wth)

        Label(self, text="Time period resolution:").grid(column=1,
                                                         row=2,
                                                         sticky=W)
        self.wtp = Scale(self, from_=1, orient=HORIZONTAL, to=1000,
                         resolution=5, length=200)
        self.wtp.grid(column=2, row=2, columnspan=2)
        self.wtp.set(wtp)

        Label(self, text="Time resolution:").grid(column=1,
                                                  row=3,
                                                  sticky=W)
        self.wtr = Scale(self, from_=0.1, orient=HORIZONTAL, to=10,
                         resolution=0.1, length=200)
        self.wtr.grid(column=2, row=3, columnspan=2)
        self.wtr.set(wtr)

        Label(self, text="Step value:").grid(column=1,
                                             row=4,
                                             sticky=W)
        self.wst = Scale(self, from_=1, orient=HORIZONTAL, to=10,
                         resolution=1, length=200)
        self.wst.grid(column=2, row=4, columnspan=2)
        self.wst.set(wst)

        Button(self, text="Apply", width=15,
               command=self.apply).grid(column=1, row=5, sticky=W)
        Button(self, text="Quit", width=15,
               command=self.qu).grid(column=3, row=5, sticky=E)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def apply(self):
        """ button apply fonction """
        self.rendu = (self.wth.get(), self.wtp.get(),
                      self.wtr.get(), self.wst.get())
        self.quit()
        self.window.destroy()
        return

    def qu(self):
        """ exit window """
        self.quit()
        self.window.destroy()
        return


if __name__ == "__main__":
    root = Tk()
    root.title("Configure")
    fenetre = Configure(root, 40, 1000, 100, 150)
    root.mainloop()
