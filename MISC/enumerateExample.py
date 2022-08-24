myList = ['Option 1', 'Option 2', 'Option 3']

#this one prints it on same line 
print('')
print(list(enumerate(myList)))
print('Same as')
x = list(enumerate(myList, 1)) # the , 1 will start it at 1 then 2 then 3 etc
print(x, '\n')

#this one prints it on each line
for count in enumerate(myList, 1):
    print(count)

#THIS IS WHAT YOU WANT FOR LISTS AND NUMBERS TO MAKE SELECTIONS
#this one prints a nice list with #s
print('')
listNumbers=[] # makes a list of the list numbers :)
for count, stuff in enumerate(myList, 1):
    print(count,'- ' + stuff)
    listNumbers.append(count)

#this takes your selection and prints the variable
choice=int(input('\nPick a number: '))
while choice not in listNumbers:
    print('wrong, try again')
    choice=int(input('\nPick a number: '))
choice=choice-1
print(f'Your choice is {myList[choice]}')
