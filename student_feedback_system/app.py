from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the SQLite database
def init_db():
    if not os.path.exists('feedback.db'):
        conn = sqlite3.connect('feedback.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                course TEXT,
                rating INTEGER,
                comments TEXT
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        rating = request.form['rating']
        comments = request.form['comments']

        conn = sqlite3.connect('feedback.db')
        c = conn.cursor()
        c.execute('INSERT INTO feedback (name, course, rating, comments) VALUES (?, ?, ?, ?)',
                  (name, course, rating, comments))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))

    return render_template('feedback.html')

@app.route('/thankyou')
def thank_you():
    return render_template("thankyou.html")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        flash("You must be logged in as admin", "danger")
        return redirect(url_for('admin'))

    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('SELECT * FROM feedback')
    data = c.fetchall()
    conn.close()
    return render_template('dashboard.html', feedbacks=data)

@app.route('/delete/<int:id>')
def delete_feedback(id):
    if not session.get('admin'):
        flash("Access denied. Login as admin.", "danger")
        return redirect(url_for('admin'))

    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('DELETE FROM feedback WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
