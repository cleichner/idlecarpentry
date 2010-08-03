from Tkinter import *

top = Tk()

play_button = Button(top, text = 'Play')
play_button.grid(row = 0, column = 0, sticky = EW)

rewind_button = Button(top, text = 'Rewind')
rewind_button.grid(row = 0, column = 1, sticky = EW)

forward_button = Button(top, text = 'Step Forward')
forward_button.grid(row = 0, column = 2, sticky = EW)

back_button = Button(top, text = 'Step Back')
back_button.grid(row = 0, column = 3, sticky = EW)


source_label = Label(top, text = 'source:')
source_label.grid(row = 1, column = 0, columnspan = 4, sticky = NSEW)

source = Text(top, height = 21)
source.grid(row = 2, column = 0, rowspan = 6, columnspan = 4, sticky = NSEW)
source.insert(INSERT, 'source')

source_scroll = Scrollbar(top, command = source.yview )
source_scroll.grid(row = 2, column = 4, rowspan = 5, sticky = NSEW)
source.config(yscrollcommand = source_scroll.set)


anno_label = Label(top, text = 'explanation:')
anno_label.grid(row = 1, column = 5, sticky = NSEW)

annotations = Text(top, height = 7)
annotations.grid(row = 2, column = 5, sticky = NSEW)
annotations.insert(INSERT, 'annotations')

annotations_scroll = Scrollbar(top, command = annotations.yview )
annotations_scroll.grid(row = 2, column = 6, sticky = NSEW)
annotations.config(yscrollcommand = annotations_scroll.set)


locals_label = Label(top, text = 'locals:')
locals_label.grid(row = 3, column = 5, sticky = NSEW)

locals = Text(top, height = 7)
locals.grid(row = 4, column = 5, sticky = NSEW)
locals.insert(INSERT, 'locals')

locals_scroll = Scrollbar(top, command = locals.yview )
locals_scroll.grid(row = 4, column = 6, sticky = NSEW)
locals.config(yscrollcommand = locals_scroll.set)


globals_label = Label(top, text = 'globals:')
globals_label.grid(row = 5, column = 5, sticky = NSEW)

globals = Text(top, height = 7)
globals.grid(row = 6, column = 5, sticky = NSEW)
globals.insert(INSERT, 'globals')

globals_scroll = Scrollbar(top, command = globals.yview )
globals_scroll.grid(row = 6, column = 6,  sticky = NSEW)
globals.config(yscrollcommand = globals_scroll.set)


stdout_label = Label(top, text = 'stdout:')
stdout_label.grid(row = 7, column = 0, columnspan = 6, sticky = NSEW)

stdout = Text(top, height = 7)
stdout.grid(row = 8, column = 0, columnspan = 6, sticky = NSEW)
stdout.insert(INSERT, 'stdout')

stdout_scroll = Scrollbar(top, command = stdout.yview )
stdout_scroll.grid(row = 8, column = 6, sticky = NSEW)
stdout.config(yscrollcommand = stdout_scroll.set)


top.mainloop()
