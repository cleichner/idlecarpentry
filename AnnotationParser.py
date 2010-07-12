import sys

#is it okay to annotate block strings? 
#or should they be skipped, like comments?
#should comments be skipped, or can they be annotated? If they are traced, they should be annotated.

def clean_file(filename, marker='#>'):
    '''Removes all annotations from a file, returning the file as a string.'''
    clean=[]
    for line in file(filename):
        if not line.strip().startswith(marker):
            clean.append(line)

    return ''.join(clean)

def parse_annotations(filename, marker='#>'):
    '''This takes a file with annotations, marked at the start of the line by a
    marker, and creates dictionary mapping line numbers to annotations, as if
    the file had no annotations.'''
    
    f=open(filename, 'r')
    annotations = {} #maps line numbers to annotations
    lineno = -1 #the traces are indexed from 0, I would like this to change

    #This is a DIY for loop so I can advance as I please through the input file
    try:
        while True:
            current_line=f.next()
            lineno+=1

            if current_line.strip().startswith(marker):
                try:
                    next_line=f.next() 
                except StopIteration:
                    #Annotation is at the end of a file, maybe should just print a warning and ignore the line
                    raise SyntaxError, "LINE %d: Annotations must be before at least one source line." % (len(silent_file)+len(annotations)+1) 

                #comments and blank lines
                while next_line.strip().startswith('#') or not next_line.strip():
                    #needs to handle multiple consecutive annotations? right now the last one overwrites any before it
                    next_line=f.next()
                    lineno+=1

                annotations[lineno]=current_line.strip()[2:].strip()

    except StopIteration:
        f.close()

    return annotations

def parse_and_clean_annotations(filename, marker='#>'):
    '''This takes a file and strips any annotations, marked at the start of the
    line by a marker, creating a dictionary mapping line numbers to annotations
    and a string which consists of the file, without any annotations'''
    
    f=open(filename, 'r')
    annotations={} #maps line numbers to annotations
    silent_file=[]  #this is returned as a string containing the file without annotations
    lineno=-1 #the traces are indexed from 0, I would like this to change

    #This is a DIY for loop so I can advance as I please through the input file
    try:
        while True:
            current_line=f.next()
            lineno+=1

            if current_line.strip().startswith(marker):
                try:
                    next_line=f.next() 
                except StopIteration:
                    #Annotation is at the end of a file, maybe should just print a warning and ignore the line
                    raise SyntaxError, "LINE %d: Annotations must be before at least one source line." % (len(silent_file)+len(annotations)+1) 

                #comments and blank lines
                while next_line.strip().startswith('#') or not next_line.strip():
                    #needs to handle multiple consecutive annotations? right now the last one overwrites any before it
                    silent_file.append(next_line)
                    next_line=f.next()
                    lineno+=1

                silent_file.append(next_line)
                annotations[lineno]=current_line.strip()[2:].strip()

            else:
                silent_file.append(current_line)

    except StopIteration:
        f.close()

    return annotations, ''.join(silent_file)

if __name__=='__main__':
    #needs unittests
    annotations = parse_annotations(sys.argv[1])
    print 'parse_annotations'
    print annotations
    print 'clean_file'
    runfile = clean_file(sys.argv[1])
    print runfile
    exec(runfile)
