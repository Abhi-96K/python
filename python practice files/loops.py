str1 = "   Silver Spoon"
print(str1)
print(str1.strip())


str2 = "Hello !"
print(str2.rstrip('!'))
arr = {1, 2, 2, 3, 3, 3, 4, 4, 4, 4}
for i in  arr:
    a = arr.count(i)
    print(f"{i} is repeated {a} times.")