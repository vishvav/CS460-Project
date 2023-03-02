DROP DATABASE IF EXISTS photoshare;
CREATE DATABASE photoshare;
USE photoshare;


CREATE TABLE Users (
    user_id INT NOT NULL AUTO_INCREMENT,
    gender VARCHAR(6),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    hometown VARCHAR(255),
    fname VARCHAR(255) NOT NULL,
    lname VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE Albums (
  album_id INT AUTO_INCREMENT,
  album_name VARCHAR(255) NOT NULL,
  date_of_creation DATE, #changed
  user_id INT NOT NULL,
  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Pictures(
  photo_id INT AUTO_INCREMENT,
  user_id INT,
  caption VARCHAR(255),
  imgdata LONGBLOB,
  album_id INT NOT NULL,
  PRIMARY KEY (photo_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE Comments(
  comment_id INT NOT NULL AUTO_INCREMENT,
  comment TEXT NOT NULL,
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  photo_id INT NOT NULL,
  PRIMARY KEY (comment_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Pictures(photo_id) ON DELETE CASCADE

);

CREATE TABLE CommentedOn(
	comment_id INT,
	photo_id INT,
  PRIMARY KEY (comment_id, photo_id),
  FOREIGN KEY (comment_id) REFERENCES Comments(comment_id),
	FOREIGN KEY (photo_id) REFERENCES Pictures(photo_id)
);

CREATE TABLE Likes(
  user_id INT NOT NULL,
  photo_id INT NOT NULL,
  PRIMARY KEY (user_id, photo_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Pictures(photo_id) ON DELETE CASCADE
);


CREATE TABLE StoredIn(
	photo_id INT,
	album_id INT,
  PRIMARY KEY (photo_id, album_id),
  FOREIGN KEY (photo_id) REFERENCES Pictures(photo_id),
	FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);

CREATE TABLE Tags(
  tag_id INT NOT NULL,
  tag VARCHAR(255),
  PRIMARY KEY (tag_id)
);

CREATE TABLE TaggedPhotos(
  count INT AUTO_INCREMENT,
  photo_id INT,
  tag_id INT,
  PRIMARY KEY (count),
  FOREIGN KEY (photo_id) REFERENCES Pictures(photo_id),
  FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
);

CREATE TABLE Friends(
  user_id1 INT NOT NULL,
  user_id2 INT NOT NULL,
  CHECK (user_id1 <> user_id2),
  PRIMARY KEY (user_id1, user_id2),
  FOREIGN KEY (user_id1) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id2) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password, dob, fname, lname) VALUES ('test@bu.edu', 'test', '1998-01-01', 'test', 'test');
INSERT INTO Users (email, password, dob, fname, lname) VALUES ('test1@bu.edu', 'test', '1998-01-01', 'test1', 'test1');
