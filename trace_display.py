from Tkinter import *
import json
import time
import sys

class TraceApp(object):
    def __init__(self, filename):

        root = Tk()
        root.title("Trace Reader")

        button_frame = Frame(root) 
        play_button = Button( button_frame, text='Play', command=self.play)
        pause_button = Button( button_frame, text='Pause', command=self.pause)
        rewind_button = Button( button_frame, text='Rewind', command=self.rewind)
        back_button = Button( button_frame, text='Step Forward', command=self.step_forward)
        forward_button = Button( button_frame, text='Step Back', command=self.step_back)

        self.source = Text(root)

        out_label = Label(text='stdout:', font=('sans', 12))

        self.stdout = Text(root, height=7)

        for widget in (button_frame, self.source, out_label, self.stdout):
            widget.pack(side=TOP, expand=1, fill=BOTH)

        for button in (play_button, pause_button, rewind_button, back_button, forward_button):
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
        self.step_rate=0.6
        
        root.mainloop()

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
        self.source.see('highlight.first')
        self.source.config(state=DISABLED)

    def clear_highlighting(self):
        self.source.config(state=NORMAL)
        self.source.tag_remove('highlight', '1.0', 'end')
        self.source.config(state=DISABLED)

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
            self.highlight_line(step['line']+1)
            if 'stdout' in step:
                self.stdout_insert(step['stdout'])
            self.current_line+=1

        if self.current_line == len(self.trace) - 1:
            self.clear_highlighting()
            self.finished=True

    def step_back(self):
        if self.current_line <= 0:
            self.rewind()

        else:
            step = self.trace[self.current_line]

            #remove the last thing printed to stdout
            if 'stdout' in step:
                self.stdout.config(state=NORMAL)
                self.stdout.delete('1.0', 'end+1c')
                for previous in range(self.current_line):
                    prev_step=self.trace[previous]
                    if 'stdout' in prev_step:
                        self.stdout.insert('insert', prev_step['stdout'])

                self.stdout.config(state=DISABLED)

            if self.finished:
                self.finished = False
                
            self.current_line -= 1
            step = self.trace[self.current_line]
            self.highlight_line(step['line']+1)

    def rewind(self):
        '''Sets all parameters back to their original states (including
        unpausing)'''

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
