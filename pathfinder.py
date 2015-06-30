#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
module qui permet de faire une fenetre de recherche de chemin
retourne un nom de fichier
"""

from tkinter import *
import os


class Fichier():
    def __init__(self, pathname):
        """
        classe qui prends un fichier (dir ou file)
        et qui donne son dossier parent et ses fils
        ainsi que ces freres = les dossier qui descende
        de son dossier parent
        """
        if os.path.exists(pathname):
            self.current = pathname
        else:
            raise OSError

    def set(self, newpathname):
        """ allow to change self.current """
        self.current = newpathname
        return self.current

    def get_parent(self):
        """get the directory parent"""
        return os.path.dirname(self.current)

    def get_children(self):
        """get the child directories """
        return os.listdir(self.current)  

    def get_brother(self):
        """get the brother directories"""
        return os.listdir(self.get_parent())


class PathFinder(Frame):
    def __init__(self):
        """objet qui contiendra notre application"""
        Frame.__init__(self)
        self.pack(fill=BOTH)
        self.current = StringVar(self, os.getcwd())

        self.dossier = Label(self, text="dossier actuel:")
        self.dossier.grid(row=1, column=1)

        self.path = Entry(self, textvariable=self.current, width=len(self.current.get()))
        self.path.grid(row=1, column=2, padx=5)

        self.parent = Listbox(self)
        self.parent.grid(row=2, column=1, rowspan=2, padx=5, pady=5, sticky=E)

        for i in os.listdir(os.path.dirname(os.getcwd())):
            self.parent.insert(0, i)
        self.parent.insert(0, os.path.split(self.current.get())[0])

        self.choix = Listbox(self)
        self.choix.grid(row=2, column=2, rowspan=2, padx=5, pady=5, sticky=E)

        for i in os.listdir():
            self.choix.insert(0, i)

        self.quit = Button(self, text="Quit", command=self.quit)
        self.quit.grid(row=2, column=3)

        self.open = Button(self, text="Open", command=self.list_dir)
        self.open.grid(row=3, column=3)


    def list_dir(self):
        """
        list dir in a given directory
        """
        ancetre = os.path.dirname(self.current.get())
        index = self.parent.curselection()[0]

        if index != 0:
            res = os.path.join(ancetre, self.parent.get(index))
        else:
            res = ancetre

        self.current.set(res)

        self.choix.delete(0, "end")
        self.parent.delete(0, "end")

        self.parent.insert("end", os.path.dirname(self.current.get()))
        self.parent.insert("end", "")
        
        for i in os.listdir(self.current.get()):
            self.parent.insert("end", i)

        for i in os.listdir(self.current.get()):
            self.choix.insert("end", i)


if __name__ == "__main__":

    PathFinder().mainloop()