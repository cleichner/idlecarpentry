#!/usr/bin/env python
#TODO
#fix multiple insertions in the trace
#have variable values be referenced
#show globals and locals

"""
This module traces the execution of a python script or function. The
output is meant to be played back later.

To trace a python script, either run this program from the command line

   ./trace.py -f trace_me.py

or run trace programatically like this

   import trace
   runner = trace.Tracer("trace_me.py")
   result, events = runner.trace()
   trace = trace.process_events_json(events)

You can also trace a particular function call instead of an entire python file

   import trace

   def foo()
      pass

   runner = trace.Tracer(foo)
   result, events = runner.trace()
   trace = trace.process_events_json(events)

"""
'''
It's JSON and there's a string of the entire source and an array of maps, one
for each step in the execution. The most important thing in each map is a line
number. Some maps also have a "stdout" or a "stderr" string of the captured
output at that step.

There's no way to currently annotate the recordings. I'd like to
modify the tracer to pull annotations from specially formatted
comments which annotate the next line, and then strip those comments
from the source string in the recording. Any suggestions for what
those comments should look like? To be useful for annotating the first
line in a loop, ie. "for item in all_items:", i think the special
comments should at least be able to specify whether the annotation
appears every time the line is executed or only the first time.
'''

import sys, os, optparse, time, json, pprint

import inspect
import token, tokenize

out=sys.stderr
def dprint(*args):
    for arg in args:
        print >>out, arg, 

def logevent(frame, event, arg):
    lines, lineno = inspect.findsource(frame.f_code)
    print >>sys.__stderr__, 'EVENT:', event, frame.f_lineno, lines[frame.f_lineno-1].strip()

class Logger(object):
    """Proxies stdout or stderr to capture the output of traced
    code."""
    def __init__(self, type, log):
        self.type = type
        self.log = log
        self.buffer = []

    def write(self, msg):
        self.buffer.append(msg)

    def flushLog(self):
        """Add any recorded output to the latest event."""
        if self.log and self.buffer:
            self.log[-1][self.type] = self.buffer
            self.buffer = []

class FrameHandler(object):
    """Handles events generated in a particular execution frame."""
    def __init__(self, tracer, frame, depth):
        self.tracer = tracer
        self.depth = depth
        
        # log initial call event
        record = tracer.log_event('call', frame, None, depth)
        self.locals = dict(frame.f_locals)
        record['d'] = self.locals
        record['g'] = dict(frame.f_globals)

    def on_event(self, frame, event, arg):
        """Trace function"""
        logevent(frame, event, arg)

        if event == 'return':
            self.tracer.current_depth -= 1

        record = self.tracer.log_event(event, frame, arg, self.depth)
        
        newlocals = dict(frame.f_locals)
        self.locals = newlocals
        record['d'] = newlocals
        record['g'] = dict(frame.f_globals)
        return self.on_event


