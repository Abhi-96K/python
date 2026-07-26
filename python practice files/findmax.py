def sum_list(numbers):
    total = 0
    for num in numbers:
        total += num
    return total 

user_input = input(" Enter the numbers seperated by comma: ")
num_list = [int(user_input.strip()) for user_input in user_input.split(",")]
print(" The sum of the numbers is:", sum_list(num_list))