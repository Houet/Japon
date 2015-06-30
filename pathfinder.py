#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
module qui permet de faire une fenetre de recherche de chemin
retourne un nom de fichier
"""

from tkinter import *
import os


class Fichier(Variable):
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
    def __str__(self):
        return self.current

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
    def __init__(self, window):
        """objet qui contiendra notre application"""
        Frame.__init__(self, window)
        self.pack(fill=BOTH)
        self.window = window
        self.current = StringVar(self, os.getcwd())
        self.local = Fichier(self.current.get())

        self.dossierparent = Label(self, text="dossiers parents:")
        self.dossierparent.grid(row=1, column=1)

        self.dossieractuel = Label(self, text="dossiers actuel:")
        self.dossieractuel.grid(row=1, column=2)

        self.dossierfils = Label(self, text="dossiers fils:")
        self.dossierfils.grid(row=1, column=3)

        self.path = Entry(self, textvariable=self.current, width=25)
        self.path.grid(row=2, column=2, padx=5)

        self.parent = Listbox(self)
        self.parent.grid(row=2, column=1, rowspan=2, padx=5, pady=5, sticky=E)

        for i in os.listdir(os.path.dirname(os.getcwd())):
            self.parent.insert(0, i)
        self.parent.insert(0, os.path.dirname(os.getcwd()))

        self.choix = Listbox(self)
        self.choix.grid(row=2, column=3, rowspan=2, padx=5, pady=5, sticky=E)

        for i in os.listdir():
            self.choix.insert(0, i)

        self.quit = Button(self, text="Quit", command=window.destroy)
        self.quit.grid(row=4, column=1)

        self.choose = Button(self, text="Choose", command=self.choose)
        self.choose.grid(row=4, column=2)

        self.open = Button(self, text="Open", command=self.list_dir)
        self.open.grid(row=4, column=3)


    def list_dir(self):
        """
        list dir in a given directory
        """
        index = self.parent.curselection()
        index2 = self.choix.curselection()

        if index != ():
            self.local.set(os.path.join(self.local.get_parent(), self.parent.get(index[0])))
        elif index2 != ():
            self.local.set(os.path.join(self.local.current, self.choix.get(index2[0])))

        self.choix.delete(0, "end")
        self.parent.delete(0, "end")

        self.current.set(self.local.current)

        for i in self.local.get_brother():
            self.parent.insert("end", i)
        self.parent.insert(0, self.local.get_parent())

        for i in self.local.get_children():
            self.choix.insert("end", i)

    def choose(self):
        """choose a file"""
        index = self.parent.curselection()
        index2 = self.choix.curselection()
        if index != ():
            self.local.set(os.path.join(self.local.get_parent(), self.parent.get(index[0])))
        elif index2 != ():
            self.local.set(os.path.join(self.local.current, self.choix.get(index2[0])))

        self.current.set(self.local.current)
        self.window.destroy()


if __name__ == "__main__":

    root =Tk()
    root.title("Pathfinder GUI")

    PathFinder(root).mainloop()