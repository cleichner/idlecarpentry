from __future__ import print_function
from Tkinter import *
from OrderedDict import OrderedDict
import json
import sys

#ISSUES
#selecting doesn't work across the entire widget
#lines don't expand well
       
class FoldManager(object):
    '''This takes a source file and splits it into the source and annotations
    as defined by the parse_source method and displays them in a split window
    which features folding.'''

    def __init__(self, raw_source):
        '''Defines the GUI, source text, annotation text and the folding
        dictionary.  It then inserts the source text and annotation text into
        their appropriate places in the GUI.'''
        
        self.raw_source=raw_source

        self.root=Tk()
        self.root.wm_title('Folding and Annotation Parsing Demo')

        frame=Frame(self.root)
        yscrollbar = Scrollbar(frame, command=self.y_scroll)
        yscrollbar.pack(side=RIGHT, fill=Y)

        self.width=80
        self.source_text=Text(frame, wrap=NONE, width=self.width)
        self.annotation_text=Text(frame, wrap=NONE, yscrollcommand=yscrollbar.set, width=self.width)
        self.stdout = Text(self.root, height=7)

        button_frame = Frame(self.root) 
        play_button = Button( button_frame, text='Play', command=self.play)
        pause_button = Button( button_frame, text='Pause', command=self.pause)
        rewind_button = Button( button_frame, text='Rewind', command=self.rewind)
        back_button = Button( button_frame, text='Step Forward', command=self.step_forward)
        forward_button = Button( button_frame, text='Step Back', command=self.step_back)
        out_label = Label(text='stdout:', font=('sans', 12))

        for widget in (button_frame, frame, out_label, self.stdout):
            widget.pack(side=TOP, expand=1, fill=BOTH)
        
        self.source_text.pack(side=LEFT, expand=1, fill=BOTH)
        self.annotation_text.pack(side=LEFT, expand=1, fill=BOTH)

        for button in (play_button, pause_button, rewind_button, back_button, forward_button):
            button.pack(side=LEFT)
        
        name=raw_source.split('.')[0]
        with open(name+'.json', 'r') as f:
            raw_trace=json.load(f)
        self.trace=raw_trace['trace']
        
        #self.source.insert(1.0, raw_trace['source'])

        self.popup_menu=Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Fold/Unfold", command=self.folder)

        self.root.bind('<Button-3>', self.popup)

        for text in (self.annotation_text, self.source_text):
            text.bind('<Button-5>', lambda e, s=self: s.y_scroll(SCROLL, 1, UNITS))
            text.bind('<Up>', lambda e, s=self: s.y_scroll(SCROLL, -1, UNITS))
            text.bind('<Button-4>', lambda e, s=self: s.y_scroll(SCROLL, -1, UNITS))
            text.bind('<Down>', lambda e, s=self: s.y_scroll(SCROLL, 1, UNITS))
