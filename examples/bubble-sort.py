#> Opening it with reading permissions
f = open("melting-points.txt", "r")

dict = {}
#> Define our list
list = []

#> Parse the file
for line in f:
    #> Remove white spaces and split the file at ":"
    #> which will return [element, melting_point]
    line = line.replace(" ","").split(":")
    element = line[0]
    melting_point = int(line[1])
    
    #> Add the melting point into our list
    list.append(melting_point)

    #> When we append each melting point to our list,
    #> we will also append them to a dictionary to keep them associated
    dict[melting_point] = element

# Bubble sort
def swap(a, b):
    temp = list[a]
    list[a] = list[b]
    list[b] = temp
    
#> We will keep repeating until swapped == False
swapped = True
while swapped:
    swapped = False
    #> Looping over out list. We subtract two
    #> So we can consider the last pair.
    for i in range(len(list) - 2):
        #> Check if the adjacent elements are in the
        #> wrong order.
        if list[i] > list[i+1]:
            #> Swap them: swap is defined in a function.
            swap(i, i+1)
            swapped = True

#> Finally, we want to create a new file called
#> 'sorted-melting-points.txt' and populate it
#> with the sorted elements.
#>          
#> Creating the new file with writing permissions
n = open("sorted-melting-points.txt", "w")

for point in list:
    #> Formatting
    entry = dict[point] + ": " + str(point) + "\n"
    n.write(entry)
