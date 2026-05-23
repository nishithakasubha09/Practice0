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

# def sumofno(items, idx=0):
#     if idx == len(items):
#         return
#     print(items[idx])
#     sumofno(items, idx + 1)
# a = ["apple", "cat", "blue", "pizza", "cloud", "keyboard", "star"]
# sumofno(a)



# with open("prac.txt", "w")as f:
#     f.write("Hi everyone\nwe are learning File I/O\nusing Java\nI like programming with Java")


# with open ("prac.txt","r")as f:
#     data = f.read()
# new_data = data.replace("Java", "python")
# with open ("prac.txt","w")as f:
#     f.write(new_data)

# def look():
#     learn = data.find("java")
#     if (learn !=-1):
#         print (True)
#     else:
#         print(False)
# look()







def for_line():
    line = 1
    data = True
    word = "learning"
    with open ("prac.txt","r")as f:
        while data:
            data = f.readline()
            if (word in data):
                print(line)
                return
            line +=1
        return -1    
for_line()



