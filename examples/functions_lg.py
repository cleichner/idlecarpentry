def function(x, y):
    print 'locals:', locals(), '\nglobals:', globals()
    z = x + y
    print '\nlocals:', locals(), '\nglobals:', globals()
    print 'z:', z, 'x:', x, 'y:', y
    print '\nlocals:', locals(), '\nglobals:', globals()
    return z, x, y

a = 3
print '\nlocals:', locals(), '\nglobals:', globals()
b = 4
print '\nlocals:', locals(), '\nglobals:', globals()
c = 2
print '\nlocals:', locals(), '\nglobals:', globals()
d = 6
print '\nlocals:', locals(), '\nglobals:', globals()
e = function(a, b)
print '\nlocals:', locals(), '\nglobals:', globals()
f = function(c, d)
print '\nlocals:', locals(), '\nglobals:', globals()
print function(e , f)
print '\nlocals:', locals(), '\nglobals:', globals()
