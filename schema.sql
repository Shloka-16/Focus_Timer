
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS focusSessions;
DROP TABLE IF EXISTS courses;


CREATE TABLE users (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    passw TEXT NOT NULL
);

CREATE TABLE focusSessions (
    sessionid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL, 
    courseid INTEGER NOT NULL, 
    startTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER NOT NULL, 
    FOREIGN KEY (userid) REFERENCES users (userid), 
    FOREIGN KEY (courseid) REFERENCES courses (courseid)

);

CREATE TABLE courses (
    courseid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL,
    courseName TEXT NOT NULL, 
    FOREIGN KEY (userid) REFERENCES users (userid)
);
