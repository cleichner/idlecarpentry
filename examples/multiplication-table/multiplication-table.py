## Multiplication table

"""

In order to visualize numbers better,
a mathematician working on a project
needs to be able to quickly generate
multiplication tables of different sizes.

Your goal is to write a Python program that
will take a number, and generate the appropriate
multiplication table inside a file.

For example, if the input is 4:

~python mutiplication-table.py 4

The output would be:

   1    2    3    4 
   2    4    6    8 
   3    6    9   12 
   4    8   12   16 

To approach this problem, lets come up
with a method of generating multiplication
tables.

## Assuming size is 4
size = 4

## Set the height to be one
height = 1

## While the height is smaller or equal to the size
while height <= size:
    ## Start at width 1
    width = 1

    ## Using a nested loop, we will
    ## create the row

    ## While the width is smaller or equal to the size
    while width <= size:

        ## Giving each entry 4 colums,
        ## print each entry. (each entry is 
        ## width * height). Because our
        ## print statement ends with a comma,
        ## the numbers will not get printed on 
        ## a new line.

        print "%4d" % (height * width),

        ## Increase the width by one
        width += 1 ## Same as "width = width + 1"
    
    ## Print new line
    print ""
    ## Increase the height by one
    height += 1


Lets test our program to make sure that it works:

~python multiplication-table.py

   1    2    3    4 
   2    4    6    8 
   3    6    9   12 
   4    8   12   16 

Great, it works fine.

The next step is to write the result into a new
file, lets call it "multiplication-file.txt".

## We create the file with writing permissions
f = open("multiplication-file.txt", "w") 

We will not replace the print statements in the code
above with f.write().

The complete code is below:

"""

import sys

f = open("multiplication-file.txt", "w")

try:
    size = int(sys.argv[1])
except:
    print "Sorry, invalid input."
    sys.exit()

def generate_table(size):
    height = 1

    while height <= size:

        width = 1
        while width <= size:

            f.write("%4d" % (height * width))
            width += 1

        f.write("\n")
        height += 1

generate_table(size)

"""
Run the program.
 
~python multiplication-table.py 6

A new file - 'multiplication-file.txt' has been
created with the following contents:


   1   2   3   4   5   6
   2   4   6   8  10  12
   3   6   9  12  15  18
   4   8  12  16  20  24
   5  10  15  20  25  30
   6  12  18  24  30  36

"""
