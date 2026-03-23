"""
Library Management System - Improved Resume Version
Connor Warming

Features:
- Object-oriented design
- Custom exception handling
- Interactive CLI menu
- JSON data persistence
- Search by title or author
- Borrow/return book tracking
- Member registration and book inventory management

Run:
    python library_management_system_improved.py
"""

import json
from pathlib import Path


DATA_FILE = Path("library_data.json")


# =========================
# Custom Exceptions
# =========================

class BookNotAvailableException(Exception):
    def __init__(self, book_title: str):
        super().__init__(f"The book '{book_title}' is not available for borrowing.")


class BookNotBorrowedException(Exception):
    def __init__(self, member_name: str, book_title: str):
        super().__init__(f"Member '{member_name}' has not borrowed the book '{book_title}'.")


class InvalidMemberException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Invalid member details: {reason}")


class MaxBooksLimitException(Exception):
    def __init__(self, max_limit: int):
        super().__init__(f"Cannot borrow more books. Maximum limit is {max_limit} books per member.")


class DuplicateBookException(Exception):
    def __init__(self, book_id: str):
        super().__init__(f"A book with ID '{book_id}' already exists.")


class DuplicateMemberException(Exception):
    def __init__(self, member_id: str):
        super().__init__(f"A member with ID '{member_id}' already exists.")


# =========================
# Book Class
# =========================

class Book:
    def __init__(self, book_id: str, title: str, author: str, is_borrowed: bool = False, borrowed_by: str | None = None):
        self.book_id = book_id.strip()
        self.title = title.strip()
        self.author = author.strip()
        self.is_borrowed = is_borrowed
        self.borrowed_by = borrowed_by

    def borrow_book(self, member_id: str):
        if self.is_borrowed:
            raise BookNotAvailableException(self.title)
        self.is_borrowed = True
        self.borrowed_by = member_id

    def return_book(self):
        self.is_borrowed = False
        self.borrowed_by = None

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "is_borrowed": self.is_borrowed,
            "borrowed_by": self.borrowed_by,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            is_borrowed=data.get("is_borrowed", False),
            borrowed_by=data.get("borrowed_by"),
        )

    def __str__(self):
        status = "Borrowed" if self.is_borrowed else "Available"
        borrower = f" | Borrowed by: {self.borrowed_by}" if self.borrowed_by else ""
        return f"{self.book_id} - {self.title} by {self.author} [{status}]{borrower}"


# =========================
# Member Class
# =========================

class Member:
    MAX_BOOKS = 3

    def __init__(self, member_id: str, name: str, borrowed_books: list[str] | None = None):
        if not member_id or not member_id.strip():
            raise InvalidMemberException("Member ID cannot be empty.")
        if not name or not name.strip():
            raise InvalidMemberException("Name cannot be empty.")

        self.member_id = member_id.strip()
        self.name = name.strip()
        self.borrowed_books = borrowed_books[:] if borrowed_books else []

    def borrow_book(self, book_id: str):
        if len(self.borrowed_books) >= self.MAX_BOOKS:
            raise MaxBooksLimitException(self.MAX_BOOKS)
        if book_id not in self.borrowed_books:
            self.borrowed_books.append(book_id)

    def return_book(self, book_id: str, book_title: str):
        if book_id not in self.borrowed_books:
            raise BookNotBorrowedException(self.name, book_title)
        self.borrowed_books.remove(book_id)

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "borrowed_books": self.borrowed_books,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            member_id=data["member_id"],
            name=data["name"],
            borrowed_books=data.get("borrowed_books", []),
        )

    def __str__(self):
        return f"{self.member_id} - {self.name} (Books borrowed: {len(self.borrowed_books)})"


# =========================
# Library Class
# =========================

