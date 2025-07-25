from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'database/stock.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                action TEXT,
                item TEXT,
                qty INTEGER,
                order_ref TEXT,
                user TEXT,
                note TEXT
            )
        """)
        conn.commit()

@app.route('/')
def index():
    return redirect(url_for('borrow_form'))

@app.route('/borrow', methods=['GET', 'POST'])
def borrow_form():
    if request.method == 'POST':
        date = request.form['date']
        action = request.form['action']
        item = request.form['item']
        qty = int(request.form['qty'])
        order_ref = request.form['order_ref']
        user = request.form['user']
        note = request.form['note']

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO stock (date, action, item, qty, order_ref, user, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, action, item, qty, order_ref, user, note))
            conn.commit()
        return redirect(url_for('borrow_form'))

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('form_borrow.html', today=today)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
