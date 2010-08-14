# a brief introduction to the native datatypes of Python

#> Lists are the most common aggregate datatype in Python, 
#> an empty one is symbolized by empty brackets.
empty_list = []
#> A list can be created with contents in it, they do not need to be the same type.
initialized_list = [1, 4.0, 'strings are fine', ['so are', 'lists']]

#> A list can be added to another list using the extend method
empty_list.extend(initialized_list)

#> Lists can be used as stacks by using append() and pop()
initialized_list.append('new value')
print initialized_list.pop()

#> They can also be subscripted
print initialized_list[0]
print initialized_list[3][0]
#> Python allows negative indexes
print initialized_list[-1]

#tuples
#> Tuples are like lists but they are immutable
example_tuple = (2, 4, "can't touch this")
print example_tuple[2]

#dictionaries
#> Dictionaries allow associations between immutable keys and values
example_dict = {'one':1, 'two':2, 'three':3}
print example_dict['one']
#> This is how new values are added and old ones are modified in a dictionary
example_dict[4] = 'four'
print example_dict

#strings
#> Strings are also immutable 
example_string = 'this is an example string'
#> Strings have some great methods in Python
print example_string.split()
#> These are just the start
print example_string.startswith('this')
print example_string.upper()
