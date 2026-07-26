def star_pyramid(rows):
    for i in range(1, rows + 1):
        spaces = " " * (rows - i)
        stars = "* " * i
        print(spaces + stars)

# Example
star_pyramid(int(input("ennter the nuber of rows:")))
print("\n\n\n\n")

def reverse_pyramid(rows):
    for i in range(rows, 0, -1):
        spaces = " " * (rows - i)
        stars = "* " * i
        print(spaces + stars)

# Example
reverse_pyramid(5)
