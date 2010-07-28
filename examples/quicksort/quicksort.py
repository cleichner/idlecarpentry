## Quicksort
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
