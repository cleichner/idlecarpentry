from Tkinter import *
import PyShell

class PySplitShellEditorWindow(PyShell.EditorWindow):
    "Split IDLE text edit window"


    

def main():
    global flist, root 

    root = Tk(className="Idle")

    fixwordbreaks(root)
    root.withdraw()
    flist = PyShellFileList(root)

    shell = flist.pyshell
    # handle remaining options:
    if debug:
        shell.open_debugger()
    if startup:
        filename = os.environ.get("IDLESTARTUP") or \
                   os.environ.get("PYTHONSTARTUP")
        if filename and os.path.isfile(filename):
            shell.interp.execfile(filename)
    if shell and cmd or script:
        shell.interp.runcommand("""if 1:
            import sys as _sys
            _sys.argv = %r
            del _sys
            \n""" % (sys.argv,))
        if cmd:
            shell.interp.execsource(cmd)
        elif script:
            shell.interp.prepend_syspath(script)
            shell.interp.execfile(script)

    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    sys.modules['PyShell'] = sys.modules['__main__']
    main()