class Tracer(object):
    def __init__(self, runme):

        # code objects that should not be traced into
        self.avoid_codes = set()
        # code objects that should be traced into but whose events will be ignored
        self.silent_codes = set()
        
        self.leaf_codes = set()

        self.avoid_codes.add(Logger.write.im_func.func_code)

        if isinstance(runme, str):
            # runme is a python file to execute
            def go():
                execfile(runme, { '__name__' : '__main__' })
            self.runme = go
            self.silent_codes.add(go.func_code)
        elif hasattr(runme, '__call__'):
            self.runme = runme
        else:
            raise TypeError, 'Object to trace must be callable or be the name of a python file to execute.'


    def trace(self, *args, **keywords):
        """Execute and trace the runme object passed to the
        constructor. Returns a 2-tuple of the result and the recorded
        events."""
        self.suppress_tracing = False
        self.current_code = None
        
        oldout = sys.stdout
        olderr = sys.stderr

        self.log = []
        sys.stdout = Logger('stdout', self.log)
        sys.stderr = Logger('stderr', self.log)

        self.current_depth = 0
        sys.settrace(self.trace_fn)
        try:
            result = self.runme(*args, **keywords)
        finally:
            sys.settrace(None)
            sys.stdout = oldout
            sys.stderr = olderr

        return (result, self.log)

    def suppress_trace_fn(self, frame, event, arg):
        """A local trace function to wait until a function returns
        before reenabling tracing"""
        if event == 'return':
            self.suppress_tracing = False

    def trace_fn(self, frame, event, arg):
        """Trace function. Creates and returns the local trace function to be used for
        a new frame."""

        if self.suppress_tracing:
            return None

        if event != 'call':
            raise ValueError('Global event should only be "call" but is "' + event + '"')

        code = frame.f_code
        if code in self.avoid_codes or (self.current_code in self.leaf_codes):
            self.suppress_tracing = True
            return self.suppress_trace_fn

        if code in self.silent_codes:
            return None

        else:
            logevent(frame, event, arg)
            handler = FrameHandler(self, frame, self.current_depth)
            self.current_depth += 1
            return handler.on_event



    def log_event(self, event, frame, arg, depth):
        """Record a trace event"""
        # flush anything written to std streams executing
        # previous line
        sys.stdout.flushLog()
        sys.stderr.flushLog()

        frame_globals=dict(frame.f_globals)
        frame_locals=dict(frame.f_globals)

        #this module likes to display the contents of '__builtins__', this fixes that
        if '__builtins__' in frame_globals:
            frame_globals['__builtins__'] = "<module '__builtin__' (built-in)>"

        if '__builtins__' in frame_locals:
            frame_locals['__builtins__'] = "<module '__builtin__' (built-in)>"

        for var in frame_globals:
            if not isinstance(var, dict):
                frame_globals[var]=repr(frame_globals[var])

        for var in frame_locals:
            if not isinstance(var, dict):
                frame_locals[var]=repr(frame_locals[var])


        record = dict(
            event = event,
            code = frame.f_code,
            line = frame.f_lineno,
            depth = depth,
            locals = frame_globals,
            globals = frame_locals
            )

        if event == "exception":
            record['exception'] = {
                "type": arg[0].__name__,
                #"args": arg[1].args,
                "args": arg[1],
                }

        self.log.append(record)
        return record

class LinesIter(object):
    def __init__(self, lines):
        self.i = 0
        self.lines = lines
        self.len = len(lines)

    def __call__(self):
        i = self.i
        self.i += 1
        if i < self.len:
            return self.lines[i]
        else:
            return ''

def getblock(lines):
    """Extract the block of code at the top of the given list of lines."""

#    while 1:
#        try:
#            print lineiter().rstrip()
#        except StopIteration:
#            print 'final line'

    for toknum, tokval, start, end, line in tokenize.generate_tokens(LinesIter(lines)):
        #print toknum, start, end #, line 
        
        if toknum == token.INDENT:
            print 'INDENT', line.rstrip()
        elif toknum == token.DEDENT:
            print 'DEDENT', line.rstrip()
        else:
            pass


#    blockfinder = BlockFinder()
#    try:
#        tokenize.tokenize(iter(lines).next, blockfinder.tokeneater)
#    except (EndOfBlock, IndentationError):
#        pass
#    return lines[:blockfinder.last]

def print_events(events):
    codes = set()

    for evt in events:
        code = evt['code']
        #if code is not None and code not in codes:
        #    codes.add(evt['code'])
            #print 'first see', code, 'is mod', inspect.ismodule(inspect.getmodule(code)), 'is func', inspect.isfunction(code)

            #lines, start = inspect.findsource(code)
            
            #print 'start', start, code.co_firstlineno

            #getblock(lines)
            #print inspect.getblock(lines[start:])

        stdout = evt.get('stdout', None)
        stderr = evt.get('stderr', None)
        print evt['depth'], code.co_filename,code.co_name, str(evt['line']) + ':', evt['event'], \
            #evt.get('d').keys(), evt.get('g').keys(),

        if evt['event'] == 'exception':
            print evt['exception'],
        if stdout:
            print 'stdout:', stdout,
        if stderr:
            print 'stderr:', stderr,

            
        print ''

