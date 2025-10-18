"""IRNsport inventory web application."""

from collections import defaultdict
from datetime import datetime
import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)
app.config["SECRET_KEY"] = "irnsport-stock-secret"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "stock.db")


def init_db() -> None:
    """Ensure the database and the ``stock`` table exist."""

    os.makedirs(DB_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
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
            """
        )
        conn.commit()

@app.route("/")
def index():
    return redirect(url_for("borrow_form"))

@app.route("/borrow", methods=["GET", "POST"])
def borrow_form():
    if request.method == "POST":
        try:
            date = request.form["date"]
            action = request.form["action"]
            item = request.form["item"]
            qty = int(request.form["qty"])
            order_ref = request.form["order_ref"]
            user = request.form["user"]
            note = request.form["note"]

            print("📦 รับข้อมูลใหม่:")
            print("วันที่:", date)
            print("ประเภท:", action)
            print("สินค้า:", item)
            print("จำนวน:", qty)
            print("อ้างอิง:", order_ref)
            print("โดย:", user)
            print("หมายเหตุ:", note)

            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO stock (date, action, item, qty, order_ref, user, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (date, action, item, qty, order_ref, user, note),
                )
                conn.commit()

            return redirect(url_for("borrow_form", success="1"))

        except Exception as e:
            return f"<h2 style='color:red;'>❌ เกิดข้อผิดพลาด: {str(e)}</h2>"

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template(
        "form_borrow.html",
        today=today,
        success=request.args.get("success") == "1",
    )


@app.route("/inventory")
def inventory_dashboard():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM stock ORDER BY date DESC, id DESC"
        )
        transactions = cur.fetchall()

        cur.execute(
            """
            SELECT
                item,
                SUM(CASE WHEN action = 'รับเข้าสินค้า' THEN qty ELSE 0 END) AS total_in,
                SUM(CASE WHEN action = 'เบิกสินค้า' THEN qty ELSE 0 END) AS total_out,
                SUM(CASE WHEN action = 'รับเข้าสินค้า' THEN qty ELSE -qty END) AS balance
            FROM stock
            GROUP BY item
            ORDER BY item COLLATE NOCASE
            """
        )
        summary = cur.fetchall()

    totals = defaultdict(int)
    for row in summary:
        totals["in"] += row["total_in"] or 0
        totals["out"] += row["total_out"] or 0
        totals["balance"] += row["balance"] or 0

    return render_template(
        "inventory.html",
        transactions=transactions,
        summary=summary,
        totals=totals,
    )

init_db()


if __name__ == '__main__':
    app.run(debug=True)
