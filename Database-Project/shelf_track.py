import sqlite3


# Helper validation functions
def get_valid_id(prompt):
    """Ensure an ID is 4 digit integer"""
    while True:
        value = input(prompt).strip()
        if not value.isdigit():
            print("Error. ID must be numeric\n")
            continue
        if len(value) != 4:
            print("Error. ID must be exactly 4 digits\n")
            continue
        return int(value)


def get_valid_int(prompt, min_val=None, max_val=None):
    """Ensure input is an integer within optional bounds"""
    while True:
        value = input(prompt).strip()
        if not value.isdigit():
            print("Error. Please enter a valid number\n")
            continue
        value = int(value)
        if min_val is not None and value < min_val:
            print(f"Error. Number must be at least {min_val}\n")
            continue
        if max_val is not None and value > max_val:
            print(f"Error. Number must be at most {max_val}\n")
            continue
        return value


def get_non_empty_text(prompt, max_length=255):
    """Ensure text input is not empty and within length limit"""
    while True:
        value = input(prompt).strip()
        if not value:
            print("Error. Field cannot be empty\n")
            continue
        if len(value) > max_length:
            print(f"Error. Text cannot exceed {max_length} characters\n")
            continue
        return value


def validate_author_id(author_id):
    """This function ensures the author ID exists in the author table before
    updating existing records (update_book)"""
    cursor.execute("SELECT id FROM author WHERE id=?", (author_id,))
    return cursor.fetchone() is not None


# ----- Functions ------
def enter_book():
    """This function allows the user to
    enter a book's title, quantity, and author.
    If this author is not from the author table,
     it is then entered as a new author"""
    try:
        title = get_non_empty_text("Enter book title: ")
        quantity = get_valid_int("Enter quantity: ", min_val=0)

        name = get_non_empty_text("Enter author name: ")
        country = get_non_empty_text("Enter author country: ")

        # Check if author exists
        cursor.execute("SELECT id FROM author WHERE name=?", (name,))
        author = cursor.fetchone()

        if author:
            authorid = author[0]
        else:
            cursor.execute("INSERT INTO author (name, country)"
                           "VALUES (?, ?)",
                           (name, country))
            # Get auto-generated ID
            authorid = cursor.lastrowid

        '''Insert book'''
        cursor.execute("INSERT INTO book (title, authorid, qty)"
                       "VALUES (?, ?, ?)",
                       (title, authorid, quantity))

        db.commit()
        print("Book added successfully.\n")
    except sqlite3.IntegrityError as e:
        print(f"Error inserting book: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def update_book():
    """This function will present the user with update options
     after inputting the ID of a book to update."""
    try:
        book_id = get_valid_id("Enter the ID of the book to update: ")

        cursor.execute('''
            SELECT book.id, book.title, book.qty, author.id,
            author.name, author.country
            FROM book
            JOIN author on book.authorid = author.id
            WHERE book.id=?
            ''', (book_id,))
        book = cursor.fetchone()

        if not book:
            print("Book not found")
            return

        b_id, b_title, b_qty, a_id, a_name, a_country = book
        print("\nSelected book:")
        print(f"Title: {b_title}")
        print(f"Quantity: {b_qty}")
        print(f"Author: {a_name} ({a_country})")

        print("\nUpdate options:")
        print("1. Title")
        print("2. Author name")
        print("3. Quantity")
        print("4. Author's country")
        print("5. Author name & country")
        print("0. Cancel")

        choice = input("Choose what to update: ")

        if choice == "1":
            new_title = get_non_empty_text("Enter new title: ")
            cursor.execute('''
            UPDATE book
            SET title = ?
            WHERE id = ?
            ''', (new_title, book_id))
        elif choice == "2":
            if not validate_author_id(a_id):
                print("Error: Invalid author ID. Unable to update author name")
                return
            new_name = get_non_empty_text(f"Enter new"
                                          f" author name(current: {a_name}): ")
            cursor.execute("UPDATE author SET name=?"
                           " WHERE id=?", (new_name, a_id))
            print("Author name updated successfully.\n")
        elif choice == "3":
            new_qty = get_valid_int("Enter the new quantity amount: ")
            cursor.execute('UPDATE book SET qty=? '
                           'WHERE id=?', (new_qty, book_id))
            print("Quantity updated successfully.\n")
        elif choice == "4":
            if not validate_author_id(a_id):
                print("Error: Invalid author ID."
                      " Unable to update author country")
                return
            new_country = get_non_empty_text(f"Enter new"
                                             f" author country "
                                             f"(current: {a_country}): ")
            cursor.execute('UPDATE author '
                           'SET country=? '
                           'WHERE id=?', (new_country, a_id))
            print("Author country updated\n")
        elif choice == "5":
            if not validate_author_id(a_id):
                print("Error: Invalid author ID. "
                      "Unable to update name and country")
            new_name = get_non_empty_text(f"Enter new"
                                          f" author name(Current: {a_name}): ")
            new_country = get_non_empty_text(f"Enter new"
                                             f" author country "
                                             f"(Current: {a_country}): ")
            cursor.execute('UPDATE author '
                           'SET name=?, country=? '
                           'WHERE id=?',
                           (new_name, new_country, a_id))
            print("Author details updated successfully\n")
        elif choice == "0":
            print("Update cancelled\n")
            return
        else:
            print("Invalid option.")

        db.commit()

    except Exception as e:
        print(f"Error updating book: {e}")


def delete_book():
    """This function will delete a book from the table
     based on the book ID inputted by the user"""
    try:
        book_id = int(input("Enter the ID of the book to delete: "))
        cursor.execute('SELECT *'
                       'FROM book'
                       ' WHERE id=?', (book_id,))
        book = cursor.fetchone()

        if not book:
            print("Book not found")
            return

        print(f"Selected book: {book}")
        confirm = input("Are you sure you want to"
                        " delete this book? (yes/no): ").lower()

        if confirm == "yes":
            cursor.execute('DELETE '
                           'FROM book '
                           'WHERE id=?', (book_id,))
            db.commit()
            print("\nBook successfully deleted\n")
        else:
            print("\nDelete cancelled\n")
    except Exception as e:
        print(f"Error deleting book: {e}")


def search_books():
    """This function returns all the details
     from the book table based on the user's keyword input"""
    try:
        keyword = input("Enter a keyword to search by title: ")
        cursor.execute('''
        SELECT
            book.id, book.title, book.qty, author.id,
            author.name, author.country
        FROM book
        JOIN author ON book.authorID = author.id
        WHERE title LIKE ?
        ''', ('%' + keyword + '%',))
        result = cursor.fetchall()

        if result:
            print("\nSearch results\n(BookID, Title, Quantity,"
                  " AuthorID, Author Name, Author Country):")
            for row in result:
                print(f"{row}\n")
        else:
            print("No book found\n")
    except Exception as e:
        print(f"Error searching books: {e}")


def view_all_books():
    """This function returns all book titles, author names and countries"""
    try:
        cursor.execute('''
            SELECT book.title, author.name, author.country
            FROM book
            JOIN author ON book.authorID = author.id
        ''')
        results = cursor.fetchall()

        if results:
            print("\nDetails")
            print("-" * 50)
            for title, name, country in results:
                print(f"Title: {title}")
                print(f"Author's name: {name}")
                print(f"Author's country: {country}")
                print("-" * 50)
        else:
            print("No book details found.")
    except Exception as e:
        print(f"Error viewing details: {e}")


# Create a file with an SQLite3 DB
db = sqlite3.connect("ebookstore.db")
cursor = db.cursor()

# Execute a SQL command to create the book table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authorID INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    FOREIGN KEY (authorid) REFERENCES author(id)
    )
    ''')

# Execute a SQL command to create the author table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL
    )
    ''')

cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('book', 3000)")

# Commit changes
db.commit()

'''If the the table is empty, populate the book table
Idea from:
https://dba.stackexchange.com/questions/223267/in-sqlite-how-to-check-the-table-is-empty-or-not'''
cursor.execute('SELECT COUNT(*) FROM book')
if cursor.fetchone()[0] == 0:
    book_data = [
        ('A Tale of Two Cities', 1290, 30),
        ("Harry Potter and the Philosopher's st", 8937, 40),
        ('The Lion, the Witch and the Wardrobe', 2356, 25),
        ('The Lord of the Rings', 6380, 37),
        ("Alice's Adventures in Wonderland", 5620, 12)
    ]

    # Inserts books
    cursor.executemany('''
        INSERT INTO book (title, authorID, qty)
        VALUES(?, ?, ?)
        ''', book_data)

    print("Books inserted\n")

    db.commit()

# If the table is empty, populate the author table
cursor.execute('SELECT COUNT(*) FROM author')
if cursor.fetchone()[0] == 0:
    author_data = [
        (1290, 'Charles Dickens', 'England'),
        (8937, 'J.K Rowling', 'England'),
        (2356, 'C.S Lewis', 'Ireland'),
        (6380, 'J.R.R Tolkien', 'South Africa'),
        (5620, 'Lewis Carroll', 'England')
    ]

    # Insert authors
    cursor.executemany('''
        INSERT INTO author (id, name, country)
        VALUES (?, ?, ?)
        ''', author_data)

    print("Authors inserted\n")

    db.commit()

# ----- Menu ------
while True:
    print("Menu:")
    print("1. Enter book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search books")
    print("5. View details of all books")
    print("0. Exit")

    option = input("\nEnter option: ")

    if option == "1":
        enter_book()
    elif option == "2":
        update_book()
    elif option == "3":
        delete_book()
    elif option == "4":
        search_books()
    elif option == "5":
        view_all_books()
    elif option == "0":
        print("Exiting program")
        break
    else:
        print("Invalid option. Please try again")

# Commit changes and close connection
db.commit()
db.close()