class Library:
    def __init__(self, name: str):
        self.name = name.strip()
        self.books: dict[str, Book] = {}
        self.members: dict[str, Member] = {}

    # ---------- Persistence ----------

    def save_data(self):
        data = {
            "library_name": self.name,
            "books": {book_id: book.to_dict() for book_id, book in self.books.items()},
            "members": {member_id: member.to_dict() for member_id, member in self.members.items()},
        }
        DATA_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")

    def load_data(self):
        if not DATA_FILE.exists():
            return

        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        self.name = data.get("library_name", self.name)

        self.books = {
            book_id: Book.from_dict(book_data)
            for book_id, book_data in data.get("books", {}).items()
        }

        self.members = {
            member_id: Member.from_dict(member_data)
            for member_id, member_data in data.get("members", {}).items()
        }

    # ---------- Book Management ----------

    def add_book(self, book_id: str, title: str, author: str):
        book_id = book_id.strip()
        if book_id in self.books:
            raise DuplicateBookException(book_id)

        self.books[book_id] = Book(book_id, title, author)
        print(f"Book '{title}' added successfully.")

    def search_books(self, keyword: str):
        keyword = keyword.strip().lower()
        results = [
            book for book in self.books.values()
            if keyword in book.title.lower() or keyword in book.author.lower()
        ]
        return results

    def display_all_books(self):
        if not self.books:
            print("No books in the library.")
            return

        print("\nAll Books:")
        for book in self.books.values():
            print(f"  {book}")

    def display_available_books(self):
        available = [book for book in self.books.values() if not book.is_borrowed]
        if not available:
            print("No books are currently available.")
            return

        print("\nAvailable Books:")
        for book in available:
            print(f"  {book}")

    # ---------- Member Management ----------

    def register_member(self, member_id: str, name: str):
        member_id = member_id.strip()
        if member_id in self.members:
            raise DuplicateMemberException(member_id)

        member = Member(member_id, name)
        self.members[member_id] = member
        print(f"Member '{name}' registered successfully.")

    def display_all_members(self):
        if not self.members:
            print("No registered members.")
            return

        print("\nRegistered Members:")
        for member in self.members.values():
            print(f"  {member}")
            if member.borrowed_books:
                print("    Borrowed Books:")
                for book_id in member.borrowed_books:
                    if book_id in self.books:
                        print(f"      - {self.books[book_id].title} ({book_id})")
            else:
                print("    Borrowed Books: None")

    # ---------- Borrow / Return ----------

    def borrow_book(self, member_id: str, book_id: str):
        if member_id not in self.members:
            print(f"Member ID '{member_id}' does not exist.")
            return

        if book_id not in self.books:
            print(f"Book ID '{book_id}' does not exist.")
            return

        member = self.members[member_id]
        book = self.books[book_id]

        try:
            member.borrow_book(book_id)
            book.borrow_book(member_id)
            print(f"'{member.name}' borrowed '{book.title}'.")
        except (MaxBooksLimitException, BookNotAvailableException) as e:
            if book_id in member.borrowed_books and book.is_borrowed:
                # only rollback if needed
                if book.borrowed_by != member_id:
                    member.borrowed_books.remove(book_id)
            print(f"Borrow error: {e}")

    def return_book(self, member_id: str, book_id: str):
        if member_id not in self.members:
            print(f"Member ID '{member_id}' does not exist.")
            return

        if book_id not in self.books:
            print(f"Book ID '{book_id}' does not exist.")
            return

        member = self.members[member_id]
        book = self.books[book_id]

        try:
            member.return_book(book_id, book.title)
            book.return_book()
            print(f"'{member.name}' returned '{book.title}'.")
        except BookNotBorrowedException as e:
            print(f"Return error: {e}")


# =========================
# CLI Helpers
# =========================

def seed_sample_data(library: Library):
    if library.books or library.members:
        return

    sample_books = [
        ("B001", "Python Programming", "John Smith"),
        ("B002", "Data Structures in Python", "Jane Doe"),
        ("B003", "Clean Code", "Robert C. Martin"),
        ("B004", "Automate the Boring Stuff", "Al Sweigart"),
    ]

    sample_members = [
        ("M001", "Alice Johnson"),
        ("M002", "Bob Williams"),
        ("M003", "Charlie Kim"),
    ]

    for book_id, title, author in sample_books:
        library.books[book_id] = Book(book_id, title, author)

    for member_id, name in sample_members:
        library.members[member_id] = Member(member_id, name)


def print_menu():
    print("\n" + "=" * 55)
    print("LIBRARY MANAGEMENT SYSTEM")
    print("=" * 55)
    print("1. Add Book")
    print("2. Register Member")
    print("3. Borrow Book")
    print("4. Return Book")
    print("5. View Available Books")
    print("6. View All Books")
    print("7. View All Members")
    print("8. Search Books")
    print("9. Save Data")
    print("10. Exit")


def run_library_app():
    library = Library("City Central Library")
    library.load_data()
    seed_sample_data(library)

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                book_id = input("Enter book ID: ")
                title = input("Enter book title: ")
                author = input("Enter author: ")
                library.add_book(book_id, title, author)

            elif choice == "2":
                member_id = input("Enter member ID: ")
                name = input("Enter member name: ")
                library.register_member(member_id, name)

            elif choice == "3":
                member_id = input("Enter member ID: ")
                book_id = input("Enter book ID: ")
                library.borrow_book(member_id, book_id)

            elif choice == "4":
                member_id = input("Enter member ID: ")
                book_id = input("Enter book ID: ")
                library.return_book(member_id, book_id)

            elif choice == "5":
                library.display_available_books()

            elif choice == "6":
                library.display_all_books()

            elif choice == "7":
                library.display_all_members()

            elif choice == "8":
                keyword = input("Enter title or author keyword: ")
                results = library.search_books(keyword)
                if not results:
                    print("No matching books found.")
                else:
                    print("\nSearch Results:")
                    for book in results:
                        print(f"  {book}")

            elif choice == "9":
                library.save_data()
                print("Library data saved successfully.")

            elif choice == "10":
                library.save_data()
                print("Data saved. Goodbye.")
                break

            else:
                print("Invalid option. Please select 1-10.")

        except (DuplicateBookException, DuplicateMemberException, InvalidMemberException) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_library_app()