## Quicksort
#> This is the list of values we're going to sort with QS
list = [1,-34534,3,32,100]

def quicksort(array):
    #> We need to keep track of values that are greater than
    #> and less than our pivot point
    less = []
    greater = []
    #> If our array only has one element, then we're already
    #> sorted, so let's bail out.
    if len(array) <= 1:
        return array
    #> Let's choose the first element of the array as our first
    #> pivot point.
    pivot = array[0]

    #> We go through the rest of the list...
    for x in array[1:]:
        #> ...and if the value that we find in the list is LESS than
        #> our pivot, we append it to our less collection...
        if x <= pivot:
            less.append(x)
        #> ...likewise, if GREATER, append to greater collection.
        else:
            greater.append(x)

    #> Then we just call quicksort again on the greater and
    #> lesser value collections.  That's recursion, baby!
    #> (oh, and make sure to wrap it around the pivot point)
    return quicksort(less) + [pivot] + quicksort(greater)

#> Let's run our quicksort on the list that we created
sorted_list = quicksort(list)

#> And print out our final result
print sorted_list
