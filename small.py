'''
This is a test module which should not be seen when it is imported into
something being traced. 
'''

def fun():
    print 'working'
    return 'working'

#This definitely shouldn't show up
