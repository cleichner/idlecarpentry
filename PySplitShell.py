from Tkinter import *
import tkMessageBox
from PyShell import PyShellEditorWindow, PyShellFileList
from EditorWindow import fixwordbreaks

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
    flist2 = PySplitShellFileList(root)

    flist.open('IOBinding.py')
    flist2.open('MultiCall.py')

    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    test()
