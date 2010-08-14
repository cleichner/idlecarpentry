# How make your program loop (so you can be lazy)
example_list = [3, 5, 'hello', 3.0]

#> This is the primary looping construct for finite loops in Python.
for element in example_list:
    #>The variable named element here can be called anything which makes sense to you.
    #> It is the current member of the thing you are looping over.
    print element

#> For loops work on anything iterable
for letter in "word":
    print letter,

#> That comma at the end of the last print statement suppressed the newline.
#> This prints one explicitly.
print '\n',

#> The variable is completely arbitrary, trust me.
for salad in ('hello', 54, ('secondary', 'tuple')):
    print salad

#> The range function produces values from 0, stopping before the specified value. 
for i in range(3):
    print i,

print '\n',
  
x = 0
#> Indefinite loops are possible too.
#> They use the 'while' keyword and take a boolean value, just like the if statement.
while x < 3:
    print x,
    #> This is a shortcut which means add one to the value of x.  
    x += 1
