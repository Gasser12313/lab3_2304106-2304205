
USE library;


INSERT INTO author (author_id, name, country, photo) VALUES
(1, 'Naguib Mahfouz',         'Egypt',          'seed_author_1.png'),
(2, 'Agatha Christie',        'United Kingdom', 'seed_author_2.png'),
(3, 'Gabriel Garcia Marquez', 'Colombia',       'seed_author_3.png'),
(4, 'Taha Hussein',           'Egypt',          'seed_author_4.png');


INSERT INTO book (book_id, title, price, author_id, cover) VALUES
(1, 'Palace Walk',                    120.00, 1, 'seed_book_1.png'),
(2, 'Sugar Street',                   110.00, 1, 'seed_book_2.png'),
(3, 'The Thief and the Dogs',          95.50, 1, 'seed_book_3.png'),
(4, 'Murder on the Orient Express',   150.00, 2, 'seed_book_4.png'),
(5, 'And Then There Were None',       140.00, 2, 'seed_book_5.png'),
(6, 'One Hundred Years of Solitude',  180.00, 3, 'seed_book_6.png'),
(7, 'Love in the Time of Cholera',    165.75, 3, 'seed_book_7.png'),
(8, 'The Days',                        99.00, 4, 'seed_book_8.png');
