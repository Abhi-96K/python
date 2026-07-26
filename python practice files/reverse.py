number = int(input("enter any number greater than 10:"))
rev = 0
while number > 0:
    rem = number % 10
    rev = rev * 10 + rem
    number = number // 10
print("reverse of the number is:", rev)
"""rem = number % 10  means that we are getting the last digit of the number and storing it in rem variable
rev = rev * 10 + rem means that we are multiplying the current value of rev by 10 and adding the last digit (rem) to it. This effectively shifts the digits of rev to the left and adds the new digit at the end.
number = number // 10 means that we are performing integer division by 10, which removes the last digit from the number. This allows us to process the next digit in the next iteration of the loop."""

a = 1234
rev = 0
while a > 0:
    rem = a % 10
    rev = rev * 10 + rem
    a = a // 10
print("reverse of the number is:", rev)


n = int(input("Enter number: "))

rev = int(str(abs(n))[::-1])   # reverse using string

if n < 0:
    rev = -rev

print(rev)

