from Tkinter import *
from OrderedDict import OrderedDict

raw_source='example_annotated_code.py'

def parse_source(raw_source):
    '''This takes a source file with annotations in it and returns two ordered
    dictionaries: the first maps line numbers to the source lines, the second
    maps line numbers to annotation lines. By changing this function, you can
    change the file format.'''

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
    return source, annotations
 
source=OrderedDict()
annotations=OrderedDict()
source, annotations = parse_source(raw_source)

#make annotation dict
annotation_dict=OrderedDict()
for lineno in source:
    if lineno in annotations:
        annotation_dict[lineno]=annotations[lineno]
    else:
        annotation_dict[lineno]='\n'

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

for lineno in source:
    source_text.insert(INSERT, source[lineno])
    annotation_text.insert(INSERT, annotation_dict[lineno])
        
root.mainloop()
