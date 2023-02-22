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
  Name VARCHAR(255) NOT NULL,
  date_of_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Pictures(
  picture_id INT AUTO_INCREMENT,
  user_id INT,
  caption VARCHAR(255),
  imgdata LONGBLOB,
  album_id INT NOT NULL,
  PRIMARY KEY (picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE Comments(
  comment_od INT NOT NULL AUTO_INCREMENT,
  text TEXT NOT NULL,
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  picture_id INT NOT NULL,
  PRIMARY KEY (comment_od),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE

);

CREATE TABLE Likes(
  user_id INT NOT NULL,
  picture_id INT NOT NULL,
  PRIMARY KEY (user_id, picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Tags(
  tag_id INT NOT NULL,
  name VARCHAR(255),
  PRIMARY KEY (tag_id)
);

CREATE TABLE Tagged(
  photo_id INT,
  tag_id INT,
  PRIMARY KEY (photo_id, tag_id),
  FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id),
  FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
);

CREATE TABLE Friendship(
  UID1 INT NOT NULL,
  UID2 INT NOT NULL,
  CHECK (UID1 <> UID2),
  PRIMARY KEY (UID1, UID2),
  FOREIGN KEY (UID1) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (UID2) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password, dob, fname, lname) VALUES ('test@bu.edu', 'test', '1998-01-01', 'test', 'test');
INSERT INTO Users (email, password, dob, fname, lname) VALUES ('test1@bu.edu', 'test', '1998-01-01', 'test1', 'test1');
