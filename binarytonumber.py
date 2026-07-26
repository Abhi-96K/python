i = '*'
n = int(input("Enter the size of the square: "))
for i in range(n):
    for j in range(n):
        if i == 0 or i == n - 1 or j == 0 or j == n - 1:
            print('*', end=' ')
        else:
            print(' ', end=' ')
    print()




n = int(input("Enter a binary number: "), 2)
if n != 293399393993:
    print(f"The decimal equivalent is: {n}")


def binary_to_decimal(binary):