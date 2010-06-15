'''
This uses every method used by IDLE. If the new Text widget works here, it
works in IDLE.  
'''

from Tkinter import *
import PySplitShell
from UndoDelegator import UndoDelegator

root=Tk()

text=Text(root)
undo=UndoDelegator()
text.undo_block_start=undo.undo_block_start
text.undo_block_stop=undo.undo_block_stop
#text=PySplitShell.SplitTextFrame(root)


text.pack()

text.config(state=DISABLED)
text.config(state=NORMAL, height=30)
text.focus_set()

text.insert(INSERT, 'Hello, World!\n')
text.insert(INSERT, 'Hello, World!\n')
text.insert(INSERT, 'Hello, World!\n')
text.insert(INSERT, 'Hello, World!\n')
text.insert(INSERT, 'Hello, World!\n')
text.insert(INSERT, 'Hello, World!\n')
text.insert(2.3, 'this works', 'tags')

print text.index(INSERT) 

text.bell()

text.delete(2.3, 4.2)

text.tag_add('sel', 1.0, 2.0)
text.delete(SEL_FIRST, SEL_LAST)

print text.get(1.0, END)

def callback():
    print 'alarms work'

text.after(500, callback)
x=text.after(500, callback)

text.after_cancel(x)

text.after_idle(callback)

if text.compare(0.0, '<=', END):
    print 'basic less than or equals works'

text.tag_add('to remove', 2.2, END)

ranges_1 = text.tag_ranges('to remove')

text.tag_remove('to remove', 1.0, END)

ranges_2 = text.tag_ranges('to remove')

print ranges_1

if not ranges_2:
    print 'remove works'

text.tag_add('to remove', 2.2, END)

text.mark_set(INSERT, 1.0)
print 'next range', text.tag_nextrange('to remove', INSERT)

text.mark_set(INSERT, END)
print 'prev range', text.tag_prevrange('to remove', INSERT)

text.tag_add('to remove', 1.1)
text.tag_add('asdf', 2.2, END)
text.tag_add('something', 2.2, END)

tags=text.tag_names()
if 'to remove' and 'asdf' and 'something' in tags:
    print 'tag_names works'
else:
    print "tag_names doesn't work"


text.mark_set(INSERT, 1.0)
text.mark_set('mine', INSERT)
text.mark_set(INSERT, END)
text.insert('mine', 'If this is on the first line, mark_set works.')

print text.mark_gravity('mine'), 'If this was "right", mark_gravity half works'

text.insert(INSERT, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nstart')
text.see(END)
text.see(1.0)

def callback(event):
    print 'events work, see:', event

text.bind('<<virtual>>', callback)
text.event_generate('<<virtual>>')

text.unbind('<<virtual>>')
text.event_generate('<<virtual>>')
print 'the events callback should only be printed once before this'

text.bind('<<virtual>>', callback)
text.event_add('<<virtual>>', '<Key>') #Test these guys seperate
text.event_delete('<<virtual>>', '<Key>')

text.update()
text.update_idletasks()

text.undo_block_start()
text.undo_block_stop() 

root.mainloop()
