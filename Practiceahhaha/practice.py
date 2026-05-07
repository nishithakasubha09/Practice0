
# Ran = (5, 10, 15, 20, 25, 20, 30, 35, 40, 45)

# userput = int (input("Enter a number:"))

# while userput not in Ran:
#     print ("Try Again")
#     userput = int (input("Enter a number:"))
# if userput in Ran:
#     print ("Congratulations! You guessed the number!!!")

# smt = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# userput = int (input("Enter a number:"))
# for el in smt:
#     if userput == el:
#         print ("Congratulations! You guessed the number!!!")
#         break
# else:
#     print ("Try Again")
#     userput = int (input("Enter a number:"))

# no = int(input("Enter a number: "))
# sum = 1
# i = 1
# while i <= no:
#     sum *= i
#     i += 1

# print(sum)

# for row in range(8):
#     for _ in range(2):  # make each square taller
#         line = ""
#         for col in range(8):
#             if (row + col) % 2 == 0:
#                 line += "████"
#             else:
#                 line += "    "
#         print(line)

# def cal_sum (a,b):
#     sum = a+b
#     return sum

# print(cal_sum (5, 10))
# print(cal_sum(6, 7))

# RS = [5, 10]
# IDK = ["Radha", "Shyam", "Sundar", "Radhe", "Radha", "Shyam", "Sundar", "Radhe"]

# def prinsmt (list):
#     return (list)

# print(prinsmt (RS))
# print(prinsmt (IDK))




# Question 1 ans
# num = int(input("Number: "))
# count = 0

# for i in range(1, int(num**0.5) + 1):
#     if num % i == 0:
#         if i == num // i:
#             count += 1
#         else:
#             count += 2

# if (count > 2):
#     print ("Composite")
# else:
#     print ("Prime")

# Question 2 ans

# a = int (input ("Number 1: "))
# b = int (input ("Number 2: "))

# gcd = 1
# small = min(a,b)

# for i in range (1, small+1):
#     if a % i == 0 and b % i == 0:
#        gcd = i

# lcm = a * b // gcd

# print ("GCD", gcd)
# print ("LCM", lcm)

# factorial = int (input("Enter a num to find out its Factorial: "))
# count = 1

# for i in range (1, factorial+1):
#     count= count*i
    
# print (count)

f = open("Python.py", "r")

print (f)