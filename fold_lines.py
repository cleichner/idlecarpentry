from Tkinter import *
from OrderedDict import OrderedDict
import re

class FoldManager(object):
    def __init__(self, raw_source):
        self.root=Tk()
        self.root.wm_title('Folding and Annotation Parsing Demo')

        self.frame=Frame(self.root)
        self.frame.pack(side=TOP, fill=BOTH, expand=1)

        self.source_text=Text(self.frame)
        self.annotation_text=Text(self.frame)

        self.source_text.config(width=80)
        self.annotation_text.config(width=80)

        self.source_text.pack(side=LEFT, fill=BOTH, expand=1)
        self.annotation_text.pack(side=LEFT, fill=BOTH, expand=1)

        self.source, self.annotations=self.parse_source(raw_source)

        self.fold_length=40
        self.folded_lines=OrderedDict()

        for line in self.annotations.values():
            folded_line=line[:self.fold_length]
            if folded_line[-1:] != '\n':
                folded_line+='\n'

            unfolded_line=line
            
            self.folded_lines[unfolded_line]=folded_line
            self.folded_lines[folded_line]=unfolded_line

        for lineno in self.source:
                self.source_text.insert(INSERT, self.source[lineno])
                self.annotation_text.insert(INSERT, self.folded_lines[self.annotations[lineno]])

        self.popup_menu=Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Fold/Unfold", command=self.folder)

        self.root.bind('<Button-3>', self.popup)

        self.root.mainloop()

    def parse_source(self, raw_source):
        '''This takes a source file with annotations in it and returns two
        ordered dictionaries: the first maps (int) line numbers to the source
        lines, the second maps line numbers to annotation lines. If there is no
        annotation for a line, it is mapped as 'lineno':'\n'. By changing this
        function, you can change the file format.'''

        source=OrderedDict()
        annotations=OrderedDict()
        in_annotations=False
        i=1

        for line in open(raw_source):
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

    def folder(self):
        #the +1c is to get the newline
        current=self.annotation_text.get('current linestart', 'current lineend+1c')
        self.annotation_text.delete('current linestart', 'current lineend+1c')
        try:
            self.annotation_text.insert('current', self.folded_lines[current])
        except KeyError:
            print current
            self.annotation_text.insert('current', current) 

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
           self.popup_menu.grab_release()

if __name__=='__main__':
    FoldManager('example_annotated_code.py')
