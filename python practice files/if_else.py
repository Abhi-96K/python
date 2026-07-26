# a = int(input("Enter a Number:"))

# if(a < 0):
#     print("Number Is Negative, Enter the Positive Number & rerun The Program.")
# elif(a > 0):
#     if(a > 0 and a < 101):
#         if(a > 0 and a < 51):
#             if(a > 0 and a < 31):
#                 if(a > 0 and a < 11):
#                     print("a Is Between 0 And 10.")
#                 elif(a > 10 and a < 21):
#                     print("a Is Between 10 & 20.")
#                 else:
#                     print("a Is Between 20 & 30.")
                

#             elif(a > 30 and a < 41):
#                 print("a is between 30 and 40.")
#             elif(a > 40 and a < 51):
#                 print("a Is Between 40 & 50.")

            
#         elif(a > 49 and a < 101):
#             if(a > 49 and a < 71):
#                 if(a > 49 and a < 61):
#                     print("The Number is betweenn 50 & 60.")
#                 else:
#                     print("The NUmberis between 60 & 70.")

#             elif(a > 70 and a < 101):
#                 if(a > 70 and a < 81):
#                     print("the nnnnumber is between 70 & 80.")
#                 elif(a > 79 and a < 91):
#                     print("The Number Is Between 80 & 90.")

#                 else:
#                     print("Number is between 90 & 101.")
                

# og_list = [1, 2, 2, 3, 4, 4, 5, 6, 7, 8, 9, 10]
# new_list = []
# for i in og_list:
#     if i not in new_list:
#         new_list.append(i)
# print(new_list)


# og1_list = [1, 2, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10]
# unique_list = []
# [unique_list.append(i) for i in og1_list if i not in unique_list]
# print(unique_list)


    
            


# import time
# n = input("Enter Your Name:")
# T = (time.strftime('%H:%M:%S'))
# print(T)
# H = int((time.strftime('%H')))
# print(H)
# if H > (3) and H < (13):
#     print("Good Morning,", n)

# elif(H > (12) and H < (17)):
#     print("Good Afternoon,", n)

# elif(H > (16) and H < (21)):
#     print("Good Evening,", n)

# elif(H > (20) and H < (24)):
#     print("Good Night,", n)

# elif(H > (0) and H < (4)):
#     print("Good Night,", n)

# else:
#     print("Fuck off,", n, ".")


# arr = [1, 2, 2, 3, 4, 4, 5, 6, 7, 8, 9, 10]
# unique_arr = []
# [unique_arr.append(i) for i in arr if i not in unique_arr]
# print(arr)
# print(unique_arr)

my_name = "Abhirath"
for i in my_name:
    if i == "r":
        break
    else:
        print(i)

list = ['larry', 'curly', 'moe']
list.append('shemp')         ## append elem at end
list.insert(0, 'xxx')        ## insert elem at index 0
list.extend(['yyy', 'zzz'])  ## add list of elems at end
print(list)  ## ['xxx', 'larry', 'curly', 'moe', 'shemp', 'yyy', 'zzz']
print(list)  ## ['xxx', 'larry', 'curly', 'moe', 'shemp', 'yyy', 'zzz']
print(list.index('curly'))    ## 2

list.remove('curly')         ## search and remove that element
list.pop(1)                  ## removes and returns 'larry'
print(list)  ## ['xxx', 'moe', 'shemp', 'yyy', 'zzz']