#            text.bind('<B1-Motion>', lambda e, s=self: s.select())
#            text.bind('<Button-1>', lambda e, s=self: s.select())

        self.source_text.bind('<Enter>', self.source_entry)
        self.annotation_text.bind('<Enter>', self.annotation_entry)

        self.source, self.annotations=self.parse_source()

        self.fold_length=40
        assert self.fold_length<self.width, "Folding width must be less than window width"
        self.stdout.config(state=DISABLED)

        self.current_line=0
        self.paused=False
        self.finished=False

        #in seconds
        self.step_rate=1
        self.folded_lines=self.fold_annotations()

        for lineno in self.source:
            self.source_text.insert(INSERT, self.source[lineno])
            self.annotation_text.insert(INSERT, self.folded_lines[self.annotations[lineno]])
            
            #to properly line up the annotations #if len(self.source[lineno]) > self.width: #    self.annotation_text.insert(INSERT, '\n')
            #This needs to do something, but not this

        self.current='source_text'

        self.root.mainloop()

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
        self.source_text.config(state=NORMAL)
        self.clear_highlighting()
        self.source_text.tag_add('highlight', '%s.0' % lineno, '%s.end' % lineno)
        self.source_text.tag_configure('highlight', background='yellow')
        self.source_text.see('highlight.first')
        self.source_text.config(state=DISABLED)

    def clear_highlighting(self):
        self.source_text.config(state=NORMAL)
        self.source_text.tag_remove('highlight', '1.0', 'end')
        self.source_text.config(state=DISABLED)

    def play(self):
        if not self.paused and not self.finished:
            self.step_forward()
            self.source_text.after(int(self.step_rate * 1000), self.play)

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
        self.source_text.see('1.0')

    def annotation_helper(self, text):
        '''Callback for the AnnotationEditor dialog box.  Deletes the current
        line and removes the reference to it in the folding dict if there is
        one. Then it creates the new folding dict entries out of the edited
        text and inserts them into the annotation text.'''

        #the +1c is to get the newline
        current_line=self.annotation_text.get('insert linestart', 'insert lineend+1c')
        current_lineno=int(float(self.annotation_text.index('insert linestart')))

        if current_line != '' and current_line != '\n':
            del self.folded_lines[current_line]
            del self.annotations[current_lineno]

        self.annotation_text.delete('insert linestart', 'insert lineend+1c')

        folded_line, unfolded_line = self.fold_line(text)

        self.folded_lines[unfolded_line]=folded_line
        self.folded_lines[folded_line]=unfolded_line

        self.annotation_text.insert('insert', folded_line)
        self.annotations[current_lineno]=text

        self.save()

    def fold_line(self, line):
        '''Takes a line and returns a tuple containing the folded and the
        unfolded version of the line.'''

        folded_line=line[:self.fold_length]

        if folded_line[-1:] != '\n':
            folded_line=folded_line[:-1]+'...\n'

        elif len(folded_line) != 1 and len(folded_line) >= self.fold_length:
            folded_line+='...\n'
        
        if line[-1:] != '\n':
            unfolded_line=line+'\n'
        else:
            unfolded_line=line
        
        return folded_line, unfolded_line
        
    def fold_annotations(self):
        '''Takes self.annotations and creates an dictionary mapping folded
        lines to unfolded lines and vice versa, where a folded line is a line
        truncated to the folding length with "..." appended to the end.'''

        folded_lines={}
        for line in self.annotations.values():

            folded_line, unfolded_line = self.fold_line(line)

            folded_lines[unfolded_line]=folded_line
            folded_lines[folded_line]=unfolded_line

        return folded_lines 

    def parse_source(self):
        '''This takes a source file with annotations in it and returns two
        ordered dictionaries: the first maps (int) line numbers to the source
        lines, the second maps line numbers to annotation lines. If there is no
        annotation for a line, it is mapped as 'lineno':'\n'. By changing this
        function, you can change the file format.'''

        source=OrderedDict()
        annotations=OrderedDict()
        in_annotations=False
        i=1

        for line in open(self.raw_source):
            if line == "'''ANNOTATIONS\n":
                in_annotations=True
            elif in_annotations:
                if line == "'''\n":
                    pass
                else:
                    parsed_anno=line.split(':')
                    annotations[int(parsed_anno[0])]=parsed_anno[1]
            else:
                source[i]=line
                i += 1

        for lineno in source:
            if lineno not in annotations:
               annotations[lineno]='\n'

        return source, annotations

#BUG this doesn't adjust the source text properly when annotations are multiple lines
    def folder(self, event=None):
        '''Replaces the current line with the contents of the folding dict if
        there is an entry for it; otherwise, it does nothing.'''
        
        if self.current == 'annotation_text' :
            #the +1c is to get the newline
            current_line=self.annotation_text.get('current linestart', 'current lineend+1c')
            self.annotation_text.delete('current linestart', 'current lineend+1c')

            try:
                self.annotation_text.insert('current', self.folded_lines[current_line])
            except KeyError:
                folded_line, unfolded_line= self.fold_line(current_line)
                self.folded_lines[folded_line] = unfolded_line
                self.folded_lines[unfolded_line] = folded_line
                self.annotation_text.insert('current', self.folded_lines[current_line])
        self.save()

    def save(self):
        '''This takes the contents of the source pane and writes them to file,
        followed by the annoations from the annotation pane (enclosed in an
        special block comment.'''
 
        #source saving
        f=open(self.raw_source, 'w') 
 
        source=self.source_text.get('1.0', END)
         
        for line in source.split('\n'):
            print(line, file=f)
            
        #annotation saving
        print("'''ANNOTATIONS", file=f)

        i=1
        annotations=self.annotation_text.get('1.0', END)
        for line in annotations.split('\n'): 
            if line:
                if line[-3:] == '...':
                    print("%d:%s" % (i, self.folded_lines[line+'\n']), end='', file=f)
                else:
                    print("%d:%s" % (i, line+'\n'), end='', file=f)
            i+=1

        print("'''", file=f)
        f.close()

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
           self.popup_menu.grab_release()

    def y_scroll(self, *args):
        self.annotation_text.yview(*args)
        self.source_text.yview(*args)
        return 'break'

    def source_entry(self, event):
        self.current='source_text'

    def annotation_entry(self, event):
        self.current='annotation_text'
    
    def select(self):
#BROKEN
        if self.current == 'annotation_text':
            row = int(float(self.annotation_text.index('current')))
        else:
            row = int(float(self.source_text.index('current')))
        self.source_text.tag_add('sel', '%d.0' % row, '%d.end' % row)
        self.annotation_text.tag_add('sel', '%d.0' % row, '%d.end' % row)
        return 'break'
        
if __name__=='__main__':
    FoldManager('hello.py')
