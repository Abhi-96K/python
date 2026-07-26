def find_maximum(numbers):
    if not numbers:
        return None
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num 
        return max_num
    
user_input = input("Enter the numbers seperated by comma: ")
num_list = [int(num.strip()) for num in user_input.split(",")]
print("The maximum number is:", find_maximum(num_list))


array_1 = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
for i in array_1:
    print(i)
    if array_1.count(i) > 1:
        print(f"{i} is repeated {array_1.count(i)} times.")