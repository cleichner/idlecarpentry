from Tkinter import *
import tkMessageBox
from PyShell import PyShellEditorWindow, PyShellFileList
from EditorWindow import fixwordbreaks
from MultiCall import MultiCallCreator

DEBUG = True

#one of these classes needs to take care of folding through virtual event bindings
#once folding works, all of these need to reference line numbers and index off
#of the source_text
        for line in 

class SplitText(object):
#need to handle one INSERT
#make this work with dictionary access meaning .config

    '''This contains two Text widgets, split by an identifier tag. It mimics
    the methods of the Text widget which EditorWindow and its subclasses use in
    for self.text ''' 

    def __init__(self, master=None, **text_options):
        self.current='source_text'

        self.source_text = MultiCallCreator(Text)(master, **text_options)
        self.annotation_text = MultiCallCreator(Text)(master, **text_options)

        master.tk_focusFollowsMouse()

        self.source_text.bind('<FocusIn>', self.source_entry)
#OR     self.source_text.bind('<Enter>', source_entry)
        
        self.annotation_text.bind('<FocusIn>', self.annotation_entry)
#OR     self.annotation_text.bind('<Enter>', annotation_entry)
#I don't know which one works better at this point

        self.annotation_text.config(state=DISABLED)
        
    def get_line(self, index):
        line_column=self.index(index)
        line=line_column.split('.')[0]
        return line
    
    def source_entry(self, event):
        self.current='source_text'

    def annotation_entry(self, event):
        self.current='annotation_text'

    def annotate(self):

    def index(self, index):
        '''Returns the line.column index corresponding to the given index.
        index - index specifier (this can be a mark)
        return the corresponding row/column, given as a 'line.column' string.'''

#source line numbers control all line numbers
#annotation lines numbers match the source lines they are annotating (WAIT 'TIL folding works to implement this)

        if self.current == 'source_text':
            return self.source_text.index(index)
        else:
            return self.annotation_text.index(index)

    def bell(self):
        '''It's just a beep.'''
        if DEBUG is True:
            print 'beep'
        self.source_text.bell()

    def delete(self, start, stop=None):
        '''Deletes the character (or embedded object) at the given position, or all
        text in the given range. Any marks within the range are moved to the
        beginning of the range.'''

        if self.current == 'source_text':
            self.source_text.delete(start, stop)
        else:
            self.annotation_text.delete(start, stop)

    def insert(self, index, text, *tags):
        '''Inserts text at the given position. The index is typically INSERT or
        END. If you provide one or more tags, they are attached to the new text.
        If you insert text on a mark, the mark is moved according to its gravity setting.
        '''

        if self.current == 'source_text':
            self.source_text.insert(index, text, *tags)
        else:
            self.annotation_text.insert(index, text, *tags)

    def get(self, start, stop=None):
        '''Returns the character at the given position, or all text in the given
        range.

        start - start position
        end - end position. If omitted, only one character is returned.
        '''

        if self.current == 'source_text':
            return self.source_text.get(start, stop)
        else:
            return self.annotation_text.get(start, stop)

    def after(self, delay_ms, callback, *args):
        '''Register an alarm callback that is called after the given number of
        else:
            return self.annotation_text.get(start, stop)

    def after(self, delay_ms, callback, *args):
        '''Register an alarm callback that is called after the given number of
        milliseconds.'''

        return self.source_text.after(delay_ms, callback, *args)

    def after_cancel(self, id):
        '''Cancels the given alarm callback.'''

        self.source_text.after_cancel(id)

    def after_idle(self, callback, *args):
        '''Register an idle callback which is called when the system is idle. (When
        there are no more events to process after the main loop)'''

        self.source_text.after_idle(callback, *args)

    def compare(self, index1, op, index2):
        '''Compares two indexes. The op argument is one of '<', '<=', '==', '>=',
        '>', '!='''

        if self.current == 'source_text':
            self.source_text.compare(index1, op, index2)
        else:
            self.annotation_text.compare(index1, op, index2)


    def tag_add(self, tag, start, stop=None):
        '''add tag to the character at the given position, or to the given
        range.'''

        if self.current == 'source_text':
            self.source_text.tag_add(tag, start, stop)
        else:
            self.annotation_text.tag_add(tag, start, stop)

    def tag_remove(self, tag, start, stop=None):
        '''If stop is None, remove the tag from the character at the start
        position, otherwise it acts on the given range. The information
        associated with the tag is not removed.''' 

        if self.current == 'source_text':
            self.source_text.tag_remove(tag, start, stop)
        else:
            self.annotation_text.tag_remove(tag, start, stop)

    def tag_ranges(self, tag):
        '''Returns a tuple with the start- and stop-indexes for each
        occurrence of the given tag. If the tag doesn't exist, this method
        returns an empty tuple. Note that the tuple contains two items for
        each range.''' 

        if self.current == 'source_text':
            return self.source_text.tag_ranges(tag)
        else:
            return self.annotation_text.tag_ranges(tag)

    def tag_nextrange(self, tag, start, stop=None):
        '''Find the next occurrence of the given tag, from start to stop, or to the
        end if stop is None. '''

        if self.current == 'source_text':
            return self.source_text.tag_nextrange(tag, start, stop)
        else:
            return self.annotation_text.tag_nextrange(tag, start, stop)

    def tag_prevrange(self, tag, start, stop=None):
        '''Find the next occurrence of the given tag, starting at the given index
        and searching towards the beginning of the text if stop is None.'''

        if self.current == 'source_text':
            return self.source_text.tag_prevrange(tag, start, stop)
        else:
            return self.annotation_text.tag_prevrange(tag, start, stop)

    def tag_names(self, index=None):
        '''If index is None, Return a tuple containing all tags used in the widget.
        This includes the SEL selection tag. Otherwise, it returns a tuple
        containing all tags used by the character at the given position.'''

        if self.current == 'source_text':
            return self.source_text.tag_names(index)
        else:
            return self.annotation_text.tag_names(index)

    def tag_bind(self, sequence, func, string=None):
        '''Add an event binding to the given tag, if string is '+'. Tag bindings
        can use mouse- and keyboard-related events, plus <Enter> and <Leave>. If
        the tag doesn't exist, it is created. Usually, the new binding replaces any
        existing binding for the same event sequence. The second form can be used
        to add the new callback to the existing binding. '''

        if self.current == 'source_text':
            self.source_text.tag_bind(sequence, func, string)
        else:
            self.annotation_text.tag_bind(sequence, func, string)

    def mark_set(self, mark, index):
        '''Move the mark to the given position. If the mark doesn't exist, it is
        created.  This method can also be used to move the predefined INSERT and
        CURRENT MARKS'''
