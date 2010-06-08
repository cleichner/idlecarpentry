try:
    from Tkinter import *
except ImportError:
    print>>sys.__stderr__, "** IDLE can't import Tkinter.  " \
                           "Your Python may not be configured for Tk. **"
import tkMessageBox

from EditorWindow import EditorWindow, fixwordbreaks
from FileList import FileList

import PyShell

class PySplitShellEditorWindow(PyShell.EditorWindow):
    "Split IDLE text edit window"
    pass 

class FileAnnotationList(PyShell.PyShellFileList):
    "Opens files and deals with partitioning the annotations and the source" 
    pass

def test():
    global flist, root, use_subprocess

    use_subprocess = True
    enable_shell = False
    enable_edit = False

    root = Tk(className="Idle")

    fixwordbreaks(root)
    root.withdraw()
    flist = FileAnnotationList(root)
    flist.open_shell()

    shell = flist.pyshell

    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    test()
