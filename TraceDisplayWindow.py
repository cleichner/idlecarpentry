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

        self.text.configure(height = 21, width = 70, wrap = WORD)

        self.annotation = Text(self.text_frame, height = 7, width = 70, wrap = WORD)
        self.locals = Text(self.text_frame, height = 7, width = 70, wrap = WORD)
        self.globals = Text(self.text_frame, height = 7, width = 70, wrap = WORD)
        self.stdout = Text(self.text_frame, height = 7, wrap = WORD)

        self.play_button = Button(self.text_frame, text = 'Play', command = self.play)
        rewind_button = Button(self.text_frame, text = 'Rewind', command = self.rewind)
        forward_button = Button(self.text_frame, text = 'Step Forward', command = self.step_forward)
        back_button = Button(self.text_frame, text = 'Step Back', command = self.step_back)

        text_label = Label(self.text_frame, text = 'text:', font = ('sans', 10))
        anno_label = Label(self.text_frame, text = 'explanation:', font = ('sans', 10))
        locals_label = Label(self.text_frame, text = 'locals:', font = ('sans', 10))
        globals_label = Label(self.text_frame, text = 'globals:', font = ('sans', 10))
        stdout_label = Label(self.text_frame, text = 'stdout:', font = ('sans', 12))

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
