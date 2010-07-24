import sys
import os
import re
import json
import tkMessageBox
import webbrowser
import idlever
import WindowList
import GrepDialog
import aboutDialog
import textView
import configDialog
import macosxSupport
from Tkinter import *
from configHandler import idleConf
from itertools import count
from MultiCall import MultiCallCreator


class TraceDisplayWindow(object):
    from Percolator import Percolator
    from ColorDelegator import ColorDelegator
    from IOBinding import IOBinding, filesystemencoding, encoding
    import Bindings
    from Tkinter import Toplevel

    help_url = None

    def __init__(self, flist=None, filename=None, key=None, root=None):
        if TraceDisplayWindow.help_url is None:
            dochome =  os.path.join(sys.prefix, 'Doc', 'index.html')
            if sys.platform.count('linux'):
                # look for html docs in a couple of standard places
                pyver = 'python-docs-' + '%s.%s.%s' % sys.version_info[:3]
                if os.path.isdir('/var/www/html/python/'):  # "python2" rpm
                    dochome = '/var/www/html/python/index.html'
                else:
                    basepath = '/usr/share/doc/'  # standard location
                    dochome = os.path.join(basepath, pyver,
                                           'Doc', 'index.html')
            elif sys.platform[:3] == 'win':
                chmfile = os.path.join(sys.prefix, 'Doc',
                                       'Python%s.chm' % _sphinx_version())
                if os.path.isfile(chmfile):
                    dochome = chmfile
            elif macosxSupport.runningAsOSXApp():
                # documentation is stored inside the python framework
                dochome = os.path.join(sys.prefix,
                        'Resources/English.lproj/Documentation/index.html')
            dochome = os.path.normpath(dochome)
            if os.path.isfile(dochome):
                TraceDisplayWindow.help_url = dochome
                if sys.platform == 'darwin':
                    # Safari requires real file:-URLs
                    TraceDisplayWindow.help_url = 'file://' + EditorWindow.help_url
            else:
                TraceDisplayWindow.help_url = "http://docs.python.org/%d.%d" % sys.version_info[:2]
        currentTheme=idleConf.CurrentTheme()
        self.flist = flist
        root = root or flist.root
        self.root = root
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '
        self.menubar = Menu(root)
        self.top = top = WindowList.ListedToplevel(root, menu=self.menubar)
        top.title("Trace Reader")

        if flist:
            self.tkinter_vars = flist.vars
            #self.top.instance_dict makes flist.inversedict avalable to
            #configDialog.py so it can access all EditorWindow instaces
            self.top.instance_dict = flist.inversedict
        else:
            self.tkinter_vars = {}  # keys: Tkinter event names
                                    # values: Tkinter variable instances
            self.top.instance_dict = {}
        self.recent_files_path = os.path.join(idleConf.GetUserCfgDir(),
                'recent-files.lst')
        button_frame = Frame(top) 
        center_frame = Frame(top) 
        anno_frame = Frame(center_frame) 
        self.text_frame = text_frame = Frame(center_frame) 

        play_button = Button( button_frame, text='Play', command=self.play)
        pause_button = Button( button_frame, text='Pause', command=self.pause)
        rewind_button = Button( button_frame, text='Rewind', command=self.rewind)
        forward_button = Button( button_frame, text='Step Forward', command=self.step_forward)
        back_button = Button( button_frame, text='Step Back', command=self.step_back)
        fast_button = Button( button_frame, text='Fast', command=self.fast)

        out_label = Label(top, text='stdout:', font=('sans', 12))
        globals_label = Label(anno_frame, text='globals:', font=('sans', 10))
        locals_label = Label(anno_frame, text='locals:', font=('sans', 10))
        anno_label = Label(anno_frame, text='explanation:', font=('sans', 10))
        source_label = Label(text_frame, text='source:', font=('sans', 10))

        #self.width = idleConf.GetOption('main','EditorWindow','width')
        text_options = {
#                'name': 'text',
                'padx': 5,
                'wrap': 'none',
        #        'width': self.width,
        #        'height': idleConf.GetOption('main', 'EditorWindow', 'height')
        }
        if TkVersion >= 8.5:
            # Starting with tk 8.5 we have to set the new tabstyle option
            # to 'wordprocessor' to achieve the same display of tabs as in
            # older tk versions.
            text_options['tabstyle'] = 'wordprocessor'

        self.text = text = Text(text_frame, wrap=WORD, borderwidth=3)
        self.stdout = Text(top, height=7)
        self.annotation = Text(anno_frame, height=7, wrap=WORD, borderwidth=3)
        self.globals = Text(anno_frame, height=7, wrap=WORD, borderwidth=3)
        self.locals = Text(anno_frame, height=7, wrap=WORD, borderwidth=3)
        self.top.focused_widget = self.text

        self.createmenubar()
        self.apply_bindings()

        self.top.protocol("WM_DELETE_WINDOW", self.close)
        self.top.bind("<<close-window>>", self.close_event)
        if macosxSupport.runningAsOSXApp():
            # Command-W on editorwindows doesn't work without this.
            text.bind('<<close-window>>', self.close_event)
        text.bind("<<help>>", self.help_dialog)
        text.bind("<<python-docs>>", self.python_docs)
        text.bind("<<about-idle>>", self.about_dialog)
        text.bind("<<open-config-dialog>>", self.config_dialog)
        text.bind("<<do-nothing>>", lambda event: "break")

        if flist:
            flist.inversedict[self] = key
            if key:
                flist.dict[key] = self
            text.bind("<<open-new-window>>", self.new_callback)
            text.bind("<<close-all-windows>>", self.flist.close_all_callback)

        fontWeight = 'normal'
        if idleConf.GetOption('main', 'EditorWindow', 'font-bold', type='bool'):
            fontWeight='bold'
        text.config(font=(idleConf.GetOption('main', 'EditorWindow', 'font'),
                          idleConf.GetOption('main', 'EditorWindow', 'font-size'),
                          fontWeight))

        button_frame.pack(side=TOP, fill=BOTH)
        center_frame.pack(side=TOP, expand=1, fill=BOTH)
        out_label.pack(side=TOP, fill=BOTH)
        self.stdout.pack(side=TOP, expand=1, fill=BOTH)

        text_frame.pack(side=LEFT, expand=1, fill=BOTH)
        source_label.pack(side=TOP, fill=BOTH)
        anno_frame.pack(side=LEFT, expand=1, fill=BOTH)

        anno_label.pack(side=TOP, fill=BOTH)
        self.annotation.pack(side=TOP, expand=1, fill=BOTH)
        locals_label.pack(side=TOP, fill=BOTH)
        self.locals.pack(side=TOP, expand=1, fill=BOTH)
        globals_label.pack(side=TOP, fill=BOTH)
        self.globals.pack(side=TOP, expand=1, fill=BOTH)

        for button in (play_button, pause_button, rewind_button, forward_button, back_button):#, fast_button):
            button.pack(side=LEFT)

        text.pack(side=TOP, fill=BOTH, expand=1)
        text.focus_set()


        self.text.config(state=DISABLED)
        self.stdout.config(state=DISABLED)
        self.annotation.config(state=DISABLED)
        self.globals.config(state=DISABLED)
        self.locals.config(state=DISABLED)

        self.trace=None
        self.current_line=0
        self.paused=False
        self.finished=False

        #in seconds
        self.step_rate=1.5
        
        # If context_use_ps1 is true, parsing searches back for a ps1 line;
        # else searches for a popular (if, def, ...) Python stmt.
        self.context_use_ps1 = False

        # When searching backwards for a reliable place to begin parsing,
        # first start num_context_lines[0] lines back, then
        # num_context_lines[1] lines back if that didn't work, and so on.
        # The last value should be huge (larger than the # of lines in a
        # conceivable file).
        # Making the initial values larger slows things down more often.
        self.num_context_lines = 50, 500, 5000000

        self.per = per = self.Percolator(text)

        # IOBinding implements file I/O and printing functionality
        self.io = io = self.IOBinding(self)
        io.set_filename_change_hook(self.filename_change_hook)

        # Create the recent files submenu
        self.recent_files_menu = Menu(self.menubar)
        self.menudict['file'].insert_cascade(3, label='Recent Files',
                                             underline=0,
                                             menu=self.recent_files_menu)
      #  self.update_recent_files_list()

        self.color = None # initialized below in self.ResetColorizer

        if filename:
            if os.path.exists(filename) and not os.path.isdir(filename):
                io.loadfile(filename)
            else:
                io.set_filename(filename)

        self.ResetColorizer()

        menu = self.menudict.get('windows')
        if menu:
            end = menu.index("end")
            if end is None:
                end = -1
            if end >= 0:
                menu.add_separator()
                end = end + 1
            self.wmenu_end = end
            WindowList.register_callback(self.postwindowsmenu)

        self.ResetColorizer()

    def set_saved(self, flag):
        pass

    def fast(self):
        self.step_rate=.3

    def insert(self, target, text):
        getattr(self, target).config(state=NORMAL)
        getattr(self, target).insert(END, text)
        if target not in ('globals', 'locals'):
            getattr(self, target).see(END)
        getattr(self, target).config(state=DISABLED)

    def clear(self, target):
        getattr(self, target).config(state=NORMAL)
        getattr(self, target).delete('1.0', 'end')
        getattr(self, target).config(state=DISABLED)

    def clear_all(self):
        for target in ('text', 'stdout', 'annotation', 'globals', 'locals'):
            self.clear(target)

    def highlight_line(self, target, lineno):
        getattr(self, target).config(state=NORMAL)
        self.clear_highlighting(target)
        getattr(self, target).tag_add('highlight', '%s.0' % lineno, '%s.end' % lineno)
        getattr(self, target).tag_configure('highlight', background='yellow')
        getattr(self, target).see('highlight.first')
        getattr(self, target).config(state=DISABLED)

    def clear_highlighting(self, target):
        getattr(self, target).config(state=NORMAL)
        getattr(self, target).tag_remove('highlight', '1.0', 'end')
        getattr(self, target).config(state=DISABLED)

    def clear_all_highlighting(self):
        for target in ('text', 'stdout', 'annotation', 'globals', 'locals'):
            self.clear_highlighting(target)

    def play(self):
        if not self.paused and not self.finished:
            self.step_forward()
            self.text.after(int(self.step_rate * 1000), self.play)

    def pause(self):
        self.paused=not self.paused 
        if not self.paused:
            self.play()

    def step_forward(self):
        '''Moves to the next trace dictionary and inserts the data it contains,
        advancing the highlighting as appropriate.'''

        if not self.finished:
            step = self.trace[self.current_line]
            self.highlight_line('text', step['line']+1)

            if 'stdout' in step:
                self.insert('stdout', step['stdout'])
            if 'stderr' in step:
                self.insert('stdout', step['stderr'])

            self.clear('annotation')
            if 'annotation' in step:
                self.insert('annotation', step['annotation'])

            if 'globals' in step:
                self.clear('globals')
                glbs=step['globals'] 
                for entry in glbs:
                    self.insert('globals', "%s = %s\n" % (str(entry), str(glbs[entry])))

            if 'locals' in step:
                self.clear('locals')
                lcls=step['locals'] 
                for entry in lcls:
                    self.insert('locals', "%s = %s\n" % (str(entry), str(lcls[entry])))

            self.current_line+=1

        if self.current_line == len(self.trace):
            self.clear_all_highlighting()
            self.finished=True

    def step_back(self):
        if self.current_line <= 0:
            self.rewind()

        else:
            try:
                step = self.trace[self.current_line]
            except IndexError:
                step = self.trace[len(self.trace)-1]
                
            prev_step = self.trace[self.current_line-1]

            #remove the last thing printed to stdout
            if 'stdout' in step:
                self.stdout.config(state=NORMAL)
                self.stdout.delete('1.0', 'end+1c')
                for previous in range(self.current_line):
                    prev_step=self.trace[previous]
                    if 'stdout' in prev_step:
                        self.stdout.insert('insert', prev_step['stdout'])
                    if 'stderr' in prev_step:
                        self.stdout.insert('insert', prev_step['stderr'])
                self.stdout.config(state=DISABLED)

            if 'stderr' in step:
                self.stdout.config(state=NORMAL)
                self.stdout.delete('1.0', 'end+1c')
                for previous in range(self.current_line):
                    prev_step=self.trace[previous]
                    if 'stdout' in prev_step:
                        self.stdout.insert('insert', prev_step['stdout'])
                    if 'stderr' in prev_step:
                        self.stdout.insert('insert', prev_step['stderr'])
                self.stdout.config(state=DISABLED)

            self.clear('annotation')
            self.clear('globals')
            self.clear('locals')

            if 'annotation' in prev_step:
                self.insert('annotation', prev_step['annotation'])
            if 'globals' in prev_step:
                glbs=prev_step['globals'] 
                for entry in glbs:
                    self.insert('globals', "%s = %s\n" % (str(entry), str(glbs[entry])))
            if 'locals' in prev_step:
                self.clear('locals')
                lcls=prev_step['locals'] 
                for entry in lcls:
                    self.insert('locals', "%s = %s\n" % (str(entry), str(lcls[entry])))
            if self.finished:
                self.finished = False
                
            self.current_line -= 1
            step = self.trace[self.current_line]
            self.highlight_line('text', step['line']+1)

    def rewind(self):
        '''Sets all parameters back to their original states (including
        unpausing)'''

        self.clear_all_highlighting()

        for output in ('stdout', 'annotation', 'globals', 'locals'):
            self.clear(output)

        self.current_line=0
        self.finished=False
        self.paused=False
        self.text.see('1.0')

    def _filename_to_unicode(self, filename):
        """convert filename to unicode in order to display it in Tk"""
        if isinstance(filename, unicode) or not filename:
            return filename
        else:
            try:
                return filename.decode(self.filesystemencoding)
            except UnicodeDecodeError:
                # XXX
                try:
                    return filename.decode(self.encoding)
                except UnicodeDecodeError:
                    # byte-to-byte conversion
                    return filename.decode('iso8859-1')

    def new_callback(self, event):
        dirname, basename = self.io.defaultfilename()
        self.flist.new(dirname)
        return "break"

    def home_callback(self, event):
        if (event.state & 12) != 0 and event.keysym == "Home":
            # state&1==shift, state&4==control, state&8==alt
            return # <Modifier-Home>; fall back to class binding

        if self.text.index("iomark") and \
           self.text.compare("iomark", "<=", "insert lineend") and \
           self.text.compare("insert linestart", "<=", "iomark"):
            insertpt = int(self.text.index("iomark").split(".")[1])
        else:
            line = self.text.get("insert linestart", "insert lineend")
            for insertpt in xrange(len(line)):
                if line[insertpt] not in (' ','\t'):
                    break
            else:
                insertpt=len(line)

        lineat = int(self.text.index("insert").split('.')[1])

        if insertpt == lineat:
            insertpt = 0

        dest = "insert linestart+"+str(insertpt)+"c"

        if (event.state&1) == 0:
            # shift not pressed
            self.text.tag_remove("sel", "1.0", "end")
        else:
            if not self.text.index("sel.first"):
                self.text.mark_set("anchor","insert")

            first = self.text.index(dest)
            last = self.text.index("anchor")

            if self.text.compare(first,">",last):
                first,last = last,first

            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", first, last)

        self.text.mark_set("insert", dest)
        self.text.see("insert")
        return "break"

    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("run", "_Run"),
        ("options", "_Options"),
        ("windows", "_Windows"),
        ("help", "_Help"),
    ]

    if macosxSupport.runningAsOSXApp():
        del menu_specs[-3]
        menu_specs[-2] = ("windows", "_Window")


    def createmenubar(self):
        mbar = self.menubar
        self.menudict = menudict = {}
        for name, label in self.menu_specs:
            underline, label = prepstr(label)
            menudict[name] = menu = Menu(mbar, name=name)
            mbar.add_cascade(label=label, menu=menu, underline=underline)

        if macosxSupport.runningAsOSXApp():
            # Insert the application menu
            menudict['application'] = menu = Menu(mbar, name='apple')
            mbar.add_cascade(label='IDLE', menu=menu)

        self.fill_menus()
        self.base_helpmenu_length = self.menudict['help'].index(END)
        self.reset_help_menu_entries()

    def postwindowsmenu(self):
        # Only called when Windows menu exists
        menu = self.menudict['windows']
        end = menu.index("end")
        if end is None:
            end = -1
        if end > self.wmenu_end:
            menu.delete(self.wmenu_end+1, end)
        WindowList.add_windows_to_menu(menu)

    rmenu = None

    def right_menu_event(self, event):
        self.text.tag_remove("sel", "1.0", "end")
        self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
        if not self.rmenu:
            self.make_rmenu()
        rmenu = self.rmenu
        self.event = event
        iswin = sys.platform[:3] == 'win'
        if iswin:
            self.text.config(cursor="arrow")
        rmenu.tk_popup(event.x_root, event.y_root)
        if iswin:
            self.text.config(cursor="ibeam")

    rmenu_specs = [
        # ("Label", "<<virtual-event>>"), ...
        ("Close", "<<close-window>>"), # Example
    ]

    def make_rmenu(self):
        rmenu = Menu(self.text, tearoff=0)
        for label, eventname in self.rmenu_specs:
            def command(text=self.text, eventname=eventname):
                text.event_generate(eventname)
            rmenu.add_command(label=label, command=command)
        self.rmenu = rmenu

    def about_dialog(self, event=None):
        aboutDialog.AboutDialog(self.top,'About IDLE')

    def config_dialog(self, event=None):
        configDialog.ConfigDialog(self.top,'Settings')

    def help_dialog(self, event=None):
        fn=os.path.join(os.path.abspath(os.path.dirname(__file__)),'help.txt')
        textView.view_file(self.top,'Help',fn)

    def python_docs(self, event=None):
        if sys.platform[:3] == 'win':
            os.startfile(self.help_url)
        else:
            webbrowser.open(self.help_url)
        return "break"

    def filename_change_hook(self):
        if self.flist:
            self.flist.filename_changed_edit(self)
        self.saved_change_hook()
       # self.top.update_windowlist_registry(self)
        self.ResetColorizer()

    def saved_change_hook(self):
        pass 
        '''
        short = self.short_title()
        long = self.long_title()
        if short and long:
            title = short + " - " + long
        elif short:
            title = short
        elif long:
            title = long
        else:
            title = "Untitled"
        icon = short or long or title
        if not self.get_saved():
            title = "*%s*" % title
            icon = "*%s" % icon
        self.top.wm_title(title)
        self.top.wm_iconname(icon)
        '''

    def ispythonsource(self, filename):
        if not filename or os.path.isdir(filename):
            return True
        base, ext = os.path.splitext(os.path.basename(filename))
        if os.path.normcase(ext) in (".py", ".pyw"):
            return True
        try:
            f = open(filename)
            line = f.readline()
            f.close()
        except IOError:
            return False
        return line.startswith('#!') and line.find('python') >= 0

    def istrace(self, filename):
        if not filename or os.path.isdir(filename):
            return True

        try:
            with open(filename) as f:
                json.load(f)

        except ValueError, IOError:
            return False

        return True

    def close_hook(self):
        if self.flist:
            self.flist.unregister_maybe_terminate(self)
            self.flist = None

    def set_close_hook(self, close_hook):
        self.close_hook = close_hook

    def _addcolorizer(self):
        if self.color:
            return
        if self.ispythonsource(self.io.filename) or self.istrace(self.io.filename):
            self.color = self.ColorDelegator()
        if self.color:
            self.per.insertfilter(self.color)

    def _rmcolorizer(self):
        if not self.color:
            return
        self.color.removecolors()
        self.per.removefilter(self.color)
        self.color = None

    def ResetColorizer(self):
        "Update the colour theme"
        # Called from self.filename_change_hook and from configDialog.py
        self._rmcolorizer()
        self._addcolorizer()
        theme = idleConf.GetOption('main','Theme','name')
        normal_colors = idleConf.GetHighlight(theme, 'normal')
        cursor_color = idleConf.GetHighlight(theme, 'cursor', fgBg='fg')
        select_colors = idleConf.GetHighlight(theme, 'hilite')
        self.text.config(
            foreground=normal_colors['foreground'],
            background=normal_colors['background'],
            insertbackground=cursor_color,
            selectforeground=select_colors['foreground'],
            selectbackground=select_colors['background'],
            )

    def ResetFont(self):
        "Update the text widgets' font if it is changed"
        # Called from configDialog.py
        fontWeight='normal'
        if idleConf.GetOption('main','EditorWindow','font-bold',type='bool'):
            fontWeight='bold'
        self.text.config(font=(idleConf.GetOption('main','EditorWindow','font'),
                idleConf.GetOption('main','EditorWindow','font-size'),
                fontWeight))

    def RemoveKeybindings(self):
        "Remove the keybindings before they are changed."
        # Called from configDialog.py
        self.Bindings.default_keydefs = keydefs = idleConf.GetCurrentKeySet()
        for event, keylist in keydefs.items():
            self.text.event_delete(event, *keylist)
        for extensionName in self.get_standard_extension_names():
            xkeydefs = idleConf.GetExtensionBindings(extensionName)
            if xkeydefs:
                for event, keylist in xkeydefs.items():
                    self.text.event_delete(event, *keylist)

    def ApplyKeybindings(self):
        "Update the keybindings after they are changed"
        # Called from configDialog.py
        self.Bindings.default_keydefs = keydefs = idleConf.GetCurrentKeySet()
        self.apply_bindings()
        for extensionName in self.get_standard_extension_names():
            xkeydefs = idleConf.GetExtensionBindings(extensionName)
            if xkeydefs:
                self.apply_bindings(xkeydefs)
        #update menu accelerators
        menuEventDict = {}
        for menu in self.Bindings.menudefs:
            menuEventDict[menu[0]] = {}
            for item in menu[1]:
                if item:
                    menuEventDict[menu[0]][prepstr(item[0])[1]] = item[1]
        for menubarItem in self.menudict.keys():
            menu = self.menudict[menubarItem]
            end = menu.index(END) + 1
            for index in range(0, end):
                if menu.type(index) == 'command':
                    accel = menu.entrycget(index, 'accelerator')
                    if accel:
                        itemName = menu.entrycget(index, 'label')
                        event = ''
                        if menuEventDict.has_key(menubarItem):
                            if menuEventDict[menubarItem].has_key(itemName):
                                event = menuEventDict[menubarItem][itemName]
                        if event:
                            accel = get_accelerator(keydefs, event)
                            menu.entryconfig(index, accelerator=accel)

    def reset_help_menu_entries(self):
        "Update the additional help entries on the Help menu"
        help_list = idleConf.GetAllExtraHelpSourcesList()
        helpmenu = self.menudict['help']
        # first delete the extra help entries, if any
        helpmenu_length = helpmenu.index(END)
        if helpmenu_length > self.base_helpmenu_length:
            helpmenu.delete((self.base_helpmenu_length + 1), helpmenu_length)
        # then rebuild them
        if help_list:
            helpmenu.add_separator()
            for entry in help_list:
                cmd = self.__extra_help_callback(entry[1])
                helpmenu.add_command(label=entry[0], command=cmd)
        # and update the menu dictionary
        self.menudict['help'] = helpmenu

    def __extra_help_callback(self, helpfile):
        "Create a callback with the helpfile value frozen at definition time"
        def display_extra_help(helpfile=helpfile):
            if not helpfile.startswith(('www', 'http')):
                url = os.path.normpath(helpfile)
            if sys.platform[:3] == 'win':
                os.startfile(helpfile)
            else:
                webbrowser.open(helpfile)
        return display_extra_help

    def update_recent_files_list(self, new_file=None):
        "Load and update the recent files list and menus"
        rf_list = []
        if os.path.exists(self.recent_files_path):
            rf_list_file = open(self.recent_files_path,'r')
            try:
                rf_list = rf_list_file.readlines()
            finally:
                rf_list_file.close()
        if new_file:
            new_file = os.path.abspath(new_file) + '\n'
            if new_file in rf_list:
                rf_list.remove(new_file)  # move to top
            rf_list.insert(0, new_file)
        # clean and save the recent files list
        bad_paths = []
        for path in rf_list:
            if '\0' in path or not os.path.exists(path[0:-1]):
                bad_paths.append(path)
        rf_list = [path for path in rf_list if path not in bad_paths]
        ulchars = "1234567890ABCDEFGHIJK"
        rf_list = rf_list[0:len(ulchars)]
        rf_file = open(self.recent_files_path, 'w')
        try:
            rf_file.writelines(rf_list)
        finally:
            rf_file.close()
        # for each edit window instance, construct the recent files menu
        for instance in self.top.instance_dict.keys():
            menu = instance.recent_files_menu
            menu.delete(1, END)  # clear, and rebuild:
            for i, file in zip(count(), rf_list):
                file_name = file[0:-1]  # zap \n
                # make unicode string to display non-ASCII chars correctly
                ufile_name = self._filename_to_unicode(file_name)
                callback = instance.__recent_file_callback(file_name)
                menu.add_command(label=ulchars[i] + " " + ufile_name,
                                 command=callback,
                                 underline=0)

    def __recent_file_callback(self, file_name):
        def open_recent_file(fn_closure=file_name):
            self.io.open(editFile=fn_closure)
        return open_recent_file

    def short_title(self):
        filename = self.io.filename
        if filename:
            filename = os.path.basename(filename)
        # return unicode string to display non-ASCII chars correctly
        return self._filename_to_unicode(filename)

    def long_title(self):
        # return unicode string to display non-ASCII chars correctly
        return self._filename_to_unicode(self.io.filename or "")

    def getwindowlines(self):
        text = self.text
        top = self.getlineno("@0,0")
        bot = self.getlineno("@0,65535")
        if top == bot and text.winfo_height() == 1:
            # Geometry manager hasn't run yet
            height = int(text['height'])
            bot = top + height - 1
        return top, bot

    def getlineno(self, mark="insert"):
        text = self.text
        return int(float(text.index(mark)))

    def get_geometry(self):
        "Return (width, height, x, y)"
        geom = self.top.wm_geometry()
        m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        tuple = (map(int, m.groups()))
        return tuple

    def close_event(self, event):
        self.close()

    def close(self):
        self._close()

    def _close(self):
        if self.io.filename:
           pass
           # self.update_recent_files_list(new_file=self.io.filename)
        WindowList.unregister_callback(self.postwindowsmenu)
        self.io.close()
        self.io = None
        if self.color:
            self.color.close(False)
            self.color = None
        self.text = None
        self.tkinter_vars = None
        self.per.close()
        self.per = None
        self.top.destroy()
        if self.close_hook:
            # unless override: unregister from flist, terminate if last window
            self.close_hook()

    def __recent_file_callback(self, file_name):
        def open_recent_file(fn_closure=file_name):
            self.io.open(editFile=fn_closure)
        return open_recent_file

    def apply_bindings(self, keydefs=None):
        if keydefs is None:
            keydefs = self.Bindings.default_keydefs
        text = self.text
        text.keydefs = keydefs
        for event, keylist in keydefs.items():
            if keylist:
                text.event_add(event, *keylist)

    def fill_menus(self, menudefs=None, keydefs=None):
        """Add appropriate entries to the menus and submenus

        Menus that are absent or None in self.menudict are ignored.
        """
        if menudefs is None:
            menudefs = self.Bindings.menudefs
        if keydefs is None:
            keydefs = self.Bindings.default_keydefs
        menudict = self.menudict
        text = self.text
        for mname, entrylist in menudefs:
            menu = menudict.get(mname)
            if not menu:
                continue
            for entry in entrylist:
                if not entry:
                    menu.add_separator()
                else:
                    label, eventname = entry
                    checkbutton = (label[:1] == '!')
                    if checkbutton:
                        label = label[1:]
                    underline, label = prepstr(label)
                    accelerator = get_accelerator(keydefs, eventname)
                    def command(text=text, eventname=eventname):
                        text.event_generate(eventname)
                    if checkbutton:
                        var = self.get_var_obj(eventname, BooleanVar)
                        menu.add_checkbutton(label=label, underline=underline,
                            command=command, accelerator=accelerator,
                            variable=var)
                    else:
                        menu.add_command(label=label, underline=underline,
                                         command=command,
                                         accelerator=accelerator)

    # Tk implementations of "virtual text methods" -- each platform
    # reusing IDLE's support code needs to define these for its GUI's
    # flavor of widget.

    # Is character at text_index in a Python string?  Return 0 for
    # "guaranteed no", true for anything else.  This info is expensive
    # to compute ab initio, but is probably already known by the
    # platform's colorizer.

    def is_char_in_string(self, text_index):
        if self.color:
            # Return true iff colorizer hasn't (re)gotten this far
            # yet, or the character is tagged as being in a string
            return self.text.tag_prevrange("TODO", text_index) or \
                   "STRING" in self.text.tag_names(text_index)
        else:
            # The colorizer is missing: assume the worst
            return 1

    # Our editwin provides a is_char_in_string function that works
    # with a Tk text index, but PyParse only knows about offsets into
    # a string. This builds a function for PyParse that accepts an
    # offset.

    def _build_char_in_string_func(self, startindex):
        def inner(offset, _startindex=startindex,
                  _icis=self.is_char_in_string):
            return _icis(_startindex + "+%dc" % offset)
        return inner

    # Make string that displays as n leading blanks.

    def _make_blanks(self, n):
        if self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            return '\t' * ntabs + ' ' * nspaces
        else:
            return ' ' * n

