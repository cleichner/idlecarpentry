from Tkinter import *

#config variables
raw_source='example_annotated_code.py'
fold_length=77

def parse_source(raw_source):

    source={}
    annotations={}
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
            source[str(i)]=line #I love you so much
            i += 1
    return source, annotations
 
source={}
annotations={}
source, annotations = parse_source(raw_source)

#make annotation dict
annotation_dict={}
#import pdb; pdb.set_trace()
#debuggers are useful, I confused ints and strings
for line in source:
    if line in annotations:
       #This branch never executes
        annotation_dict[line]=annotations[line]
    else:
        annotation_dict[line]='\n'

#GUI definitions
root=Tk()

frame=Frame(root)
frame.pack()

source_text=Text(frame)
annotation_text=Text(frame)

source_text.pack(side=LEFT)
annotation_text.pack(side=LEFT)

for line in source:
    source_text.insert(INSERT, source[line])
    if line in annotation_dict:
        annotation_text.insert(INSERT, annotation_dict[line])
    else:
        annotation_text.insert(INSERT, '\n')
        
root.mainloop()
