from __future__ import print_function
from Tkinter import *
from OrderedDict import OrderedDict

#ISSUES
#deal with expanding the source code when the annotations are unfolded
#source lines longer than the width of the program mess up the spacing

class AnnotationEditor(Toplevel):
    def __init__(self, master, current_text, annotation_callback):
        '''NEEDS DOCUMENTATION'''
        Toplevel.__init__(self, master)
        self.transient(master)

        #this should take a string as its argument
        self.annotation_callback=annotation_callback

        self.title('Edit')

        self.master = master

        Label(self, text="Insert Your Annotation").pack()

        self.annotation = Entry(self)
        
        self.annotation.insert(INSERT, current_text)
        self.annotation.pack(padx=5)

        done_button = Button(self, text="Done", command=self.done)
        done_button.pack(pady=5)

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.done)

        self.annotation.focus_set()

        self.wait_window(self)

    def done(self):
        self.annotation_callback(self.annotation.get())
        self.destroy()
       
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
        frame.pack(side=TOP, fill=BOTH, expand=1)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.width=80
        self.source_text=Text(frame, wrap=NONE, width=self.width)
        self.annotation_text=Text(frame, wrap=NONE, yscrollcommand=scrollbar.set, width=self.width)

        scrollbar.config(command=self.scroll)

        self.source_text.pack(side=LEFT, fill=BOTH, expand=1)
        self.annotation_text.pack(side=LEFT, fill=BOTH, expand=1)

        self.popup_menu=Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Edit Annotations", command=self.annotate)
        self.popup_menu.add_command(label="Fold/Unfold", command=self.folder)

        self.root.bind('<Button-3>', self.popup)

        for text in (self.annotation_text, self.source_text):
            text.bind('<Button-5>', lambda e, s=self: s.scroll(SCROLL, 1, UNITS))
            text.bind('<Up>', lambda e, s=self: s.scroll(SCROLL, -1, UNITS))
            text.bind('<Button-4>', lambda e, s=self: s.scroll(SCROLL, -1, UNITS))
            text.bind('<Down>', lambda e, s=self: s.scroll(SCROLL, 1, UNITS))
#           text.bind('<B1-Motion>', lambda e, s=self: s.select(e.y))
#           text.bind('<Button-1>', lambda e, s=self: s.select(e.y))

        self.source_text.bind('<Enter>', self.source_entry)
        self.annotation_text.bind('<Enter>', self.annotation_entry)

        self.source, self.annotations=self.parse_source()

        self.fold_length=40
        assert self.fold_length<self.width, "Folding width must be less than window width"
        self.folded_lines=self.fold_annotations()

        for lineno in self.source:
            self.source_text.insert(INSERT, self.source[lineno])
            self.annotation_text.insert(INSERT, self.folded_lines[self.annotations[lineno]])
            
            #to properly line up the annotations #if len(self.source[lineno]) > self.width: #    self.annotation_text.insert(INSERT, '\n')
            #This needs to do something, but not this

        self.current='source_text'
        self.annotation_text.config(state=DISABLED)

        self.root.mainloop()


    def annotate(self):
        '''NEEDS DOCUMENTATION'''
        if self.current == 'source_text':
            self.annotation_text.config(state=NORMAL)

            source_index=self.source_text.index('current')
            self.annotation_text.mark_set(INSERT, source_index)
            self.annotation_text.focus_set()

            current_text=self.annotation_text.get('insert linestart', 'insert lineend+1c')

            if current_text == '\n':
                current_text=''

            if current_text in self.folded_lines and current_text[-4:] == '...\n':
                current_text=self.folded_lines[current_text]

            AnnotationEditor(self.root, current_text, self.annotation_helper)

            self.annotation_text.config(state=DISABLED)

    def annotation_helper(self, text):
        '''Calback for the AnnotationEditor dialog box.  Deletes the current
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
    def folder(self):
        '''Replaces the current line with the contents of the folding dict if
        there is an entry for it; otherwise, it does nothing.'''
        
        self.annotation_text.config(state=NORMAL)
        if self.current == 'annotation_text' :
            #the +1c is to get the newline
            current_line=self.annotation_text.get('current linestart', 'current lineend+1c')
            self.annotation_text.delete('current linestart', 'current lineend+1c')

            try:
                self.annotation_text.insert('current', self.folded_lines[current_line])
            except KeyError:
                self.annotation_text.insert('current', current_line) 

        self.annotation_text.config(state=DISABLED)

    def save(self):
       '''NEEDS DOCUMENTATION'''
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
               print("%d:%s" % (i, self.folded_lines[line+'\n']), end='', file=f)
               print("%d:%s" % (i, self.folded_lines[line+'\n']), end='')
           i+=1

       print("'''", file=f)

#potential trace saving
       f.close()

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
           self.popup_menu.grab_release()

    def scroll(self, *args):
        self.annotation_text.yview(*args)
        self.source_text.yview(*args)
        return 'break'

    def source_entry(self, event):
        self.current='source_text'

    def annotation_entry(self, event):
        self.current='annotation_text'
    
#   def select(self, y):
#BROKEN FOR TEXT
#should use current instead of nearest
#       row = self.lists[0].nearest(y)
#       self.selection_clear(0, END)
#       self.selection_set(row)
#       return 'break'
        
if __name__=='__main__':
    FoldManager('example_annotated_code.py')
