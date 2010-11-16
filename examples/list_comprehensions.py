
#> This is the basic list which will be used for processing in this example.
# A brief demonstration of list comprehensions:
list = ['a', 'mpilgrim', 'foo', 'b', 'b', 'd']

#> This is a typical example of imperative list processing.
#> First, a new empty list is declared.
long_words = []
#> Then, we iterate over the list.
for element in list:
    #> If the element satisfies the condition, add it to the new list
    if len(element) > 1:
        long_words.append(element)

print long_words
#> This is the functional approach, which is more like set-builder notation in math.
#> This generates a new list; the syntax mimics the list declaration.
#> It has a output function, a working variable, a source, and a conditional statement.
#> In this case, the output function is element, the working variable is element, the source is list and the conditional is len(element) > 1.
print [element for element in list if len(element) > 1]

#> This removes long_words from the global variable dictionary.
del long_words

#> This is the same thing as before, but slightly more complicated.
#> It generates a list of the upper case version of all the members of list which aren't b.
upper_list = []
for element in list:
    if element != 'b':
        upper_list.append(element.upper())

print upper_list
#> This demonstrates the ability to use an arbitrary value as the return function.
#> In this case it is element.upper()
print [element.upper() for element in list if element != 'b']
