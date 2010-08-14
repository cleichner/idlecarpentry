
# How to make your program make choices
#> Python has three ways to make something conditionally execute.
#> The first is the 'if' statement.
if True:
    print "This 'if' statement executed."
    
#> The 'if' statement takes one argument which can be True or False (remember the ':' at the end)
if False:
    print "This one didn't."

#> Any boolean expression can be used in an 'if' statement. Here are some examples of boolean expressions.
print 4 > 5 
print 4 < 5
#> This means is equal to, a single equals sign was already taken by the assignment operator
print 3 == 3
#> This means does not equal
print 3 != 5 

#> This is how they can be used
if 4 < 5:
    print 'math still works'

#> Equality checks can work for strings too!  
if 'Python' == 'Python':
    print 'hooray!'

#> The else statement evalutes when an associated if statement evaluates false.
if 'Python' == 'The C Programming Language':
    print 'something very scary happened'
else:
    print 'all is right with the world'

#> The elif statement lets you pick from several sections of code
x = 5
if x > 5:
    print 'x is bigger than five'
elif x == 5:
    print 'x is five'
else:
    print 'x is less than five'
