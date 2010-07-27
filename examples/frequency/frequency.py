#> open file 'text.txt'
f = open("text.txt", "r")
#> create new file 'frequency.txt'
n = open("frequency.txt", "w")

#> define our dictionary
dict = {}

#> loop over each line in 'text.txt'
for line in f:
    #> split this line into words
    parsed_line = line.split(" ")
    #> loop over each word
    for word in parsed_line:
        #> If this is a new word that we did not see before
        if word in dict:
            #> Add 1 to it's frequency count
            dict[word] += 1
        else:
            word = word.replace("\n","")
            #> Add it to the dictonary with frequency count 1
            dict[word] = 1

for item in dict:
    #> formatting the entry
    entry = str(item) + ": " +  str(dict[item]) + "\n"
    n.write(entry)
    
f.close()
n.close()
