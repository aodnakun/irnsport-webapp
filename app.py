# app.py - IRNsport Web App (เวอร์ชันมี error handling)
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_PATH = '/tmp/stock.db'

# ฟังก์ชันสร้างตารางในฐานข้อมูล
def init_db():
    os.makedirs('database', exist_ok=True)  # สร้างโฟลเดอร์ถ้ายังไม่มี
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
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
        ''')
        conn.commit()

@app.route('/')
def index():
    return redirect(url_for('borrow_form'))

@app.route('/borrow', methods=['GET', 'POST'])
def borrow_form():
    if request.method == 'POST':
        try:
            date = request.form['date']
            action = request.form['action']
            item = request.form['item']
            qty = int(request.form['qty'])
            order_ref = request.form['order_ref']
            user = request.form['user']
            note = request.form['note']

            print('📦 รับข้อมูลใหม่:')
            print('วันที่:', date)
            print('ประเภท:', action)
            print('สินค้า:', item)
            print('จำนวน:', qty)
            print('อ้างอิง:', order_ref)
            print('โดย:', user)
            print('หมายเหตุ:', note)

            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO stock (date, action, item, qty, order_ref, user, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (date, action, item, qty, order_ref, user, note))
                conn.commit()

            return redirect(url_for('borrow_form'))

        except Exception as e:
            return f"<h2 style='color:red;'>❌ เกิดข้อผิดพลาด: {str(e)}</h2>"

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('form_borrow.html', today=today)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
