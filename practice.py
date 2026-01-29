'''Times = input("How many number of times do you want to print Radhe? :")

Name = "Radhe"
count = 1

while count <= int(Times):
    print ("Radhe", count)
    count +=1

Count = 100
while Count >= 1:
    print (Count)
    Count -= 1'''

Dict = {
    "Name" : "Radhe",
    "Age" : 14,
    "City" : "Mathura",
    "School" : "Hare Krishna school",
    "Subjects" : ["Maths", "Science", "English", "Sanskrit"],
    "Marks": {
        "Maths" : 95,
        "Science" : 98,
        "English" : 93,
        "Sanskrit" : 97
    }

}

Dict["Hobby"] = "Doing Kirtan"
print (Dict)