#This one needs to be modified to act like there is one mark which is split across both text boxes, maybe

        if self.current == 'source_text':
            self.source_text.mark_set(mark, index)
        else:
            self.annotation_text.mark_set(mark, index)

    def mark_gravity(self, mark, gravity=None):
        '''Return the current gravity setting for the given mark (LEFT of RIGHT) or
        sets the gravity (how to move the mark if text is inserted exactly on the
        mark) for the mark if gravity is not None'''

        if self.current == 'source_text':
            return self.source_text.mark_gravity(mark, gravity)
        else:
            return self.annotation_text.mark_gravity(mark, gravity)

    def see(self, index):
        '''Scroll the text, if necessary, to make sure the text at the given
        position is visible.'''

#needs to by sychronized across the two pieces of text, should work better once folding is working
        if self.current == 'source_text':
            self.source_text.see(index)
        else:
            self.annotation_text.see(index)

    def bind(self, triplet, func, string=None):
        '''If string is '+', this binds func to self in response to triplet.'''

        self.source_text.bind(triplet, func, string)
        self.annotation_text.bind(triplet, func, string)

    def unbind(self, triplet, func):
        '''Remove the event binding from self.'''

        self.source_text.unbind(triplet, func)
        self.annotation_text.unbind(triplet, func)

    def event_add(self, virtual, *sequences):
        '''Binds virtual events to physical ones.'''

        self.source_text.event_add(virtual, *sequences)
        self.annotation_text.event_add(virtual, *sequences)

    def event_generate(self, sequence, **keywords):
        ''' This method causes an event to trigger without any external stimulus.
        The handling of the event is the same as if it had been triggered by an
        external stimulus. The sequence argument describes the event to be
        triggered. You can set values for selected fields in the Event object by
        providing keyword=value arguments, where the keyword specifies the name of
        a field in the Event  object. '''

        self.source_text.event_generate(sequence, **keywords)
        self.annotation_text.event_generate(sequence, **keywords)

    def event_delete(self, virtual, *sequences):
        '''Deletes physical events from the virtual event whose name is given by
        the string virtual. If all the physical events are removed from a given
        virtual event, that virtual event won't happen anymore. '''

        self.source_text.event_add(virtual, *sequences)
        self.annotation_text.event_add(virtual, *sequences)

    def config(self, **options):
        '''Modifies one or more widget options. If no options are given, the method
        returns a dictionary containing all current option values.'''
#I might need to implement a frame around the current widget to make this one work

        self.source_text.config(**options)
        self.annotation_text.config(**options)

    def focus_set(self):
        '''Move keyboard focus to self.'''

        self.source_text.focus_set()

    def pack(self, *kw_options):
        '''Pack the widgets as described by the options'''

        self.source_text.pack(side=LEFT)
        self.annotation_text.pack(side=LEFT)

    def update(self):
        '''Process all pending events, call event callbacks, complete any pending
        geometry management, redraw widgets as necessary, and call all pending idle
        tasks.'''

        self.source_text.update()
        self.annotation_text.update()

    def update_idletasks(self):
        '''Call all pending idle tasks, without processing any other events.''' 

        self.source_text.update_idletasks()
        self.annotation_text.update_idletasks()

#These shouldn't need to be implemented for this to work
    def undo_block_start(self): 
        '''Start of an undo block, from UndoDelagator. If these are nested the
        inner commands will act like nops.'''
#Look into how these will interact across the annotations and source
#ANSWER: undo_block_start for each source and annotations, don't nest them.
        pass

    def undo_block_stop(self):
        '''Stop of an undo block, from UndoDelagator. If these are nested the
        inner commands will act like nops.''' 
        pass

class PySplitShellEditorWindow(PyShellEditorWindow):
    "Split IDLE text edit window"
    def __init__(self, *args):
        super(PySplitShellEditorWindow, self).__init__(*args)
        self.text=text=SplitText(self.text_frame, **self.text_options)

class PySplitShellFileList(PyShellFileList):
    "Opens files and deals with partitioning the annotations and the source"
    EditorWindow = PySplitShellEditorWindow
    pass

def test():
    root = Tk(className="Idle")

    fixwordbreaks(root)
    root.withdraw()

    flist = PySplitShellFileList(root)

    flist.new()

