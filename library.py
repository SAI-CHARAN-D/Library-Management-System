import pymongo
from datetime import datetime, timedelta
from bson import ObjectId

class LibrarySystem:
    def __init__(self, mongodb_uri="mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(mongodb_uri)
        self.db = self.client['library_management']
        self.books = self.db['books']
        self.users = self.db['users']
        self.borrowings = self.db['borrowings']
        
        # Create indexes
        self.books.create_index('isbn', unique=True)
        self.users.create_index('email', unique=True)
        self.borrowings.create_index([('user_id', 1), ('book_id', 1)])
    
    def add_book(self, title, author, isbn, quantity):
        """Add a new book to the library"""
        try:
            book = {
                'title': title,
                'author': author,
                'isbn': isbn,
                'quantity': quantity,
                'available': quantity,
                'added_date': datetime.now()
            }
            result = self.books.insert_one(book)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f'Book with ISBN {isbn} already exists')
    
    def view_available_books(self, filter_criteria=None):
        """View all available books with optional filtering"""
        if filter_criteria is None:
            filter_criteria = {}
        filter_criteria['available'] = {'$gt': 0}
        return list(self.books.find(filter_criteria))
    
    def register_user(self, name, email, phone):
        """Register a new library user"""
        try:
            user = {
                'name': name,
                'email': email,
                'phone': phone,
                'registration_date': datetime.now(),
                'active_borrowings': 0
            }
            result = self.users.insert_one(user)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f'User with email {email} already exists')
    
    def borrow_book(self, user_id, book_id, duration_days=14):
        """Process a book borrowing"""
        user = self.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError('User not found')
        
        if user['active_borrowings'] >= 5:
            raise ValueError('User has reached maximum borrowing limit')
        
        book = self.books.find_one({'_id': ObjectId(book_id)})
        if not book:
            raise ValueError('Book not found')
        
        if book['available'] <= 0:
            raise ValueError('Book is not available for borrowing')
        
        borrowing = {
            'user_id': ObjectId(user_id),
            'book_id': ObjectId(book_id),
            'borrow_date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=duration_days),
            'return_date': None,
            'status': 'active'
        }
        
        # Update book availability and user's active borrowings
        self.books.update_one(
            {'_id': ObjectId(book_id)},
            {'$inc': {'available': -1}}
        )
        self.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'active_borrowings': 1}}
        )
        
        result = self.borrowings.insert_one(borrowing)
        return str(result.inserted_id)
    
    def return_book(self, borrowing_id):
        """Process a book return"""
        borrowing = self.borrowings.find_one({'_id': ObjectId(borrowing_id)})
        if not borrowing:
            raise ValueError('Borrowing record not found')
        
        if borrowing['status'] != 'active':
            raise ValueError('Book is already returned')
        
        # Update borrowing record
        self.borrowings.update_one(
            {'_id': ObjectId(borrowing_id)},
            {
                '$set': {
                    'return_date': datetime.now(),
                    'status': 'returned'
                }
            }
        )
        
        # Update book availability and user's active borrowings
        self.books.update_one(
            {'_id': borrowing['book_id']},
            {'$inc': {'available': 1}}
        )
        self.users.update_one(
            {'_id': borrowing['user_id']},
            {'$inc': {'active_borrowings': -1}}
        )
        
        return True
    
    def get_user_history(self, user_id):
        """Get borrowing history for a specific user"""
        user = self.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError('User not found')
        
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$lookup': {
                'from': 'books',
                'localField': 'book_id',
                'foreignField': '_id',
                'as': 'book'
            }},
            {'$unwind': '$book'},
            {'$project': {
                'book_title': '$book.title',
                'borrow_date': 1,
                'due_date': 1,
                'return_date': 1,
                'status': 1
            }}
        ]
        
        return list(self.borrowings.aggregate(pipeline))
    
    def get_overdue_books(self):
        """Get all overdue books"""
        pipeline = [
            {'$match': {
                'status': 'active',
                'due_date': {'$lt': datetime.now()}
            }},
            {'$lookup': {
                'from': 'books',
                'localField': 'book_id',
                'foreignField': '_id',
                'as': 'book'
            }},
            {'$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }},
            {'$unwind': '$book'},
            {'$unwind': '$user'},
            {'$project': {
                'book_title': '$book.title',
                'user_name': '$user.name',
                'user_email': '$user.email',
                'borrow_date': 1,
                'due_date': 1
            }}
        ]
        
        return list(self.borrowings.aggregate(pipeline))

def print_menu():
    print("\nLibrary Management System")
    print("1. Add Book")
    print("2. View Available Books")
    print("3. Register User")
    print("4. Borrow Book")
    print("5. Return Book")
    print("6. View User History")
    print("7. View Overdue Books")
    print("8. Exit")

def format_book(book):
    return f"Title: {book['title']}\nAuthor: {book['author']}\nISBN: {book['isbn']}\nAvailable: {book['available']}/{book['quantity']}\n"

def main():
    library = LibrarySystem()
    
    while True:
        try:
            print_menu()
            choice = input("Enter your choice (1-8): ")
            
            if choice == '1':
                title = input("Enter book title: ")
                author = input("Enter author name: ")
                isbn = input("Enter ISBN: ")
                quantity = int(input("Enter quantity: "))
                
                book_id = library.add_book(title, author, isbn, quantity)
                print(f"\nBook added successfully! ID: {book_id}")
                
            elif choice == '2':
                books = library.view_available_books()
                if not books:
                    print("\nNo books available!")
                else:
                    print("\nAvailable Books:")
                    for book in books:
                        print("\n" + format_book(book))
                        
            elif choice == '3':
                name = input("Enter user name: ")
                email = input("Enter user email: ")
                phone = input("Enter user phone: ")
                
                user_id = library.register_user(name, email, phone)
                print(f"\nUser registered successfully! ID: {user_id}")
                
            elif choice == '4':
                user_id = input("Enter user ID: ")
                book_id = input("Enter book ID: ")
                duration = input("Enter duration in days (default 14): ")
                
                duration_days = int(duration) if duration else 14
                borrowing_id = library.borrow_book(user_id, book_id, duration_days)
                print(f"\nBook borrowed successfully! Borrowing ID: {borrowing_id}")
                
            elif choice == '5':
                borrowing_id = input("Enter borrowing ID: ")
                
                if library.return_book(borrowing_id):
                    print("\nBook returned successfully!")
                    
            elif choice == '6':
                user_id = input("Enter user ID: ")
                history = library.get_user_history(user_id)
                
                if not history:
                    print("\nNo borrowing history found!")
                else:
                    print("\nBorrowing History:")
                    for record in history:
                        print(f"\nBook: {record['book_title']}")
                        print(f"Borrowed: {record['borrow_date']}")
                        print(f"Due: {record['due_date']}")
                        print(f"Returned: {record['return_date'] or 'Not returned'}")
                        print(f"Status: {record['status']}")
                        
            elif choice == '7':
                overdue = library.get_overdue_books()
                
                if not overdue:
                    print("\nNo overdue books!")
                else:
                    print("\nOverdue Books:")
                    for record in overdue:
                        print(f"\nBook: {record['book_title']}")
                        print(f"User: {record['user_name']}")
                        print(f"Email: {record['user_email']}")
                        print(f"Borrowed: {record['borrow_date']}")
                        print(f"Due: {record['due_date']}")
                        
            elif choice == '8':
                print("\nThank you for using the Library Management System!")
                break
                
            else:
                print("\nInvalid choice! Please try again.")
                
        except ValueError as e:
            print(f"\nError: {str(e)}")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()