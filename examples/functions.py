# Another trick for lazy programming (which will make your code better)'
#> This gives access to constants defined outside of the current file.
from math import pi
#> When you want to do something serveral times in your code (
#> or just simplify a particular bit of logic) you can define a function to do so.
#> Here is an example which finds (and returns) the area of a circle.
def circle_area(radius):
    return pi * (radius**2)

#> Once defined for a general case, the chunk of code can be referenced by supplying a parameter.
print circle_area(5)
#> This is a very useful technique
print circle_area(6)

# In Python everything is an object, so some very sophisticated techniques are possible.
#> This is called a closure
def named_area(name, radius):
    def area():
        return name + str(pi*radius**2)
    return area

#> These generate function objects which can then be called
five_area = named_area('five ', 5)
six_area = named_area('six ', 6)

#>The functions retain the arguments they were created with
print five_area()
print six_area()
