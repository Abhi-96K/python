from pymongo import MongoClient


client = MongoClient("mongodb+srv://0irrao99:<db_password>@cluster1.6ais2mh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")



db = client['LibraryDB']
books = db['Books']

# ---------------------- INSERT ----------------------
book_data = [
    {"title": "Python 101", "author": "John Doe", "year": 2020},
    {"title": "Learning MongoDB", "author": "Jane Smith", "year": 2021},
    {"title": "AI Basics", "author": "Alice Johnson", "year": 2019},
    {"title": "Data Science Handbook", "author": "Bob Lee", "year": 2022},
    {"title": "Machine Learning", "author": "Tom Hardy", "year": 2023}
]
books.insert_many(book_data)

# ---------------------- READ ----------------------
print("\nAll books:")
for book in books.find():
    print(book)

print("\nBooks published after 2020:")
for book in books.find({"year": {"$gt": 2020}}):
    print(book)

print("\nBooks by 'Jane Smith':")
for book in books.find({"author": "Jane Smith"}):
    print(book)

print("\nFind one book:")
print(books.find_one())

print("\nCount of books:")
print(books.count_documents({}))

# ---------------------- UPDATE ----------------------
books.update_one({"title": "Python 101"}, {"$set": {"year": 2024}})
books.update_one({"author": "Jane Smith"}, {"$set": {"author": "Jane A. Smith"}})
books.update_one({"title": "AI Basics"}, {"$inc": {"year": 1}})
books.update_one({"title": "Data Science Handbook"}, {"$set": {"genre": "Education"}})
books.update_one({"title": "Machine Learning"}, {"$set": {"publisher": "TechPress"}})

# ---------------------- DELETE ----------------------
books.delete_one({"title": "Python 101"})
books.delete_one({"author": "Jane A. Smith"})
books.delete_one({"title": "AI Basics"})
books.delete_one({"title": "Data Science Handbook"})
books.delete_one({"title": "Machine Learning"})

print("\nFinal list of books:")
for book in books.find():
    print(book)

