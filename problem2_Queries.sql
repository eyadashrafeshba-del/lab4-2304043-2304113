USE libraryDB;

-- F2.1
SELECT book_id, title, price
FROM Book
WHERE title LIKE '%soft%' AND price BETWEEN 15 AND 300 AND category_id = 1
ORDER BY price ASC;

-- F2.2
SELECT b.book_id, b.title, b.price, a.name AS author, p.name AS publisher, c.name AS category
FROM Book b
JOIN Author a ON b.author_id = a.author_id
JOIN Publisher p ON b.publisher_id = p.publisher_id
JOIN Category c ON b.category_id = c.category_id
ORDER BY b.book_id;

-- F2.3a
SELECT c.name AS category, COUNT(*) AS books, AVG(b.price) AS average_price
FROM Category c JOIN Book b ON b.category_id = c.category_id
GROUP BY c.category_id, c.name;

-- F2.3b
SELECT a.name AS author, COUNT(*) AS books
FROM Author a JOIN Book b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(*) >= 2;

-- F2.3c
SELECT SUM(price) AS total_price, MIN(price) AS cheapest, MAX(price) AS most_expensive
FROM Book;

-- F2.4a
SELECT l.loan_id, b.title AS book, m.name AS member, l.loan_date
FROM Loan l
JOIN Book b ON l.book_id = b.book_id
JOIN Member m ON l.member_id = m.member_id
WHERE l.return_date IS NULL;

-- F2.4b
SELECT m.member_id, m.name
FROM Member m LEFT JOIN Loan l ON l.member_id = m.member_id
WHERE l.loan_id IS NULL;

-- F2.4c
SELECT b.book_id, b.title
FROM Book b LEFT JOIN Loan l ON l.book_id = b.book_id
WHERE l.loan_id IS NULL;

-- F2.5
SELECT b.title, COUNT(*) AS loans
FROM Book b JOIN Loan l ON l.book_id = b.book_id
GROUP BY b.book_id, b.title
ORDER BY loans DESC
LIMIT 3;

-- F2.5
SELECT m.name, COUNT(*) AS loans
FROM Member m JOIN Loan l ON l.member_id = m.member_id
GROUP BY m.member_id, m.name
ORDER BY loans DESC
LIMIT 1;

-- F2.6
SELECT a.name AS author, COUNT(b.book_id) AS books
FROM Author a LEFT JOIN Book b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name;

-- F2.6
SELECT b.title, a.name AS author, p.name AS publisher, a.country
FROM Book b
JOIN Author a ON b.author_id = a.author_id
JOIN Publisher p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country;
