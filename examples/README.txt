The files in this directory are meant to show the potential of the tracing
extensions as a teaching and learning tool.

Any file which ends in '.json' in this directory can be opened and run by the
tracer directly. What this means is that when those files are opened from
within the modified IDLE (or opened from the command-line) they will
immediately be opened into the trace display interface. 

The '.py' files are provided for some of these files to show how the traces are
generated and allow for modification, however, all trace files will execute
independent from their creation environment.

The trace interface uses a media-player metaphor for stepping through the
source code with 'play/pause' automatically moving through the code in the
order of its execution, the step forward and step back buttons moving the
current line forward or backwards one line of source, and the rewind button
going back to the beginning of execution. Any annotations provided with the
file are displayed in the box marked 'Explanations' and global and local
variables are displayed directly below that. Any output from the program is
displayed in the large box on the bottom (stderr displays in red, stdout in
black).

If you would like to generate a trace file of your own, you can open an
existing file in IDLE or create one from scratch. To create a trace, select
from the 'Run' menu 'Create Trace'. This will generate a trace of the execution
of your current code with any lines preceded with '#>' stripped out by the
tracer and used to create the explanations/annotations seen in the right upper
box when the trace is played back. Only code which is defined in the source
file will be traced into (though any code which is imported can be executed).
Currently reading from stdin isn't supported, but reading from files works
fine.  The trace will be saved in the same directory as the source file, with
the same name and a '.json' extension.

chaoslichen@gmail.com
