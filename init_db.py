import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Insert user
cur.execute("INSERT INTO users (username, passw) VALUES (?, ?)", ("Shloka", "123"))

# Insert courses
cur.execute("INSERT INTO courses (userid, courseName) VALUES (?, ?)", (1, "CS 1"))
cur.execute("INSERT INTO courses (userid, courseName) VALUES (?, ?)", (1, "CS 2"))

# Insert sessions
cur.execute("""
INSERT INTO focusSessions (userid, courseid, duration)
VALUES (?, ?, ?)
""", (1, 1, 25))

cur.execute("""
INSERT INTO focusSessions (userid, courseid, duration)
VALUES (?, ?, ?)
""", (1, 2, 50))

connection.commit()
connection.close()