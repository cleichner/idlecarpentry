from Tkinter import *
import json
import sys

class TraceApp(object):
    def __init__(self, filename):

        root = Tk()
        root.title("Trace Reader")

        button_frame = Frame(root) 
        center_frame = Frame(root) 
        anno_frame = Frame(center_frame) 
        source_frame = Frame(center_frame) 

        play_button = Button( button_frame, text='Play', command=self.play)
        pause_button = Button( button_frame, text='Pause', command=self.pause)
        rewind_button = Button( button_frame, text='Rewind', command=self.rewind)
        forward_button = Button( button_frame, text='Step Forward', command=self.step_forward)
        back_button = Button( button_frame, text='Step Back', command=self.step_back)
        fast_button = Button( button_frame, text='Fast', command=self.fast)

        out_label = Label(text='stdout:', font=('sans', 12))
        globals_label = Label(anno_frame, text='globals:', font=('sans', 10))
        locals_label = Label(anno_frame, text='locals:', font=('sans', 10))
        anno_label = Label(anno_frame, text='explanation:', font=('sans', 10))
        source_label = Label(source_frame, text='source:', font=('sans', 10))

        self.source = Text(source_frame, wrap=WORD)
        self.stdout = Text(root, height=7)
        self.annotation = Text(anno_frame, height=7, wrap=WORD)
        self.globals = Text(anno_frame, height=7, wrap=WORD)
        self.locals = Text(anno_frame, height=7, wrap=WORD)

        for widget in (button_frame, center_frame, out_label, self.stdout):
            widget.pack(side=TOP, expand=1, fill=BOTH)

        source_frame.pack(side=LEFT, expand=1, fill=BOTH)
        source_label.pack(side=TOP, expand=1, fill=BOTH)
        anno_frame.pack(side=LEFT, expand=1, fill=BOTH)

        for widget in (anno_label, self.annotation, locals_label, self.locals, globals_label, self.globals):
            widget.pack(side=TOP, expand=1, fill=BOTH)

        for button in (play_button, pause_button, rewind_button, forward_button, back_button, fast_button):
            button.pack(side=LEFT)

        self.source.pack(side=TOP, expand=1, fill=BOTH)

        with open(filename, 'r') as f:
            raw_trace=json.load(f)
        self.trace=raw_trace['trace']
        
        self.source.insert(1.0, raw_trace['source'])
        self.source.config(state=DISABLED)
        self.stdout.config(state=DISABLED)
        self.annotation.config(state=DISABLED)
        self.globals.config(state=DISABLED)
        self.locals.config(state=DISABLED)

        self.current_line=0
        self.paused=False
        self.finished=False

        #in seconds
        self.step_rate=1.5
        
        root.mainloop()

    def fast(self):
        self.step_rate=.3

    def insert(self, target, text):
        getattr(self, target).config(state=NORMAL)
        getattr(self, target).insert(END, text)
        getattr(self, target).see(END)
        getattr(self, target).config(state=DISABLED)

    def clear(self, target):
        getattr(self, target).config(state=NORMAL)
        getattr(self, target).delete('1.0', 'end')
        getattr(self, target).config(state=DISABLED)

    def clear_all(self):
        for target in ('source', 'stdout', 'annotation', 'globals', 'locals'):
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
        for target in ('source', 'stdout', 'annotation', 'globals', 'locals'):
            self.clear_highlighting(target)

    def play(self):
        if not self.paused and not self.finished:
            self.step_forward()
            self.source.after(int(self.step_rate * 1000), self.play)

    def pause(self):
        self.paused=not self.paused 
        if not self.paused:
            self.play()

    def step_forward(self):
        '''Moves to the next trace dictionary and inserts the data it contains,
        advancing the highlighting as appropriate.'''

        if not self.finished:
            step = self.trace[self.current_line]
            self.highlight_line('source', step['line']+1)

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
            self.highlight_line('source', step['line']+1)

    def rewind(self):
        '''Sets all parameters back to their original states (including
        unpausing)'''

        self.clear_all_highlighting()

        for output in ('stdout', 'annotation', 'globals', 'locals'):
            self.clear(output)

        self.current_line=0
        self.finished=False
        self.paused=False
        self.source.see('1.0')

if __name__=='__main__':
    if len(sys.argv) == 2:
        TraceApp(sys.argv[1])
    else:
        print 'ERROR: This takes one trace file as an arguement.'
