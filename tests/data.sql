INSERT INTO user (username,password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
('other','pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO book (title,author,isbn,publisher,year,edition,genre,series,volume,description,permalink,ndl_image_url)
VALUES
('入門Python 3','Lubanovic, Bill','9784873119328','オライリー・ジャパン',Null,'第2版',Null,'','',Null,'https://iss.ndl.go.jp/books/R100000074-I000721538-00',Null),
('初めてのPython','Lutz, Mark','9784873113937','オライリー・ジャパン',Null,'',Null,'','',Null,'https://iss.ndl.go.jp/books/R100000096-I006692207-00',Null);

INSERT INTO record (user_id,book_id,status,comment,rating,record_at)
VALUES
(1,1,'read','test comment',5,'2022-01-01 00:00:00');