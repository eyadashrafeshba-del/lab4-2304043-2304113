import os
import uuid
from decimal import Decimal, InvalidOperation

from flask import (Flask, flash, redirect, render_template, request,
                   url_for)
from pymysql import MySQLError
from werkzeug.utils import secure_filename

import db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB uploads

UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------- helpers ----------
def save_image(field):
    """Save an uploaded image. Returns the stored file name or None."""
    f = request.files.get(field)
    if not f or not f.filename:
        return None
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED:
        flash("Image must be png, jpg, jpeg, gif or webp.", "error")
        return None
    name = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_DIR, name))
    return name


def remove_image(name):
    if name:
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(path):
            os.remove(path)


def parse_price(text):
    try:
        price = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        return None
    return price if price > 0 else None


def parse_num(text, default):
    """Optional number: blank -> default, invalid -> None."""
    text = (text or "").strip()
    if not text:
        return default
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def lookups():
    """Lists used by the book form (author / publisher / category selects)."""
    return dict(
        authors=db.query("SELECT author_id, name FROM Author ORDER BY name"),
        publishers=db.query("SELECT publisher_id, name FROM Publisher ORDER BY name"),
        categories=db.query("SELECT category_id, name FROM Category ORDER BY name"),
    )


def read_book_form():
    """Return (title, price, year, author_id, publisher_id, category_id) or None."""
    f = request.form
    title = f.get("title", "").strip()
    price = parse_price(f.get("price", ""))
    year = f.get("publish_year", "").strip()
    ids = [f.get(k, "") for k in ("author_id", "publisher_id", "category_id")]
    if not title or price is None or not year.isdigit() or not all(i.isdigit() for i in ids):
        return None
    return (title, price, int(year), *[int(i) for i in ids])


def page(title, *sections):
    """Render one or more (heading, sql) queries as tables."""
    data = [(heading, db.query(sql)) for heading, sql in sections]
    return render_template("report.html", title=title, sections=data)


# ---------- home ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- Lab 3 pages: show / add / edit / remove ----------
@app.route("/books")
def books():
    rows = db.query("SELECT * FROM Book ORDER BY book_id")
    return render_template("books.html", books=rows)


@app.route("/authors")
def authors():
    rows = db.query("SELECT * FROM Author ORDER BY author_id")
    return render_template("authors.html", authors=rows)


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        data = read_book_form()
        if data is None:
            flash("Title, price, year, author, publisher and category are required.", "error")
            return render_template("book_form.html", book=request.form,
                                   mode="Add", **lookups())
        cover = save_image("cover")
        try:
            db.execute(
                "INSERT INTO Book (title, price, publish_year, author_id, "
                "publisher_id, category_id, image_url) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)", (*data, cover))
        except MySQLError as e:
            remove_image(cover)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("book_form.html", book=request.form,
                                   mode="Add", **lookups())
        flash("Book added.", "ok")
        return redirect(url_for("books"))
    return render_template("book_form.html", book={}, mode="Add", **lookups())


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = db.query("SELECT * FROM Book WHERE book_id = %s", (book_id,), one=True)
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("books"))
    if request.method == "POST":
        data = read_book_form()
        if data is None:
            flash("Title, price, year, author, publisher and category are required.", "error")
            return render_template("book_form.html", book={**book, **request.form},
                                   mode="Edit", **lookups())
        cover = save_image("cover")
        try:
            if cover:
                db.execute(
                    "UPDATE Book SET title=%s, price=%s, publish_year=%s, author_id=%s, "
                    "publisher_id=%s, category_id=%s, image_url=%s WHERE book_id=%s",
                    (*data, cover, book_id))
                remove_image(book["image_url"])
            else:
                db.execute(
                    "UPDATE Book SET title=%s, price=%s, publish_year=%s, author_id=%s, "
                    "publisher_id=%s, category_id=%s WHERE book_id=%s",
                    (*data, book_id))
        except MySQLError as e:
            remove_image(cover)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("book_form.html", book={**book, **request.form},
                                   mode="Edit", **lookups())
        flash("Book updated.", "ok")
        return redirect(url_for("books"))
    return render_template("book_form.html", book=book, mode="Edit", **lookups())


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.query("SELECT image_url FROM Book WHERE book_id = %s", (book_id,), one=True)
    if book:
        try:
            db.execute("DELETE FROM Book WHERE book_id = %s", (book_id,))
        except MySQLError as e:
            flash(f"Database error: {e.args[-1]}", "error")
            return redirect(url_for("books"))
        remove_image(book["image_url"])
        flash("Book removed.", "ok")
    return redirect(url_for("books"))


