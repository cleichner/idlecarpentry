#>This is an external module that gives access to the execution system
import sys

#>This is a small block of code that can be called remotely
def function(x, y):
    z = x + y
    print 'z =', z, 'x =', x, 'y =', y
    return z, x, y

#>These variables hold values and can be called by name
a = 3
b = 4
c = 2
d = 6
#>This uses the function we defined earlier
e = function(a, b)
f = function(c, d)
print function(e , f)
