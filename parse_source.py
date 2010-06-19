from Tkinter import *
from OrderedDict import OrderedDict

class AnnotationReader(object):
    def __init__(self, raw_source):
        self.source=OrderedDict()
        self.annotations=OrderedDict()

        self.source, self.annotations = self.parse_source(raw_source)

    def parse_source(self, raw_source):
        '''This takes a source file with annotations in it and returns two
        ordered dictionaries: the first maps line numbers to the source lines,
        the second maps line numbers to annotation lines. If there is no
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
                    annotations[parsed_anno[0]]=parsed_anno[1]
            else:
                source[str(i)]=line
                i += 1

        for lineno in source:
            if lineno not in annotations:
               annotations[lineno]='\n'

        return source, annotations

#GUI definitions
root=Tk()
root.wm_title("Annotation Parsing Demo")

frame=Frame(root)
frame.pack()

source_text=Text(frame)
annotation_text=Text(frame)

source_text.pack(side=LEFT)
annotation_text.pack(side=LEFT)

#import pdb; pdb.set_trace()
source_reader=AnnotationReader('example_annotated_code.py')

for lineno in source_reader.source:
    source_text.insert(INSERT, source_reader.source[lineno])
    annotation_text.insert(INSERT, source_reader.annotations[lineno])
        
root.mainloop()
