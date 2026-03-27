import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.exceptions import abort

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ─── Dashboard ───────────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db_connection()

    sessions = conn.execute('''
        SELECT focusSessions.*, courses.courseName
        FROM focusSessions
        JOIN courses ON focusSessions.courseid = courses.courseid
        ORDER BY focusSessions.startTime DESC
        LIMIT 10
    ''').fetchall()

    stats = conn.execute('''
        SELECT
            COUNT(*) as total_sessions,
            COALESCE(SUM(duration), 0) as total_minutes,
            COALESCE(ROUND(AVG(duration)), 0) as avg_duration
        FROM focusSessions
    ''').fetchone()

    course_count = conn.execute('SELECT COUNT(*) as c FROM courses').fetchone()['c']
    courses = conn.execute('SELECT * FROM courses').fetchall()

    conn.close()

    return render_template('index.html',
        sessions=sessions,
        total_sessions=stats['total_sessions'],
        total_minutes=stats['total_minutes'],
        avg_duration=stats['avg_duration'],
        course_count=course_count,
        courses=courses
    )

# ─── Add Session ─────────────────────────────────────────────
@app.route('/add_session', methods=['GET', 'POST'])
def add_session():
    conn = get_db_connection()

    if request.method == 'POST':
        courseid = request.form['course']
        duration = request.form['duration']
        conn.execute(
            'INSERT INTO focusSessions (userid, courseid, duration) VALUES (?, ?, ?)',
            (1, courseid, duration)
        )
        conn.commit()
        conn.close()
        flash('Session logged successfully!', 'success')
        return redirect(url_for('index'))

    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return render_template('add_session.html', courses=courses)

# ─── Delete Session ───────────────────────────────────────────
@app.route('/delete_session/<int:id>')
def delete_session(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM focusSessions WHERE sessionid = ?', (id,))
    conn.commit()
    conn.close()
    flash('Session deleted.', 'success')
    return redirect(request.referrer or url_for('index'))

# ─── Session History ──────────────────────────────────────────
@app.route('/history')
def history():
    conn = get_db_connection()
    sessions = conn.execute('''
        SELECT focusSessions.*, courses.courseName
        FROM focusSessions
        JOIN courses ON focusSessions.courseid = courses.courseid
        ORDER BY focusSessions.startTime DESC
    ''').fetchall()
    conn.close()
    return render_template('history.html', sessions=sessions)

# ─── Courses ──────────────────────────────────────────────────
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    conn = get_db_connection()

    if request.method == 'POST':
        course_name = request.form['courseName'].strip()
        if course_name:
            conn.execute('INSERT INTO courses (courseName) VALUES (?)', (course_name,))
            conn.commit()
            flash(f'"{course_name}" added!', 'success')
        conn.close()
        return redirect(url_for('courses'))

    courses = conn.execute('''
        SELECT courses.*,
               COUNT(focusSessions.sessionid) as session_count
        FROM courses
        LEFT JOIN focusSessions ON courses.courseid = focusSessions.courseid
        GROUP BY courses.courseid
        ORDER BY courses.courseName
    ''').fetchall()
    conn.close()
    return render_template('courses.html', courses=courses)

# ─── Delete Course ────────────────────────────────────────────
@app.route('/delete_course/<int:id>')
def delete_course(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM focusSessions WHERE courseid = ?', (id,))
    conn.execute('DELETE FROM courses WHERE courseid = ?', (id,))
    conn.commit()
    conn.close()
    flash('Course deleted.', 'success')
    return redirect(url_for('courses'))

# ─── Edit Session ────────────────────────────────────────────
@app.route('/edit_session/<int:id>', methods=['GET', 'POST'])
def edit_session(id):
    conn = get_db_connection()

    if request.method == 'POST':
        duration = request.form['duration']
        courseid = request.form['course']
        conn.execute(
            'UPDATE focusSessions SET duration = ?, courseid = ? WHERE sessionid = ?',
            (duration, courseid, id)
        )
        conn.commit()
        conn.close()
        flash('Session updated successfully!', 'success')
        return redirect(url_for('history'))

    focus_session = conn.execute(
        '''SELECT focusSessions.*, courses.courseName
           FROM focusSessions
           JOIN courses ON focusSessions.courseid = courses.courseid
           WHERE sessionid = ?''', (id,)
    ).fetchone()

    if focus_session is None:
        conn.close()
        abort(404)

    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return render_template('edit_session.html', session=focus_session, courses=courses)

# ─── Report ───────────────────────────────────────────────────
@app.route('/report')
def report():
    conn = get_db_connection()

    courseid    = request.args.get('course')
    min_duration = request.args.get('min')
    max_duration = request.args.get('max')

    query = '''
        SELECT focusSessions.*, courses.courseName
        FROM focusSessions
        JOIN courses ON focusSessions.courseid = courses.courseid
        WHERE 1=1
    '''
    params = []

    if courseid:
        query += ' AND focusSessions.courseid = ?'
        params.append(courseid)
    if min_duration:
        query += ' AND duration >= ?'
        params.append(min_duration)
    if max_duration:
        query += ' AND duration <= ?'
        params.append(max_duration)

    query += ' ORDER BY focusSessions.startTime DESC'

    sessions = conn.execute(query, params).fetchall()
    courses  = conn.execute('SELECT * FROM courses').fetchall()

    # summary stats for filtered results
    total_mins = sum(int(s['duration']) for s in sessions)
    avg_dur    = round(total_mins / len(sessions)) if sessions else 0

    conn.close()
    return render_template('report.html',
        sessions=sessions,
        courses=courses,
        total_mins=total_mins,
        avg_dur=avg_dur,
        selected_course=courseid,
        min_duration=min_duration,
        max_duration=max_duration
    )

# ─── Auth ─────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, passw) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND passw = ?',
            (username, password)
        ).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['userid']
            return redirect('/')
        else:
            return "Invalid login"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)