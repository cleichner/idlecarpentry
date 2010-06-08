try:
    from Tkinter import *
except ImportError:
    print>>sys.__stderr__, "** IDLE can't import Tkinter.  " \
                           "Your Python may not be configured for Tk. **"
import tkMessageBox
from PyShell import PyShellEditorWindow, PyShellFileList
from EditorWindow import fixwordbreaks

class PySplitShellEditorWindow(PyShellEditorWindow):
    "Split IDLE text edit window"
    pass 

class FileAnnotationList(PyShellFileList):
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
