import sqlite3
from datetime import datetime

DB_NAME = "expenses.db"

#  DB CONNECTION 
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # access columns by name
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

#  CREATE TABLES 
def init_db():
    conn = get_connection()

    # CREATE TABLE categories
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    """)

    # CREATE TABLE expenses with FOREIGN KEY
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

#  CATEGORY FUNCTIONS 
def add_category():
    name = input("Enter new category name: ").strip()
    if not name:
        print("Category name cannot be empty.")
        return

    conn = get_connection()
    try:
        # INSERT into categories
        conn.execute("INSERT INTO categories (name) VALUES (?);", (name,))
        conn.commit()
        print(f"✔ Category '{name}' added.")
    except sqlite3.IntegrityError:
        print("Category already exists.")
    finally:
        conn.close()

def view_categories():
    conn = get_connection()
    cur = conn.cursor()

    # SELECT with ORDER BY
    cur.execute("SELECT id, name FROM categories ORDER BY name;")
    rows = cur.fetchall()

    if not rows:
        print("\n(No categories found. Add some first.)")
    else:
        print("\n--- CATEGORIES ---")
        for row in rows:
            print(f"{row['id']}: {row['name']}")

    conn.close()

#  EXPENSE FUNCTIONS 
def add_expense():
    date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Validate date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    print("\nChoose category by ID:")
    view_categories()
    cat_id_str = input("Enter category ID: ").strip()
    if not cat_id_str.isdigit():
        print("Invalid category ID.")
        return
    category_id = int(cat_id_str)

    description = input("Enter description: ").strip()
    amount_str = input("Enter amount: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # Check if category exists (SELECT with WHERE)
    cur.execute("SELECT id FROM categories WHERE id = ?;", (category_id,))
    if cur.fetchone() is None:
        print("Category ID not found.")
        conn.close()
        return

    # INSERT into expenses
    conn.execute(
        "INSERT INTO expenses (date, category_id, description, amount) VALUES (?, ?, ?, ?);",
        (date_str, category_id, description, amount)
    )
    conn.commit()
    conn.close()
    print("✔ Expense added.\n")

def view_all_expenses():
    conn = get_connection()
    cur = conn.cursor()

    # SELECT with INNER JOIN and ORDER BY
    cur.execute("""
        SELECT e.id, e.date, c.name AS category, e.description, e.amount
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC, e.id DESC;
    """)
    rows = cur.fetchall()

    if not rows:
        print("\n(No expenses recorded.)\n")
    else:
        print("\n---- ALL EXPENSES (JOIN) ----")
        for row in rows:
            print(f"ID: {row['id']}")
            print(f"Date: {row['date']}")
            print(f"Category: {row['category']}")
            print(f"Description: {row['description']}")
            print(f"Amount: ₹{row['amount']:.2f}")
            print("------------")

    # Aggregate: SUM()
    cur.execute("SELECT SUM(amount) AS total FROM expenses;")
    total = cur.fetchone()["total"]
    print(f"TOTAL SPENT: ₹{total if total else 0:.2f}\n")

    conn.close()

def view_expenses_date_range():
    start = input("Enter start date (YYYY-MM-DD): ").strip()
    end = input("Enter end date (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # SELECT + JOIN + BETWEEN
    cur.execute("""
        SELECT e.id, e.date, c.name AS category, e.description, e.amount
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.date BETWEEN ? AND ?
        ORDER BY e.date;
    """, (start, end))

    rows = cur.fetchall()
    if not rows:
        print("\n(No expenses in this date range.)\n")
    else:
        print("\n---- EXPENSES BETWEEN DATES (BETWEEN + JOIN) ----")
        for row in rows:
            print(f"{row['date']} | {row['category']} | ₹{row['amount']:.2f} | {row['description']}")

    conn.close()

def view_total_per_category():
    conn = get_connection()
    cur = conn.cursor()

    # GROUP BY + HAVING
    cur.execute("""
        SELECT c.name AS category, SUM(e.amount) AS total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        GROUP BY c.name
        HAVING SUM(e.amount) > 0
        ORDER BY total DESC;
    """)

    rows = cur.fetchall()
    if not rows:
        print("\n(No expenses to summarize.)\n")
    else:
        print("\n---- TOTAL PER CATEGORY (GROUP BY + HAVING) ----")
        for row in rows:
            print(f"{row['category']}: ₹{row['total']:.2f}")

    conn.close()

def update_expense_amount():
    exp_id = input("Enter expense ID to update: ").strip()
    if not exp_id.isdigit():
        print("Invalid ID.")
        return

    new_amount_str = input("Enter new amount: ").strip()
    try:
        new_amount = float(new_amount_str)
    except ValueError:
        print("Invalid amount.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # UPDATE query
    cur.execute("UPDATE expenses SET amount = ? WHERE id = ?;", (new_amount, exp_id))
    conn.commit()

    if cur.rowcount == 0:
        print("No expense found with that ID.")
    else:
        print("✔ Expense updated.")

    conn.close()

def delete_expense():
    exp_id = input("Enter expense ID to delete: ").strip()
    if not exp_id.isdigit():
        print("Invalid ID.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # DELETE query
    cur.execute("DELETE FROM expenses WHERE id = ?;", (exp_id,))
    conn.commit()

    if cur.rowcount == 0:
        print("No expense found with that ID.")
    else:
        print("✔ Expense deleted.")

    conn.close()

#  MENU 
def menu():
    init_db()

    while True:
        print("\n===== EXPENSE TRACKER  =====")
        print("1. Add Category")
        print("2. View Categories")
        print("3. Add Expense")
        print("4. View All Expenses (JOIN)")
        print("5. View Expenses Between Dates (BETWEEN)")
        print("6. View Total per Category (GROUP BY)")
        print("7. Update Expense Amount (UPDATE)")
        print("8. Delete Expense (DELETE)")
        print("9. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_category()
        elif choice == "2":
            view_categories()
        elif choice == "3":
            add_expense()
        elif choice == "4":
            view_all_expenses()
        elif choice == "5":
            view_expenses_date_range()
        elif choice == "6":
            view_total_per_category()
        elif choice == "7":
            update_expense_amount()
        elif choice == "8":
            delete_expense()
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

#  MAIN 
if __name__ == "__main__":
    menu()
