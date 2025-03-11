# Library Management System

A Python-based Library Management System using MongoDB for managing books, users, and borrowing transactions.

## Features
- Add and view available books.
- Register users.
- Borrow and return books with due date tracking.
- View user borrowing history.
- Identify overdue books.

## Requirements
Ensure you have Python and MongoDB installed, then install the required dependencies:
```sh
pip install pymongo bson
```

## Usage
Run the script from the terminal:
```sh
python library_system.py
```

### Menu Options:
1. Add Book
2. View Available Books
3. Register User
4. Borrow Book
5. Return Book
6. View User History
7. View Overdue Books
8. Exit

### Example Usage:
- Add a book:
  ```sh
  Enter book title: The Great Gatsby
  Enter author name: F. Scott Fitzgerald
  Enter ISBN: 1234567890
  Enter quantity: 5
  ```
- Register a user:
  ```sh
  Enter user name: John Doe
  Enter user email: john.doe@example.com
  Enter user phone: 1234567890
  ```
- Borrow a book:
  ```sh
  Enter user ID: 605c72d8f1a2bcd123456789
  Enter book ID: 605c72d8f1a2bcd123456788
  Enter duration in days (default 14): 10
  ```

## MongoDB Collections
- `books`: Stores book details including availability.
- `users`: Stores user information.
- `borrowings`: Stores active and past borrowing records.

## License
This project is open-source and available under the MIT License.