def extract_codes(events):
    # collect all code objects
    module_codes = set()
    other_codes = set()
    for evt in events:
        code = evt['code']
        if code.co_name == '<module>':
            module_codes.add(code)
        else:
            other_codes.add(code)

    # find all the source code necessary to build the full program text

    module_source = {}
    for code in module_codes:
        filename = inspect.getsourcefile(code)
        lines, _ = inspect.findsource(code)
        module_source[filename] = (code, lines, {})
        #print ''.join(lines)

    ext_func_source = {}
    for code in other_codes:
        filename = inspect.getsourcefile(code)
        if filename in module_source:
            # already including entire module source
            _, _, funcs = module_source[filename]

            _, lineno = inspect.findsource(code)
            funcs[code] = lineno
        else:
            ext_func_source[code] = inspect.getsourcelines(code)

    #print 'module_source', module_source
    #print 'ext_func_source', ext_func_source

    return module_source, ext_func_source

def assemble_source(events):
    module_source, ext_func_source = extract_codes(events)

    # assemble all source together
    all_lines = []
    # and keep track of an offset to adjust line numbers seen during
    # trace for each code object. These offsets translate between
    # trace line numbers and line numbers in the assembled program
    # source
    line_offsets = {}

    
    # start with external functions at the top, sorted by file and line number
    for code in sorted(ext_func_source.keys(), key=lambda c: (c.co_filename, c.co_firstlineno)):
        lines, lineno = ext_func_source[code]
        # -1 because trace line numbers start at 1
        line_offsets[code] = len(all_lines) - 1
        all_lines.extend(lines)
        # add new line between functions
        all_lines.append('\n')
        
    # go through module code objects. There should only be one, I
    # think. Try to handle multiple, although it might not make sense.
    for filename, val in module_source.iteritems():
        code, lines, sub_funcs = val
        offset = len(all_lines) - 1
        line_offsets[code] = offset
        all_lines.extend(lines)

        # set offsets for code contained within this module's source
        for subfn, lineno in sub_funcs.iteritems():
            line_offsets[subfn] = offset


    #remove whitespace lines from start and end
    first = 0
    while first < len(all_lines) and all_lines[first].isspace():
        first += 1

    last = len(all_lines) - 1
    while last >= 0 and all_lines[last].isspace():
        last -= 1

    all_lines = all_lines[first:last+1]
    # adjust offsets for removed lines
    if first:
        for code in line_offsets:
            line_offsets[code] -= first

    return all_lines, line_offsets


def process_events(events):
    """ Takes the events produced by Tracer.trace, grabs all the
    relevent python source and returns the trace in a format that's
    almost ready to be replayed """
    all_lines, line_offsets = assemble_source(events)

    result_events = []

    for evt in events:
        if evt['event'] not in ('line','return', 'call', 'globals', 'locals'):
            continue
        
        code = evt['code']
        r = dict(line=line_offsets[code] + evt['line'])

        if evt['event'] == 'exception':
            r['exception'] =  evt['exception']['type']
            
        for entry in ('stdout', 'stderr'):
            if entry in evt:
                r[entry] = ''.join(evt[entry])

        for entry in ('globals', 'locals'):
            if entry in evt:
                r[entry] = evt[entry]
            
        #take care of the call/return multiple trace entry problem here
        result_events.append(r)

    return dict(source=''.join(all_lines), trace=result_events)
    
def process_events_json(events):
    """ Like process_events, except this will convert the trace to a
    json string before returning it """
    trace=process_events(events)
    return json.dumps(trace, separators=(',',':'), indent=2)

def roo():
    return 2

def foo():
    x = 3
    x += 2
    roo()
    print 'splash',x

def main():
    #print 'ismod', inspect.ismodule(inspect)
    #print inspect.getsource(inspect)

    parser = optparse.OptionParser()
    parser.add_option('-f', '--filename', dest='filename', metavar='FILE',
                      help = 'Python file to run',
                      )
    options,args = parser.parse_args()

    if options.filename is None:
        parser.print_help()
        sys.exit(2)

    runner = Tracer(options.filename)
#    runner = Tracer(foo)
    result, events = runner.trace()
    print process_events_json(events)

if __name__ == '__main__':
    main()
