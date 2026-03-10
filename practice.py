
'''Ran = (5, 10, 15, 20, 25, 20, 30, 35, 40, 45)

userput = int (input("Enter a number:"))

while userput not in Ran:
    print ("Try Again")
    userput = int (input("Enter a number:"))
if userput in Ran:
    print ("Congratulations! You guessed the number!!!")'''

smt = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

userput = int (input("Enter a number:"))
for el in smt:
    if userput == el:
        print ("Congratulations! You guessed the number!!!")
        break
else:
    print ("Try Again")
    userput = int (input("Enter a number:"))