def prepstr(s):
    # Helper to extract the underscore from a string, e.g.
    # prepstr("Co_py") returns (2, "Copy").
    i = s.find('_')
    if i >= 0:
        s = s[:i] + s[i+1:]
    return i, s

keynames = {
 'bracketleft': '[',
 'bracketright': ']',
 'slash': '/',
}

def get_accelerator(keydefs, eventname):
    keylist = keydefs.get(eventname)
    if not keylist:
        return ""
    s = keylist[0]
    s = re.sub(r"-[a-z]\b", lambda m: m.group().upper(), s)
    s = re.sub(r"\b\w+\b", lambda m: keynames.get(m.group(), m.group()), s)
    s = re.sub("Key-", "", s)
    s = re.sub("Cancel","Ctrl-Break",s)   # dscherer@cmu.edu
    s = re.sub("Control-", "Ctrl-", s)
    s = re.sub("-", "+", s)
    s = re.sub("><", " ", s)
    s = re.sub("<", "", s)
    s = re.sub(">", "", s)
    return s

def fixwordbreaks(root):
    # Make sure that Tk's double-click and next/previous word
    # operations use our definition of a word (i.e. an identifier)
    tk = root.tk
    tk.call('tcl_wordBreakAfter', 'a b', 0) # make sure word.tcl is loaded
    tk.call('set', 'tcl_wordchars', '[a-zA-Z0-9_]')
    tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_]')

def test():
    root = Tk()
    fixwordbreaks(root)
    root.withdraw()
    if sys.argv[1:]:
        filename = sys.argv[1]
    else:
        filename = None
    edit = TraceDisplayWindow(root=root, filename=filename)
    edit.set_close_hook(root.quit)
    edit.text.bind("<<close-all-windows>>", edit.close_event)
    root.mainloop()
    root.destroy()

if __name__ == '__main__':
    test()
