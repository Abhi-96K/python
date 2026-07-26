from pymongo import MongoClient
# Step 1: Establish connection
client = MongoClient("mongodb://localhost:27017/")
db = client["LibraryDB"]
books = db["Books"]
# ------------------ INSERT Operations ------------------
print("\n--- Inserting 5 Books ---")
book_data = [
    {"book_id": 1, "title": "Python Basics", "author": "John Smith", "year":
    2020},
    {"book_id": 2, "title": "Learning MongoDB", "author": "Anna Lee", "year":
    2019},
    {"book_id": 3, "title": "Flask for Web", "author": "Mike Doe", "year": 2021},
    {"book_id": 4, "title": "Data Structures", "author": "Nina Roy", "year":
    2018},
    {"book_id": 5, "title": "Machine Learning", "author": "Ravi Kumar", "year":
    2022},
]
books.insert_many(book_data)
# ------------------ READ Operations ------------------
print("\n--- Retrieving 5 Books ---")
for book in books.find().limit(5):
    print(book)
# ------------------ UPDATE Operations ------------------
print("\n--- Updating 5 Books ---")
updates = [
    (1, {"author": "John S."}),
    (2, {"year": 2020}),
    (3, {"title": "Flask Web Development"}),
    (4, {"author": "Dr. Nina Roy"}),
    (5, {"year": 2023}),
]
for book_id, new_values in updates:
    books.update_one({"book_id": book_id}, {"$set": new_values})
# Show updated records
for book in books.find().limit(5):
    print(book)
# ------------------ DELETE Operations ------------------
print("\n--- Deleting 5 Books ---")
for book_id in range(1, 6):
    books.delete_one({"book_id": book_id})
# Final check
print("\n--- Final Books in Collection ---")
for book in books.find():
    print(book)