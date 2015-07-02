#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" fenetre de configuration pour interface principale"""

from tkinter import *

class Configure(Frame):
	def __init__(self, window, wth, wtp, wbt, wet, **kwargs):
		Frame.__init__(self, window, **kwargs)
		self.pack(fill=BOTH)
		self.window = window
		self.rendu = ()


		Label(self, text="Threshold resolution:").grid(column=1, row=1, sticky=W)
		self.wth = Scale(self, from_=1, orient=HORIZONTAL, to=20,
						resolution=1, length=200)
		self.wth.grid(column=2, row=1, columnspan=2)
		self.wth.set(wth)


		Label(self, text="Time period resolution:").grid(column=1, row=2, sticky=W)
		self.wtp = Scale(self, from_=1, orient=HORIZONTAL, to=1000,
						resolution=5, length=200)
		self.wtp.grid(column=2, row=2, columnspan=2)
		self.wtp.set(wtp)


		Label(self, text="Default begin time:").grid(column=1, row=3, sticky=W)
		self.wbt = Scale(self, from_=0, orient=HORIZONTAL, to=500,
						resolution=5, length=200)
		self.wbt.grid(column=2, row=3, columnspan=2)
		self.wbt.set(wbt)


		Label(self, text="Default ending time:").grid(column=1, row=4, sticky=W)
		self.wet = Scale(self, from_=0, orient=HORIZONTAL, to=500,
						resolution=5, length=200)
		self.wet.grid(column=2, row=4, columnspan=2)
		self.wet.set(wet)

		Button(self, text="Apply", width=15, command=self.apply).grid(column=1, row=5)
		Button(self, text="Save config", width=15).grid(column=2, row=5)
		Button(self, text="Quit", width=15, command=self.window.destroy).grid(column=3, row=5)

		for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)

	def apply(self):
		""" envoie les données """
		self.rendu = (self.wth.get(), self.wtp.get(), self.wbt.get(), self.wet.get())
		self.quit()
		self.window.destroy()
		return

	def save(self):
		""""""
		pass


if __name__ == "__main__":
    root = Tk()
    root.title("Configure")
    fenetre = Configure(root, 40, 1000, 100, 150)
    root.mainloop()
