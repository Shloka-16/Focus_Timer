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
cur.execute("INSERT INTO courses (userid, courseName) VALUES (?, ?)", (1, "CS 348"))

# Insert sessions
cur.execute("""
INSERT INTO focusSessions (userid, courseid, duration)
VALUES (?, ?, ?)
""", (1, 1, 25))

cur.execute("""
INSERT INTO focusSessions (userid, courseid, duration)
VALUES (?, ?, ?)
""", (1, 2, 50))

# Indexes
cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_courseid ON focusSessions(courseid)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_duration ON focusSessions(duration)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_starttime ON focusSessions(startTime)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")

connection.commit()
connection.close()