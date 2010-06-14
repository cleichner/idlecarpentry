from Tkinter import *
import tkMessageBox
from PyShell import PyShellEditorWindow, PyShellFileList
from EditorWindow import fixwordbreaks
from MultiCall import MultiCallCreator

DEBUG = True

class SplitTextFrame(Frame):
    '''This contains two Text widgets, split by an identifier tag. It mimics
    the methods of the Text widget which EditorWindow and its subclasses use in
    for self.text ''' 

    def __init__(self, master=None, **options)
        self.source_text = MultiCallCreator(Text)(text_frame, **text_options)
        self.annotation_text = MultiCallCreator(Text)(text_frame, **text_options)

    def index(self, index)
    '''Returns the line.column index corresponding to the given index.
       index - index specifier (this can be a mark)
       return the corresponding row/column, given as a 'line.column' string.'''
        pass

    def bell(self):
    '''It's just a beep.'''
        if DEBUG is True:
            print 'beep'
        self.source_text.bell()

    def delete(self):
    '''Deletes the character (or embedded object) at the given position, or all
    text in the given range. Any marks within the range are moved to the
    beginning of the range.'''
        pass

    def insert(self, index, text, *tags):
    '''Inserts text at the given position. The index is typically INSERT or
    END. If you provide one or more tags, they are attached to the new text.
    If you insert text on a mark, the mark is moved according to its gravity setting.
    '''
        pass

    def get(self, start, end=None):
    '''Returns the character at the given position, or all text in the given
    range.

    start - start position
    end - end position. If omitted, only one character is returned.
    '''
        pass

    def after(self, delay_ms, callback, *args):
    '''Register an alarm callback that is called after the given number of
    milliseconds.'''
        pass

    def after_cancel(self, id):
    '''Cancels the given alarm callback.'''
        pass

    def after_idle(self, callback, *args):
    '''Register an idle callback which is called when the system is idle. (When
    there are no more events to process after the main loop)'''
        pass

    def compare(self, index1, op, index2):
    '''Compares two indexes. The op argument is one of '<', '<=', '==', '>=',
    '>', '!='''
        pass

    def tag_add(self, tag, start, stop=None):
    '''add tag to the character at the given position, or to the given
    range.'''
        pass

    def tag_remove(self, tag, start, stop=None):
    '''If stop is None, remove the tag from the character at the start
    position, otherwise it acts on the given range. The information
    associated with the tag is not removed.''' 
        pass

    def tag_ranges(self, tag):
    '''Returns a tuple with the start- and stop-indexes for each
    occurrence of the given tag. If the tag doesn't exist, this method
    returns an empty tuple. Note that the tuple contains two items for
    each range.''' 
        pass

    def tag_nextrange(self, tag, start, stop=None):
    '''Find the next occurrence of the given tag, from start to stop, or to the
    end if stop is None. '''
        pass

    def tag_prevrange(self, tag, start, stop=None):
    '''Find the next occurrence of the given tag, starting at the given index
    and searching towards the beginning of the text if stop is None.'''
        pass

    def tag_names(self, index=None):
    '''If index is None, Return a tuple containing all tags used in the widget.
    This includes the SEL selection tag. Otherwise, it returns a tuple
    containing all tags used by the character at the given position.'''
        pass

    def tag_bind(self, sequence, func, string=None):
    '''Add an event binding to the given tag, if string is '+'. Tag bindings
    can use mouse- and keyboard-related events, plus <Enter> and <Leave>. If
    the tag doesn't exist, it is created. Usually, the new binding replaces any
    existing binding for the same event sequence. The second form can be used
    to add the new callback to the existing binding. '''
        pass

    def mark_set(self, mark, index):
    '''Move the mark to the given position. If the mark doesn't exist, it is
    created.  This method can also be used to move the predefined INSERT and
    CURRENT MARKS'''
        pass

    def mark_gravity(self, mark, gravity=None):
    '''Return the current gravity setting for the given mark (LEFT of RIGHT) or
    sets the gravity (how to move the mark if text is inserted exactly on the
    mark) for the mark if gravity is not None'''
        pass

    def see(self, index):
    '''Scroll the text, if necessary, to make sure the text at the given
    position is visible.'''
        pass

    def bind(self, triplet, func, string=None):
    '''If string is '+', this binds func to self in response to triplet.'''
        pass

    def unbind(self, triplet, func):
    '''Remove the binding from self.'''
        pass

    def event_add(self, virtual, *sequences):
    '''Adds a virtual event any number of sequences, describing physical
    events.'''
        pass

    def event_generate(self, sequence, **keywords):
    ''' This method causes an event to trigger without any external stimulus.
    The handling of the event is the same as if it had been triggered by an
    external stimulus. The sequence argument describes the event to be
    triggered. You can set values for selected fields in the Event object by
    providing keyword=value arguments, where the keyword specifies the name of
    a field in the Event  object. '''
        pass

    def event_delete(self, virtual, *sequences):
    '''Deletes physical events from the virtual event whose name is given by
    the string virtual. If all the physical events are removed from a given
    virtual event, that virtual event won't happen anymore. '''
        pass

    def config(self, **options):
    '''Modifies one or more widget options. If no options are give, the method
    returns a dictionary containing all current option values.'''
        pass

    def focus_set(self):
    '''Move keyboard focus to self.'''
        pass

    def pack(self, *kw_options):
    '''Pack the widgets as described by the options'''
        pass

    def update(self):
    '''Process all pending events, call event callbacks, complete any pending
    geometry management, redraw widgets as necessary, and call all pending idle
    tasks.'''
        pass
    
    def update_idletasks(self):
    '''Call all pending idle tasks, without processing any other events.''' 
        pass

    def undo_block_start(self): 
    '''Start of an undo block, from UndoDelagator. If these are nested the
    inner commands will act like nops.'''
    #Look into how these will interact across the annotations and source
        pass

    def undo_block_stop(self):
    '''Stop of an undo block, from UndoDelagator. If these are nested the
    inner commands will act like nops.''' 
        pass

class PySplitShellEditorWindow(PyShellEditorWindow):
    "Split IDLE text edit window"
    text=None
    pass 

class PySplitShellFileList(PyShellFileList):
    "Opens files and deals with partitioning the annotations and the source"
    EditorWindow = PySplitShellEditorWindow
    pass

def test():
    root = Tk(className="Idle")

    fixwordbreaks(root)
    root.withdraw()

    flist = PySplitShellFileList(root)

    flist.open('test')

    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    test()
