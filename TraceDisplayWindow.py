import sys
import json
from Tkinter import *
from configHandler import idleConf
from EditorWindow import EditorWindow, fixwordbreaks

class TraceDisplayWindow(EditorWindow):

    menu_specs = [
        ("file", "_File"),
        ("options", "_Options"),
        ("windows", "_Windows"),
        ("help", "_Help"),
    ]

    def __init__(self, *args, **kwargs):
        '''Calls the superclass __init__ method then takes apart the superclass
        GUI and assembles a new one using the grid manager.''' 
        self.trace = None

        EditorWindow.__init__(self, *args, **kwargs)

        #remove the existing layout and usage of the pack manager 
        self.text.pack_forget()
        self.status_bar.pack_forget()
        self.vbar.pack_forget()
        self.text_frame.pack_forget()

        small_height = int(self.height) / 6
        small_width = int(self.width) * 5 / 6
        self.text.configure(height = small_height * 3, width = small_width, wrap = WORD)

        self.annotation = Text(self.text_frame, height = small_height, width =
                small_width, wrap = WORD)

        self.locals = Text(self.text_frame, height = small_height, width =
                small_width, wrap = WORD)

        self.globals = Text(self.text_frame, height = small_height, width =
                small_width, wrap = WORD)

        self.stdout = Text(self.text_frame, height = small_height, wrap = WORD)

        self.play_button = Button(self.text_frame, text = 'Play', command = self.play)
        rewind_button = Button(self.text_frame, text = 'Rewind', command = self.rewind)
        forward_button = Button(self.text_frame, text = 'Step Forward', command = self.step_forward)

        back_button = Button(self.text_frame, text = 'Step Back', command = self.step_back)

        text_label = Label(self.text_frame, text = 'Source Code:', font = ('sans', 10)) 
        anno_label = Label(self.text_frame, text = 'Explanation:', font = ('sans', 10)) 
        locals_label = Label(self.text_frame, text = 'Local Variables:', font = ('sans', 10)) 
        globals_label = Label(self.text_frame, text = 'Global Variables :', font = ('sans', 10)) 
        stdout_label = Label(self.text_frame, text = 'Output:', font = ('sans', 12)) 

        text_scroll = Scrollbar(self.text_frame, command = self.text.yview )
        annotation_scroll = Scrollbar(self.text_frame, command = self.annotation.yview )
        locals_scroll = Scrollbar(self.text_frame, command = self.locals.yview )
        globals_scroll = Scrollbar(self.text_frame, command = self.globals.yview )
        stdout_scroll = Scrollbar(self.text_frame, command = self.stdout.yview )

        self.text.config(yscrollcommand = text_scroll.set)
        self.annotation.config(yscrollcommand = annotation_scroll.set)
        self.locals.config(yscrollcommand = locals_scroll.set)
        self.globals.config(yscrollcommand = globals_scroll.set)
        self.stdout.config(yscrollcommand = stdout_scroll.set)

        fontWeight = 'normal'

        if idleConf.GetOption('main','EditorWindow','font-bold',type='bool'):
            fontWeight = 'bold'

        for text_box in ('stdout', 'annotation', 'globals', 'locals'):
            getattr(self, text_box).config(
                    font = (idleConf.GetOption('main','EditorWindow','font'), 
                        idleConf.GetOption('main','EditorWindow','font-size'), fontWeight))

        self.text_frame.grid(row = 0, column = 0, rowspan = 9, columnspan = 9, sticky = NSEW)

        self.play_button.grid(row = 1, column = 1, sticky = EW)
        rewind_button.grid(row = 1, column = 2, sticky = EW)
        forward_button.grid(row = 1, column = 3, sticky = EW)
        back_button.grid(row = 1, column = 4, columnspan = 2, sticky = EW)

        text_label.grid(row = 2, column = 1, columnspan = 4, sticky = NSEW)
        globals_label.grid(row = 6, column = 6, sticky = NSEW)
        locals_label.grid(row = 4, column = 6, sticky = NSEW)
        anno_label.grid(row = 2, column = 6, sticky = NSEW)
        stdout_label.grid(row = 8, column = 1, columnspan = 6, sticky = NSEW)

        self.text.grid(row = 3, column = 1, rowspan = 6, columnspan = 4, sticky = NSEW)
        self.annotation.grid(row = 3, column = 6, sticky = NSEW)
        self.globals.grid(row = 7, column = 6, sticky = NSEW)
        self.locals.grid(row = 5, column = 6, sticky = NSEW)
        self.stdout.grid(row = 9, column = 1, columnspan = 6, sticky = NSEW)

        text_scroll.grid(row = 3, column = 5, rowspan = 5, sticky = NSEW)
        annotation_scroll.grid(row = 3, column = 7, sticky = NSEW)
        locals_scroll.grid(row = 5, column = 7, sticky = NSEW)
        globals_scroll.grid(row = 7, column = 7,  sticky = NSEW)
        stdout_scroll.grid(row = 9, column = 7, sticky = NSEW)

        self.text.config( highlightbackground = 'grey' )
        self.stdout.config( highlightbackground = 'grey' )
        self.annotation.config( highlightbackground = 'grey' )
        self.globals.config( highlightbackground = 'grey' )
        self.locals.config( highlightbackground = 'grey' )

        self.text.config(state=DISABLED)
        self.stdout.config(state=DISABLED)
        self.annotation.config(state=DISABLED)
        self.globals.config(state=DISABLED)
        self.locals.config(state=DISABLED)

        self.current_step = 0
        self.finished = False
        self.paused = True

        #in seconds
        self.step_rate=1.5
        
    def insert(self, target, text, color = None):
        '''Enables the text box named target, inserts text of colored color, and disables the
        text box again.'''

        getattr(self, target).config(state=NORMAL)

        if color: 
            getattr(self, target).insert(END, text, 'color_%s' % color)
            getattr(self, target).tag_configure('color_%s' % color, foreground = color)

        else:
            getattr(self, target).insert(END, text)

        if target not in ('globals', 'locals'):
            getattr(self, target).see('end')
        getattr(self, target).config(state = DISABLED)

    def clear(self, target):
        '''Clears all text out of Text widget target.'''

        getattr(self, target).config(state=NORMAL)
        getattr(self, target).delete('1.0', 'end')
        getattr(self, target).config(state=DISABLED)

    def clear_all(self):
        for target in ('text', 'stdout', 'annotation', 'globals', 'locals'):
            self.clear(target)

    def highlight_line(self, target, lineno, clear_highlighting = True):
        '''Highlights the line linenno in the target Text widget.'''

        getattr(self, target).config(state=NORMAL)

        if clear_highlighting:
            self.clear_highlighting(target)

        getattr(self, target).tag_add('highlight', '%s.0' % lineno, '%s.end' % lineno)
        getattr(self, target).tag_configure('highlight', background = 'yellow')

        #This makes sure the highlighted region is visible and has some context
        getattr(self, target).see('highlight.first')
        getattr(self, target).see('highlight.first + 5l')
        
        getattr(self, target).config(state=DISABLED)

    def clear_highlighting(self, target):
        '''Clears all highlighting out of Text widget target.'''

        getattr(self, target).config(state=NORMAL)
        getattr(self, target).tag_remove('highlight', '1.0', 'end')
        getattr(self, target).config(state=DISABLED)

    def clear_all_highlighting(self):
        for target in ('text', 'stdout', 'annotation', 'globals', 'locals'):
            self.clear_highlighting(target)

    def play(self):
        '''Starts/resumes advancing execution or pauses execution depending on
        the current state of the program.'''

        self.paused=not self.paused 
        if not self.paused:
            self.play_button.config(text='Pause')
            self.text.after(0, self.play_action)
        else:
            self.play_button.config(text='Play')

    def play_action(self):
        if not self.paused and not self.finished:
            self.step_forward()
            self.text.after(int(self.step_rate * 1000), self.play_action)

    def highlight_changes(self, current_step, previous_step):
        '''Inserts the globals and locals into their respective Text boxes,
        highlighting any differences between the previous contents and the
        current one.'''
        
        for target in ('globals', 'locals'):
            if target in current_step:
                self.clear(target)
                globals=current_step[target] 
                old_globals = globals

                if target in previous_step:
                    old_globals = previous_step[target]

                lineno = 0
                for entry in globals:
                    lineno += 1
                    self.insert(target, "%s = %s\n" % (str(entry), str(globals[entry])))

                    if entry not in old_globals or globals[entry] != old_globals[entry]:
                        self.highlight_line(target, lineno, clear_highlighting = False)
                        self.globals.see('%d.0' % lineno)

    def step_forward(self):
        '''Moves to the next dictionary in the trace and inserts the data it contains,
        advancing the highlighting as appropriate.'''

        if not self.finished:
            step = self.trace[self.current_step]
            prev_step = step

            if self.current_step > 0:
                prev_step = self.trace[self.current_step - 1] 

            self.highlight_line('text', step['line']+1)

            if 'stdout' in step:
                self.insert('stdout', step['stdout'])

            if 'stderr' in step:
                self.insert('stdout', step['stderr'], 'red')

            self.clear('annotation')
            if 'annotation' in step:
                self.insert('annotation', step['annotation'])

            self.highlight_changes(step, prev_step)
            self.current_step+=1

        else:
            self.clear_all_highlighting()

        if self.current_step == len(self.trace):
            self.finished=True
    
    def step_back(self):
        '''Goes to the previous dictionary in the trace and recreates the state
        of the tracer at that point by replaying stdout.'''

        if self.current_step > 0:
            try:
                step = self.trace[self.current_step]
            except IndexError:
                step = self.trace[len(self.trace)-1]
               
            prev_step = self.trace[self.current_step-1]

            #remove the last thing printed to stdout
            if 'stdout' in prev_step or 'stderr' in prev_step:
                self.clear('stdout')
                for previous in range(self.current_step-1):
                    prev_step=self.trace[previous]
                    if 'stdout' in prev_step:
                        self.insert('stdout', prev_step['stdout'])
                    if 'stderr' in prev_step:
                        self.insert('stdout', prev_step['stderr'], 'red')

            self.clear('annotation')

            if 'annotation' in prev_step:
                self.insert('annotation', prev_step['annotation'])

            self.clear('globals')
            self.clear('locals')

            self.highlight_changes(prev_step, self.trace[self.current_step-2])

            if self.finished:
                self.finished = False
               
            self.current_step -= 1
            step = self.trace[self.current_step]
            self.highlight_line('text', step['line']+1)

        else:
            self.rewind()

    def rewind(self):
        '''Sets all parameters back to their original states (including
        unpausing)'''

        self.clear_all_highlighting()

        for output in ('stdout', 'annotation', 'globals', 'locals'):
            self.clear(output)

        self.current_step=0
        self.finished=False
        self.paused=True
        self.play_button.config(text='Play')
        self.text.see('1.0')

    def ResetFont(self):
        EditorWindow.ResetFont(self)
        fontWeight = 'normal'

        if idleConf.GetOption('main','EditorWindow','font-bold',type='bool'):
            fontWeight = 'bold'

        for text_box in ('stdout', 'annotation', 'globals', 'locals'):
            getattr(self, text_box).config(font=(idleConf.GetOption('main','EditorWindow','font'), idleConf.GetOption('main','EditorWindow','font-size'), fontWeight))

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
