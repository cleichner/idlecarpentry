from Tkinter import *

class Hack:
    def __init__(self):
        self.root=Tk()

        self.text=Text(self.root)
        self.text.pack()

        self.button_frame=Frame(self.root)
        self.button_frame.pack()

        self.hack_button=Button(self.button_frame, text='Hack.', command=self.hack)
        self.hack_button.pack(side=LEFT)

        self.number=0
        self.button_displayed=False

        self.fix_button=Button(self.button_frame, text="It's okay, I found a new bank.", command=self.fix)

        self.root.mainloop()

    def hack(self):
        if self.number < 5:
            self.text.insert(INSERT, 'Transferring the money from the bank.\n')
            self.number+=1
        if self.number >= 5:
            self.text.insert(INSERT, "The money is all gone. Find a new bank. Serious, you're an asshole.\n")
            if not self.button_displayed:
                self.fix_button.pack(side=LEFT)
                self.button_displayed=True

    def fix(self):
        self.number=0
        self.text.insert(INSERT, "Okay, it's cool.\n")
        self.fix_button.pack_forget()
        self.button_displayed=False

Hack()
