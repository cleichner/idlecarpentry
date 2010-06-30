from Tkinter import *
import json
import time
import sys

class TraceApp(object):
    def __init__(self, filename):

        root = Tk()
        root.title("Trace Reader")

        button_frame = Frame(root) 
        play = Button( button_frame, text='Play', command=self.play_cb)
        pause = Button( button_frame, text='Pause', command=self.pause_cb)
        rewind = Button( button_frame, text='Rewind', command=self.rewind_cb)
        step_back = Button( button_frame, text='Step Forward', command=self.step_forward_cb)
        step_forward = Button( button_frame, text='Step Back', command=self.step_back_cb)
        fast = Button( button_frame, text='Fast', command=self.fast_cb)

        self.source = Text(root)

        out_label = Label(text='stdout:', font=('sans', 12))

        self.stdout = Text(root, height=7)

        for widget in (button_frame, self.source, out_label, self.stdout):
            widget.pack(side=TOP, expand=1, fill=BOTH)

        for button in (play, pause, rewind, step_back, step_forward, fast):
            button.pack(side=LEFT)

        with open(filename, 'r') as f:
            raw_trace=json.load(f)
        self.trace=raw_trace['trace']
        
        self.source.insert(1.0, raw_trace['source'])
        self.source.config(state=DISABLED)
        self.stdout.config(state=DISABLED)

        self.current_line=0
        self.paused=False
        self.finished=False

        #in seconds
        self.step_rate=0.55
        
        root.mainloop()

    def fast_cb(self):
        self.step_rate=0.001

    def stdout_insert(self, text):
        self.stdout.config(state=NORMAL)
        self.stdout.insert(END, text)
        self.stdout.see(END)
        self.stdout.config(state=DISABLED)

    def stdout_clear(self):
        self.stdout.config(state=NORMAL)
        self.stdout.delete('1.0', 'end')
        self.stdout.config(state=DISABLED)

    def highlight_line(self, lineno):
        self.source.config(state=NORMAL)
        self.clear_highlighting()
        self.source.tag_add('highlight', '%s.0' % lineno, '%s.end' % lineno)
        self.source.tag_configure('highlight', background='yellow')
        self.source.config(state=DISABLED)

    def clear_highlighting(self):
        self.source.config(state=NORMAL)
        self.source.tag_remove('highlight', '1.0', 'end')
        self.source.config(state=DISABLED)

    def play_cb(self):
        if not self.paused and not self.finished:
            self.step_forward_cb()
            self.source.after(int(self.step_rate * 1000), self.play_cb)

    def pause_cb(self):
        self.paused=not self.paused 
        if not self.paused:
            self.play_cb()

    def step_forward_cb(self):
        '''Moves to the next trace dictionary and inserts the data it contains,
        advancing the highlighting as appropriate.'''

        if not self.finished:
            step = self.trace[self.current_line]
            self.highlight_line(step['line']+1)
            self.source.see('%d.0' % (step['line']+1))
            if 'stdout' in step:
                self.stdout_insert(step['stdout'])
            self.current_line+=1

        if self.current_line == len(self.trace) - 1:
            self.clear_highlighting()
            self.finished=True

#NEEDS WORK
    def step_back_cb(self):
        if self.current_line <= 0:
            self.rewind_cb()

        else:
            step= self.trace[self.current_line]
            if 'stdout' in step:
                self.stdout.config(state=NORMAL)
                current_text=self.stdout.get('1.0', 'end+1c')
                self.stdout.delete('1.0', 'end+1c')
#replace may need to be rewritten so it starts at the end
                self.stdout.insert('1.0', current_text.replace(step['stdout'], '', 1))
                self.stdout.config(state=DISABLED)

            self.current_line -= 1
            step = self.trace[self.current_line]
            if self.finished:
                self.finished = False
            self.highlight_line(step['line']+1)

    def rewind_cb(self):
        '''Sets all parameters back to their original states (including unpausing)'''
        self.clear_highlighting()
        self.stdout_clear()
        self.current_line=0
        self.finished=False
        self.paused=False
        self.source.see('1.0')

if __name__=='__main__':
    if len(sys.argv) == 2:
        TraceApp(sys.argv[1])
    else:
        print 'ERROR: This takes one trace file as an arguement.'