@app.route("/authors/add", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        if not name or not country:
            flash("Author name and country are required.", "error")
            return render_template("author_form.html", author=request.form, mode="Add")
        photo = save_image("photo")
        try:
            db.execute("INSERT INTO Author (name, country, image_url) "
                       "VALUES (%s, %s, %s)", (name, country, photo))
        except MySQLError as e:
            remove_image(photo)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("author_form.html", author=request.form, mode="Add")
        flash("Author added.", "ok")
        return redirect(url_for("authors"))
    return render_template("author_form.html", author={}, mode="Add")


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    author = db.query("SELECT * FROM Author WHERE author_id = %s", (author_id,), one=True)
    if not author:
        flash("Author not found.", "error")
        return redirect(url_for("authors"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        if not name or not country:
            flash("Author name and country are required.", "error")
            return render_template("author_form.html",
                                   author={**author, **request.form}, mode="Edit")
        photo = save_image("photo")
        try:
            if photo:
                db.execute("UPDATE Author SET name=%s, country=%s, image_url=%s "
                           "WHERE author_id=%s", (name, country, photo, author_id))
                remove_image(author["image_url"])
            else:
                db.execute("UPDATE Author SET name=%s, country=%s "
                           "WHERE author_id=%s", (name, country, author_id))
        except MySQLError as e:
            remove_image(photo)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("author_form.html",
                                   author={**author, **request.form}, mode="Edit")
        flash("Author updated.", "ok")
        return redirect(url_for("authors"))
    return render_template("author_form.html", author=author, mode="Edit")


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = db.query("SELECT image_url FROM Author WHERE author_id = %s", (author_id,),
                      one=True)
    if author:
        covers = db.query("SELECT image_url FROM Book WHERE author_id = %s", (author_id,))
        try:
            db.execute("DELETE FROM Author WHERE author_id = %s", (author_id,))
        except MySQLError as e:
            flash(f"Database error: {e.args[-1]}", "error")
            return redirect(url_for("authors"))
        remove_image(author["image_url"])
        for c in covers:
            remove_image(c["image_url"])
        flash("Author and all of their books removed.", "ok")
    return redirect(url_for("authors"))


# =====================  LAB 4 PAGES  =====================

# ---------- F2.1 Search books (WHERE, LIKE, BETWEEN) + prepared statement (bonus) ----------
@app.route("/search")
def search():
    cats = db.query("SELECT category_id, name FROM Category ORDER BY name")
    rows = None
    if request.args:
        keyword = request.args.get("keyword", "").strip()
        low = parse_num(request.args.get("min_price"), Decimal("0"))
        high = parse_num(request.args.get("max_price"), Decimal("99999999.99"))
        cat = request.args.get("category_id", "")
        if low is None or high is None:
            flash("Minimum and maximum price must be numbers.", "error")
        else:
            sql = ("SELECT book_id, title, price FROM Book "
                   "WHERE title LIKE %s AND price BETWEEN %s AND %s")
            args = [f"%{keyword}%", low, high]
            if cat.isdigit():
                sql += " AND category_id = %s"
                args.append(int(cat))
            sql += " ORDER BY price ASC"
            rows = db.query(sql, args)   # placeholders: no SQL injection
    return render_template("search.html", categories=cats, rows=rows,
                           form=request.args)


# ---------- F2.2 Catalogue (JOIN) ----------
@app.route("/catalogue")
def catalogue():
    return page("Catalogue", ("All books", """
        SELECT b.book_id, b.title, b.price, a.name AS author,
               p.name AS publisher, c.name AS category
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        JOIN Publisher p ON b.publisher_id = p.publisher_id
        JOIN Category c ON b.category_id = c.category_id
        ORDER BY b.book_id"""))


# ---------- F2.3 Reports (GROUP BY, HAVING) ----------
@app.route("/reports")
def reports():
    return page(
        "Reports",
        ("Books and average price of each category", """
            SELECT c.name AS category, COUNT(*) AS books, AVG(b.price) AS average_price
            FROM Category c JOIN Book b ON b.category_id = c.category_id
            GROUP BY c.category_id, c.name"""),
        ("Authors who wrote at least 2 books", """
            SELECT a.name AS author, COUNT(*) AS books
            FROM Author a JOIN Book b ON b.author_id = a.author_id
            GROUP BY a.author_id, a.name
            HAVING COUNT(*) >= 2"""),
        ("Total, smallest and largest price of the library", """
            SELECT SUM(price) AS total_price, MIN(price) AS cheapest,
                   MAX(price) AS most_expensive
            FROM Book"""),
    )


# ---------- F2.4 Loans (JOIN, LEFT JOIN) ----------
@app.route("/loans")
def loans():
    return page(
        "Loans",
        ("Loans not returned yet", """
            SELECT l.loan_id, b.title AS book, m.name AS member, l.loan_date
            FROM Loan l
            JOIN Book b ON l.book_id = b.book_id
            JOIN Member m ON l.member_id = m.member_id
            WHERE l.return_date IS NULL"""),
        ("Members who never borrowed a book", """
            SELECT m.member_id, m.name
            FROM Member m LEFT JOIN Loan l ON l.member_id = m.member_id
            WHERE l.loan_id IS NULL"""),
        ("Books that were never borrowed", """
            SELECT b.book_id, b.title
            FROM Book b LEFT JOIN Loan l ON l.book_id = b.book_id
            WHERE l.loan_id IS NULL"""),
    )


# ---------- F2.5 Most borrowed (GROUP BY, ORDER BY, LIMIT) ----------
@app.route("/most-borrowed")
def most_borrowed():
    return page(
        "Most borrowed",
        ("The 3 books with the most loans", """
            SELECT b.title, COUNT(*) AS loans
            FROM Book b JOIN Loan l ON l.book_id = b.book_id
            GROUP BY b.book_id, b.title
            ORDER BY loans DESC
            LIMIT 3"""),
        ("The member with the most loans", """
            SELECT m.name, COUNT(*) AS loans
            FROM Member m JOIN Loan l ON l.member_id = m.member_id
            GROUP BY m.member_id, m.name
            ORDER BY loans DESC
            LIMIT 1"""),
    )


# ---------- F2.6 Authors and books (LEFT JOIN, JOIN) ----------
@app.route("/authors-books")
def authors_books():
    return page(
        "Authors and books",
        ("Every author with the number of books (including 0)", """
            SELECT a.name AS author, COUNT(b.book_id) AS books
            FROM Author a LEFT JOIN Book b ON b.author_id = a.author_id
            GROUP BY a.author_id, a.name"""),
        ("Books whose author and publisher are from the same country", """
            SELECT b.title, a.name AS author, p.name AS publisher, a.country
            FROM Book b
            JOIN Author a ON b.author_id = a.author_id
            JOIN Publisher p ON b.publisher_id = p.publisher_id
            WHERE a.country = p.country"""),
    )


@app.errorhandler(413)
def too_big(_):
    flash("Image is too large (max 5 MB).", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
