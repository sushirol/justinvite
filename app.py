import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import sql
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Initialize database
def init_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS invites (
            id SERIAL PRIMARY KEY,
            user_email TEXT,
            guest_email TEXT,
            status TEXT,
            adults INTEGER,
            kids INTEGER
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Send email function (same as before)
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = to_email

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.login('your_email@example.com', 'your_password')
        server.sendmail('your_email@example.com', [to_email], msg.as_string())

# Routes (same as before)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['invite_card']
        file.save(f'static/{file.filename}')
        return redirect(url_for('send_invites'))
    return render_template('upload.html')

@app.route('/send_invites', methods=['GET', 'POST'])
def send_invites():
    if request.method == 'POST':
        guest_emails = request.form.get('guest_emails').split(',')
        for email in guest_emails:
            send_email(email.strip(), 'You are invited!', 'Please respond here: [SHORT_URL]')
        return redirect(url_for('dashboard'))
    return render_template('send_invites.html')

@app.route('/dashboard')
def dashboard():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute('SELECT * FROM invites')
    invites = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('dashboard.html', invites=invites)

if __name__ == '__main__':
    app.run(debug=True)
