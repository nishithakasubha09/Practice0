# Student = { 
#     "Name" : "Nishitha",
#     "Age" : 13,
#     "School" : "Hare Krishna School"
#   }
# '''Student ["Age"] = 14
# Student ["Grade"] = "9th"'''

# print (len(list(Student.keys()))) 

# num = 36
# count = 0

# for i in range(1, int(num**0.5) + 1):
#     if num % i == 0:
#         if i == num // i:
#             count += 1
#         else:
#             count += 2

# print(count)

# a = int (input ("Number 1: "))
# b = int (input ("Number 2: "))

# gcd = 1
# small = min(a,b)

# for i in range (1, small+1):
#     if a % i == 0 and b % i == 0:
#        gcd = i
# print (gcd)



def sumofno(items, idx=0):
    if idx == len(items):
        return
    print(items[idx])
    sumofno(items, idx + 1)

a = ["apple", "cat", "blue", "pizza", "cloud", "keyboard", "star"]

sumofno(a)