USE libraryDB;

-- authors 1 and 4 are both from Egypt; author 4 has no books
INSERT INTO Author(`name`, country) VALUES
('Ezz Gamal', 'Egypt'),
('Ahmed Ali', 'UAE'),
('Mike Tyson', 'USA'),
('Sara Hassan', 'Egypt');

-- Nile Press (Egypt) has the same country as Ezz Gamal
INSERT INTO Publisher(`name`, country) VALUES
('Nile Press', 'Egypt'),
('Gulf Books', 'UAE'),
('Star Publishing', 'USA');

INSERT INTO Category(`name`) VALUES
('Technology'), ('Business'), ('Sports');

INSERT INTO Book(title, price, publish_year, author_id, publisher_id, category_id) VALUES
('SOFTWARE IN BRIEF',              125.22, 2018, 1, 1, 1),
('How to become rich in 60 Days',   67.99, 2020, 2, 2, 2),
('Boxing Life',                    150.57, 2015, 3, 3, 3),
('ADVANCED SOFTWARE OOD',          299.70, 2021, 1, 2, 1),
('My Life in France',               60.99, 2019, 2, 1, 2),
('MMA Fighter Story',               99.99, 2022, 3, 3, 3),
('SQL Basics',                      17.50, 2023, 1, 1, 1),  -- price between 15 and 20
('Startup Notes',                   45.00, 2017, 2, 2, 2),
('Training Guide',                  80.00, 2016, 3, 3, 3),  -- never borrowed
('Data Structures',                 35.00, 2024, 1, 1, 1);  -- never borrowed

-- member 5 (Karim) has no loans
INSERT INTO Member(`name`, email, join_date) VALUES
('Omar',    'omar@mail.com',  '2026-01-10'),
('Mona',    'mona@mail.com',  '2026-02-11'),
('Youssef', 'youssef@mail.com','2026-03-12'),
('Laila',   'laila@mail.com', '2026-04-13'),
('Karim',   'karim@mail.com', '2026-05-14');

-- loans 9 and 11 are not returned yet (return_date NULL)
INSERT INTO Loan(book_id, member_id, loan_date, return_date) VALUES
(1, 1, '2026-09-01', '2026-09-10'),
(1, 2, '2026-09-05', '2026-09-15'),
(1, 3, '2026-09-20', '2026-09-28'),
(2, 1, '2026-09-02', '2026-09-12'),
(2, 4, '2026-09-08', '2026-09-18'),
(3, 2, '2026-09-10', '2026-09-20'),
(3, 4, '2026-10-01', '2026-10-09'),
(4, 3, '2026-10-03', '2026-10-11'),
(5, 1, '2026-10-05', NULL),
(6, 2, '2026-10-07', '2026-10-17'),
(7, 3, '2026-10-10', NULL),
(8, 1, '2026-10-12', '2026-10-20');
