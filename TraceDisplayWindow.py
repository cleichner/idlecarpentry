import sys
import json
from Tkinter import *
from configHandler import idleConf
from MultiCall import MultiCallCreator
from EditorWindow import EditorWindow, fixwordbreaks

class TraceDisplayWindow(EditorWindow):

    def __init__(self, *args, **kwargs):

        EditorWindow.__init__(self, *args, **kwargs)

        #remove the existing layout and usage of the pack manager 
        self.text.pack_forget()
        self.status_bar.pack_forget()
        self.vbar.pack_forget()
        self.text_frame.pack_forget()

        old_text = self.text.get('1.0', 'end')
        self.text = Text(self.top, height = 21, width = 70, wrap = WORD)
        self.text.insert(INSERT, old_text)

        self.annotation = Text(self.top, height = 7, width = 70, wrap = WORD)
        self.locals = Text(self.top, height = 7, width = 70, wrap = WORD)
        self.globals = Text(self.top, height = 7, width = 70, wrap = WORD)
        self.stdout = Text(self.top, height = 7, wrap = WORD)

        self.play_button = Button(self.top, text = 'Play', command = self.play)
        rewind_button = Button(self.top, text = 'Rewind', command = self.rewind)
        forward_button = Button(self.top, text = 'Step Forward', command = self.step_forward)
        back_button = Button(self.top, text = 'Step Back', command = self.step_back)

        self.play_button.grid(row = 0, column = 0, sticky = EW)
        rewind_button.grid(row = 0, column = 1, sticky = EW)
        forward_button.grid(row = 0, column = 2, sticky = EW)
        back_button.grid(row = 0, column = 3, columnspan = 2, sticky = EW)

        text_label = Label(self.top, text = 'text:', font = ('sans', 10))
        anno_label = Label(self.top, text = 'explanation:', font = ('sans', 10))
        locals_label = Label(self.top, text = 'locals:', font = ('sans', 10))
        globals_label = Label(self.top, text = 'globals:', font = ('sans', 10))
        stdout_label = Label(self.top, text = 'stdout:', font = ('sans', 12))

        text_label.grid(row = 1, column = 0, columnspan = 4, sticky = NSEW)
        globals_label.grid(row = 5, column = 5, sticky = NSEW)
        locals_label.grid(row = 3, column = 5, sticky = NSEW)
        anno_label.grid(row = 1, column = 5, sticky = NSEW)
        stdout_label.grid(row = 7, column = 0, columnspan = 6, sticky = NSEW)

        self.text.grid(row = 2, column = 0, rowspan = 6, columnspan = 4, sticky = NSEW)
        self.annotation.grid(row = 2, column = 5, sticky = NSEW)
        self.globals.grid(row = 6, column = 5, sticky = NSEW)
        self.locals.grid(row = 4, column = 5, sticky = NSEW)
        self.stdout.grid(row = 8, column = 0, columnspan = 6, sticky = NSEW)

        text_scroll = Scrollbar(self.top, command = self.text.yview )
        text_scroll.grid(row = 2, column = 4, rowspan = 5, sticky = NSEW)
        self.text.config(yscrollcommand = text_scroll.set)

        annotation_scroll = Scrollbar(self.top, command = self.annotation.yview )
        locals_scroll = Scrollbar(self.top, command = self.locals.yview )
        globals_scroll = Scrollbar(self.top, command = self.globals.yview )
        stdout_scroll = Scrollbar(self.top, command = self.stdout.yview )

        annotation_scroll.grid(row = 2, column = 6, sticky = NSEW)
        self.annotation.config(yscrollcommand = annotation_scroll.set)

        locals_scroll.grid(row = 4, column = 6, sticky = NSEW)
        self.locals.config(yscrollcommand = locals_scroll.set)

        globals_scroll.grid(row = 6, column = 6,  sticky = NSEW)
        self.globals.config(yscrollcommand = globals_scroll.set)

        stdout_scroll.grid(row = 8, column = 6, sticky = NSEW)
        self.stdout.config(yscrollcommand = stdout_scroll.set)

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

        self.trace = None
        self.current_line = 0
        self.paused = True
        self.finished = False

        #in seconds
        self.step_rate=1.5
        
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
        self.paused=True
        self.play_button.config(text='Play')
        self.text.see('1.0')

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
