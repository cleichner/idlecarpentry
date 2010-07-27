## Quicksort

"""

In order to conduct several experiments,
a geologist gathered valuable data, and needs 
a quick way to sort it. In a previous example, 
we sorted a list of numbers using the bubble sort
technique. For the sake of practicing loops
and recursion, lets sort his data using a different
method called quicksort.

the data consists of several numbers:

1, 2, 4, 345, 234, 3246, 4, 2, 2, 3, -34534, 3, 32, 100

-------------------------------------------

## Quicksort

## Create a list with the above data
list = [1, 2, 4, 345, 234, 3246, 4, 2, 2, 3, -34534, 3, 32, 100]

## Quicksort function
def quicksort(array):
    ## Defining two new lists, 'less' and 'greater'
    less = []
    greater = []
    ## If the list is empty or has one element we
    ## return it
    if len(array) <= 1:
        return array

    ## Next we choose the first elment of the list,
    ## remove it from the array, and compare all the
    ## other elements to it
    pivot = array[0]
    array.remove(pivot)

    ## Iterating over every element in the list:
    ## if it is smaller then the pivot, we append
    ## it to the 'less' list we defined earlier.
    ## Otherwize, we append it to 'greater' list.
    for i in array:
        if i <= pivot:
            less.append(x)
        else:
            greater.append(x)

    ## We call quicksort on both 'less' and 'greater',
    ## and return the result. This is where the recursion
    ## is initiated.

    return quicksort(less) + [pivot] + quicksort(greater)

    
sorted_list = quicksort(list)
print sorted_list

The complete code is below:

"""

list = [1,2,4,345,234,3246,4,2,2,3,-34534,3,32,100]

def quicksort(array):
    less = []
    greater = []
    if len(array) <= 1:
        return array
    pivot = array[0]
    
    ##array.remove(pivot)
    for x in array[1:]:
        if x <= pivot:
            less.append(x)
        else:
            greater.append(x)

    return quicksort(less) + [pivot] + quicksort(greater)
            
sorted_list = quicksort(list)

print sorted_list

"""
Run the program.

~python quicksort.py

[-34534, 1, 2, 2, 2, 3, 3, 4, 4, 32, 100, 234, 345, 3246]


"""
