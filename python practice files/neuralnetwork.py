def iseven(n):
    if n % 2 == 0:
        return True
    else:
        return False

num = int (input("Enter a number: "))
while not iseven(num):
    print("The number is odd. Please enter an even number.")
    num = int (input("Enter a number: "))
print("Thank you! You entered an even number:", num)
