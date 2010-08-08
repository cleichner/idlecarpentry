#!/usr/bin/env python

"""
This module traces the execution of a python script. The output is meant to be
played back later.  Annotations can be added to the execution flow by making
comments starting with #>. They will be stripped out and associated with the
nearest program line after them in the trace. 

To trace a python script, either run this program from the command line

   ./trace.py -f trace_me.py

or run trace programatically like this

   import trace
   trace = trace.trace("trace_me.py")

"""

import sys
import optparse
import json
import inspect
import token
import tokenize
import tempfile

DEBUG = False

out=sys.stderr
def dprint(*args):
    if DEBUG:
        for arg in args:
            print >>out, arg, 

def logevent(frame, event, arg):
    if DEBUG:
        lines, lineno = inspect.findsource(frame.f_code)
        print >>sys.__stderr__, 'EVENT:', event, \
            frame.f_lineno, lines[frame.f_lineno-1].strip()

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
        tracer.log_event('call', frame, None, depth)

    def on_event(self, frame, event, arg):
        """Trace function"""
        logevent(frame, event, arg)

        if event == 'return':
            self.tracer.current_depth -= 1

        self.tracer.log_event(event, frame, arg, self.depth)
        
        return self.on_event

class Tracer(object):
    def __init__(self, runme):

        # code objects that should not be traced into
        self.avoid_codes = set()
        # code objects that should be traced into but whose events will be ignored
        self.silent_codes = set()
        
        self.leaf_codes = set()

        self.avoid_codes.add(Logger.write.im_func.func_code)

        self.filename = runme

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
            return

        if event != 'call':
            raise ValueError('Global event should only be "call" but is "' + event + '"')

        #ignore imported modules
        if frame.f_code.co_filename != self.filename:
            return 

        code = frame.f_code
        if code in self.avoid_codes or (self.current_code in self.leaf_codes):
            self.suppress_tracing = True
            return self.suppress_trace_fn

        if code in self.silent_codes:
            return

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
        frame_locals=dict(frame.f_locals)

        #this module likes to display the contents of '__builtins__', this fixes that
        for var in frame_globals:
            if var != '__builtins__':
                frame_globals[var]=repr(frame_globals[var])
            else:
                frame_globals[var] = "<module '__builtin__' (built-in)>"

        for var in frame_locals:
            if var != '__builtins__':
                frame_locals[var]=repr(frame_locals[var])
            else:
                frame_locals[var] = "<module '__builtin__' (built-in)>"

        record = dict(
            event = event,
            code = frame.f_code,
            line = frame.f_lineno,
            depth = depth,
            globals = frame_globals,
            locals = frame_locals
            )

        if event == "exception":
            record['exception'] = {
                "type": arg[0].__name__,
                "args": arg[1],
                }

        self.log.append(record)
        return record

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
    removed=0
    while all_lines[0].isspace():
        del all_lines[0]
        removed += 1

    while all_lines[-1].isspace():
        del all_lines[-1]
    
    # adjust offsets for removed lines
    if removed:
        for code in line_offsets:
            line_offsets[code] -= removed

    return all_lines, line_offsets


def process_events(events):
    """ Takes the events produced by Tracer.trace, grabs all the
    relevent python source and returns the trace in a format that's
    almost ready to be replayed """
    all_lines, line_offsets = assemble_source(events)

    result_events = []

    for event in events:
        if event['event'] not in ('line','return', 'call', 'globals', 'locals'):
            continue
        
        code = event['code']
        trace_line = dict(line=line_offsets[code] + event['line'])

        if event['event'] == 'exception':
            trace_line['exception'] =  event['exception']['type']
            
        for entry in ('stdout', 'stderr'):
            if entry in event:
                trace_line[entry] = ''.join(event[entry])

        for entry in ('globals', 'locals'):
            if entry in event:
                trace_line[entry] = event[entry]
            
        if result_events and result_events[-1]['line'] == trace_line['line']:
            for item in trace_line:
                if item not in result_events[-1]:
                    result_events[-1][item] = trace_line[item]

        else:
            result_events.append(trace_line)

    return dict(source=''.join(all_lines), trace=result_events)
    
def process_events_json(events):
    """ Like process_events, except this will convert the trace to a
    json string before returning it """
    trace=process_events(events)
    return json.dumps(trace, separators=(',',':'), indent=2)

def clean_file(filename, marker='#>'):
    '''Removes all annotations from a file, returning the file as a string.'''
    clean=[]
    for line in file(filename):
        if not line.strip().startswith(marker):
            clean.append(line)

    return ''.join(clean)

def strip_annotation(line, marker):
    '''Removes whitespace, removes marker, removes remaining whitespace,
    returns the annotation.''' 
    return line.strip()[len(marker):].strip()

def parse_annotations(filename, marker='#>'):
    '''This takes a file with annotations, marked at the start of the line by a
    marker, and creates dictionary mapping line numbers to annotations, as if
    the file had no annotations.'''
    
    f=open(filename, 'r')
    annotations = {} #maps line numbers to annotations
    lineno = -1 #the traces are indexed from 0, I would like this to change

    try:
        while True:
            current_line=f.next()
            lineno+=1

            if current_line.strip().startswith(marker):
                annotation=[strip_annotation(current_line, marker)] 
                try:
                    next_line=f.next() 
                except StopIteration:
                    #Annotation is at the end of a file
                    raise SyntaxError, \
                          "LINE %d: Annotations must be before at least one source line." \
                          % (lineno+len(annotations)+1) 

                #comments, blank lines, and further annotations
                while next_line.strip().startswith('#') \
                      or not next_line.strip():

                    if next_line.strip().startswith(marker):
                        annotation.append(strip_annotation(next_line, marker))
                    else:    
                        lineno+=1

                    next_line=f.next()

                annotations[lineno]='\n'.join(annotation)

    except StopIteration:
        f.close()

    return annotations

def trace(filename, pprint=True):
    '''Takes a filename and returns a complete trace, if pprint is True, the
    returned trace will be pretty printed.'''

    #This function works as a series of filters, each one modifying the text
    #and passing it on to the next stage

    #strips annoations from the file
    clean_text = clean_file(filename)
    runme_clean = tempfile.NamedTemporaryFile(mode='wt', delete=False)
    runme_clean.write(clean_text)
    runme_clean.close()

    #traces file execution 
    runner = Tracer(runme_clean.name)
    result, events = runner.trace()
    trace = process_events(events)
    
    #attaches annotations to the trace
    annotations = parse_annotations(filename)

    for entry in trace['trace']:
        lineno=entry['line']
        if lineno in annotations:
            entry['annotation']=annotations[lineno]

    if pprint:
        return json.dumps(trace, indent=2)
    else:
        return json.dumps(trace, separators=(',',':'))

def main():
    parser = optparse.OptionParser()
    parser.add_option('-f', '--filename', dest='filename', metavar='FILE',
                      help = 'Python file to run',
                      )

    parser.add_option('-p', '--pprint', action='store_true',
                      help = 'Pretty prints the JSON ouput',
                      )

    options,args = parser.parse_args()

    if not options.filename:
        parser.print_help()
        sys.exit(2)

    print trace(options.filename, pprint=options.pprint)

if __name__ == '__main__':
    main()
