# DBMS
# Expense Tracker (Python + SQLite)

A very simple console-based Expense Tracker built using Python and SQLite.  
This project is suitable for DBMS practicals and includes SQL queries such as:

- CREATE TABLE
- INSERT
- SELECT
- JOIN
- GROUP BY
- HAVING
- UPDATE
- DELETE
- FOREIGN KEY relations

---

## 📌 Features
- Add categories (Food, Travel, Rent, etc.)
- Add expenses
- View all expenses with category names (JOIN)
- View expenses between two dates (BETWEEN)
- View category-wise totals (GROUP BY + HAVING)
- Update expense amount
- Delete expenses
- SQLite database stored in `expenses.db`

---

## 📁 Database Details

### **Tables Used**
#### 1. `categories`
| Field | Type | Description |
|-------|-------|-------------|
| id | INTEGER (PK) | Unique ID |
| name | TEXT | Category name |

#### 2. `expenses`
| Field | Type | Description |
|-------|-------|-------------|
| id | INTEGER (PK) | Expense ID |
| date | TEXT | Stored as YYYY-MM-DD |
| category_id | INTEGER (FK) | Linked to categories.id |
| description | TEXT | Optional |
| amount | REAL | Expense amount |

---

## 🚀 How to Run

1. Install Python 3
2. Place the project file: main.py
3. Run the program:
```bash
python main.py
```
