# app.py - IRNsport Web App (เวอร์ชันมี error handling)
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_PATH = '/tmp/stock.db'


def calculate_profit(sale_price_per_unit, qty, cost_per_unit, platform_fee_percent, ads_cost=0, shipping_cost=0, other_cost=0):
    revenue = sale_price_per_unit * qty
    cogs = cost_per_unit * qty
    platform_fee = revenue * (platform_fee_percent / 100)
    total_cost = cogs + platform_fee + ads_cost + shipping_cost + other_cost
    net_profit = revenue - total_cost
    margin_percent = (net_profit / revenue * 100) if revenue else 0

    return {
        'revenue': revenue,
        'cogs': cogs,
        'platform_fee': platform_fee,
        'total_cost': total_cost,
        'net_profit': net_profit,
        'margin_percent': margin_percent,
    }

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



@app.route('/profit', methods=['GET', 'POST'])
def profit_calculator():
    values = {
        'sale_price_per_unit': '',
        'qty': '',
        'cost_per_unit': '',
        'platform_fee_percent': '',
        'ads_cost': 0,
        'shipping_cost': 0,
        'other_cost': 0,
    }
    result = None
    error = None

    if request.method == 'POST':
        try:
            values = {key: request.form.get(key, '') for key in values}
            sale_price_per_unit = float(values['sale_price_per_unit'])
            qty = int(values['qty'])
            cost_per_unit = float(values['cost_per_unit'])
            platform_fee_percent = float(values['platform_fee_percent'])
            ads_cost = float(values['ads_cost'] or 0)
            shipping_cost = float(values['shipping_cost'] or 0)
            other_cost = float(values['other_cost'] or 0)

            result = calculate_profit(
                sale_price_per_unit, qty, cost_per_unit, platform_fee_percent, ads_cost, shipping_cost, other_cost
            )
        except ValueError:
            error = 'กรอกข้อมูลไม่ถูกต้อง กรุณาตรวจสอบตัวเลขอีกครั้ง'
        except Exception as e:
            error = f'เกิดข้อผิดพลาด: {str(e)}'

    return render_template('profit_calculator.html', values=values, result=result, error=error)

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
