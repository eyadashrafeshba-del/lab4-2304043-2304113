# 📚 Library Website — Lab 4

**Introduction to Database Systems · Alexandria National University · Fall 2026**

A small library website built with **Flask** and **MySQL**. It manages **authors**, **publishers**, **categories**, **books**, **members** and **loans**, and it adds **search pages** that run SQL queries (WHERE, JOIN, GROUP BY, HAVING, LEFT JOIN, ORDER BY, LIMIT). The Lab 3 pages (add / edit / remove books and authors, image upload) still work.

---



| ID    | Page | URL | SQL used |
|-------|------|-----|----------|
| F2.1  | Search books: title keyword, min / max price, category; cheapest first | `/search` | `WHERE`, `LIKE`, `BETWEEN`, `ORDER BY` |
| F2.2  | Catalogue: author, publisher and category names instead of ids | `/catalogue` | `JOIN` (3 joins) |
| F2.3  | Reports: books and average price per category, authors with at least 2 books, total / smallest / largest price | `/reports` | `GROUP BY`, `HAVING`, aggregates |
| F2.4  | Loans: loans not returned yet, members who never borrowed, books never borrowed | `/loans` | `JOIN`, `LEFT JOIN ... IS NULL` |
| F2.5  | Most borrowed: top 3 books and the member with the most loans | `/most-borrowed` | `GROUP BY`, `ORDER BY`, `LIMIT` |
| F2.6  | Authors and books: number of books per author (including 0), books whose author and publisher are from the same country | `/authors-books` | `LEFT JOIN`, `JOIN` |
| Bonus | The search form of F2.1 uses **prepared statements** (`%s` placeholders), never the raw text typed by the user | `/search` | |

Lab 3 pages: `/books`, `/authors`, add / edit / remove a book or an author (removing an author deletes his or her books with `ON DELETE CASCADE`), cover and photo upload.

---

## 🗂️ Project structure

```
lab4-2304043-2304113/
├── problem1_DDL.sql        # Problem 1: COMPANY database (5 tables, keys)
├── problem1_DML.sql        # Problem 1: INSERT statements
├── problem1_Answers.txt    # Problem 1: SQL + output/error for Q1.1–Q1.12
├── problem2_DDL.sql        # Problem 2: libraryDB database (6 tables)
├── problem2_DML.sql        # Problem 2: seed data
├── problem2_Queries.sql    # Problem 2: SQL of the pages F2.1–F2.6
├── README.md
└── website/
    ├── app.py              # Flask routes
    ├── db.py               # MySQL connection helpers
    ├── requirements.txt
    ├── .env.example        # copy to .env and fill in your password
    ├── templates/          # HTML pages (Jinja2)
    └── static/             # style.css and uploaded images
```

---

## 🗄️ Database schema (Problem 2)

```
Author    (author_id, name, country, image_url)
Publisher (publisher_id, name, country)
Category  (category_id, name)
Book      (book_id, title, price, publish_year, author_id, publisher_id, category_id, image_url)
Member    (member_id, name, email, join_date)
Loan      (loan_id, book_id, member_id, loan_date, return_date)
```

- `Book.author_id`, `Book.publisher_id` and `Book.category_id` are **foreign keys** to `Author`, `Publisher` and `Category`.
- `Loan.book_id` → `Book.book_id` and `Loan.member_id` → `Member.member_id`.
- **`ON DELETE CASCADE`**: deleting an author deletes his or her books, and deleting a book deletes its loans.
- `return_date` is `NULL` while the book is still borrowed.
- `image_url` stores the **file name** of the uploaded image (files live in `website/static/uploads/`).

**Seed data:** 4 authors, 3 publishers, 3 categories, 10 books, 5 members and 12 loans. It contains two authors from the same country, an author with no books, an author with at least 2 books, an author and a publisher from the same country, a book priced between 15 and 20, books that were never borrowed, a member with no loans and loans that are not returned yet.

---

## ⚙️ Requirements

- **Python 3.9+**
- **MySQL Server 8.0+** and the `mysql` command-line client
- `pip` (comes with Python)

---

## 🚀 How to run (step by step)

### 1. Clone the repository
```bash
git clone <repository-url>
cd lab4-2304043-2304113
```

### 2. Build the databases
Each DDL script drops and recreates its database, so you can re-run it at any time.

```bash
# Problem 1 (COMPANY database)
mysql -u root -p < problem1_DDL.sql
mysql -u root -p < problem1_DML.sql

# Problem 2 (libraryDB database, used by the website)
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql
```

To run the queries of the pages by hand:
```bash
mysql -u root -p < problem2_Queries.sql
```

To check the data by hand:
```bash
mysql -u root -p libraryDB
mysql> SELECT * FROM Book;
mysql> SELECT * FROM Loan;
```

### 3. Configure the connection
```bash
cd website
cp .env.example .env        # on Windows: copy .env.example .env
```
Open `.env` and write your MySQL password:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=libraryDB
SECRET_KEY=change-me
```

### 4. Install the dependencies
```bash
python -m venv venv
source venv/bin/activate    # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Check the connection (optional but recommended)
```bash
python db.py
```
It prints whether `.env` was found, whether the MySQL login works, and whether the `libraryDB` tables exist.

### 6. Start the website
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Quick test

1. Open **Search**, type `soft` as the keyword, choose the category *Technology*: you should see the software books, cheapest first.
2. Open **Catalogue**: every book shows the author, publisher and category names.
3. Open **Reports**: 3 categories, authors with 2 or more books, and the total / smallest / largest price.
4. Open **Loans**: 2 loans are not returned yet, *Karim* never borrowed, and 2 books were never borrowed.
5. Open **Most borrowed** and **Authors & books**: *Sara Hassan* appears with 0 books.
6. Add a book (the form asks for year, author, publisher and category), edit it, then remove it.
7. Remove an author: his or her books disappear from the Books page as well.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `Access denied for user 'root'` | Run `python db.py`. The `.env` file must be inside `website/` (next to `db.py`), named exactly `.env`, and contain your MySQL password. Restart `python app.py` after editing it. |
| `Unknown database 'libraryDB'` | Run `problem2_DDL.sql` first. |
| `Unknown column 'publish_year'` | You still have the Lab 3 database. Re-run `problem2_DDL.sql` and `problem2_DML.sql`. |
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt`. |
| `Can't connect to MySQL server` | Make sure the MySQL service is running. |
| Port 5000 already in use | Stop the other program, or change the port in the last line of `app.py`. |

---

## 👤 Authors

| Name | Student ID |
|------|-----------|
| Ezz Eldeen Gamal | 2304043 |
| Eyad Ashrf | 2304113 |
