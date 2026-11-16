DROP DATABASE IF EXISTS libraryDB;
CREATE DATABASE libraryDB;
USE libraryDB;

CREATE TABLE Author(
    author_id INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    country VARCHAR(150) NOT NULL,
    image_url VARCHAR(500) NULL,
    CONSTRAINT PK_Author PRIMARY KEY (author_id)
);

CREATE TABLE Publisher(
    publisher_id INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    country VARCHAR(150) NOT NULL,
    CONSTRAINT PK_Publisher PRIMARY KEY (publisher_id)
);

CREATE TABLE Category(
    category_id INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    CONSTRAINT PK_Category PRIMARY KEY (category_id)
);

CREATE TABLE Book(
    book_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    publish_year INT NOT NULL,
    author_id INT NOT NULL,
    publisher_id INT NOT NULL,
    category_id INT NOT NULL,
    image_url VARCHAR(500) NULL,
    CONSTRAINT PK_Book PRIMARY KEY (book_id),
    CONSTRAINT FK_Book_author FOREIGN KEY (author_id) REFERENCES Author(author_id)
        ON DELETE CASCADE,
    CONSTRAINT FK_Book_publisher FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id),
    CONSTRAINT FK_Book_category FOREIGN KEY (category_id) REFERENCES Category(category_id),
    CONSTRAINT CK_Book_price CHECK (price > 0.0)
);

CREATE TABLE Member(
    member_id INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    join_date DATE NOT NULL,
    CONSTRAINT PK_Member PRIMARY KEY (member_id)
);

CREATE TABLE Loan(
    loan_id INT NOT NULL AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,   -- NULL while the book is still borrowed
    CONSTRAINT PK_Loan PRIMARY KEY (loan_id),
    CONSTRAINT FK_Loan_book FOREIGN KEY (book_id) REFERENCES Book(book_id)
        ON DELETE CASCADE,
    CONSTRAINT FK_Loan_member FOREIGN KEY (member_id) REFERENCES Member(member_id)
);
