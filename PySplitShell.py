from Tkinter import *
import tkMessageBox
from PyShell import PyShellEditorWindow, PyShellFileList
from EditorWindow import fixwordbreaks
from MultiCall import MultiCallCreator

class SplitTextFrame(Frame):
    '''This contains two Text widgets, split by an identifier tag. It mimicks
    the methods of the Text widget which EditorWindow and its subclasses use in
    for self.text ''' 
    pass

class PySplitShellEditorWindow(PyShellEditorWindow):
    "Split IDLE text edit window"
    pass 

class PySplitShellFileList(PyShellFileList):
    "Opens files and deals with partitioning the annotations and the source" 
    EditorWindow = PySplitShellEditorWindow
    pass

def test():
    root = Tk(className="Idle")

    fixwordbreaks(root)
    root.withdraw()

    flist = PySplitShellFileList(root)

    flist.open('test')

    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    test()
