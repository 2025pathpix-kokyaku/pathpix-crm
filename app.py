from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'crm.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/customers')
def customers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers ORDER BY created_at DESC')
    rows = cur.fetchall()
    conn.close()
    return render_template('customers.html', customers=rows)

@app.route('/customer/new', methods=['GET', 'POST'])
def customer_new():
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['contact_person'],
            request.form['phone'],
            request.form['email'],
            request.form['address'],
            request.form['customer_type'],
            request.form['notes'],
            datetime.now().strftime('%Y-%m-%d')
        )
        conn = get_db()
        conn.execute('''
            INSERT INTO customers (name, contact_person, phone, email, address, customer_type, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    return render_template('customer_new.html')

@app.route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    conn = get_db()
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    conn.close()
    return render_template('customer_detail.html', customer=customer)

@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
def customer_edit(customer_id):
    conn = get_db()
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['contact_person'],
            request.form['phone'],
            request.form['email'],
            request.form['address'],
            request.form['customer_type'],
            request.form['notes'],
            customer_id
        )
        conn.execute('''
            UPDATE customers SET name=?, contact_person=?, phone=?, email=?, address=?, customer_type=?, notes=?
            WHERE id=?
        ''', data)
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    conn.close()
    return render_template('customer_edit.html', customer=customer)

@app.route('/contacts')
def contacts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT contacts.id, customers.name AS customer_name, contacts.date, contacts.method,
               contacts.staff, contacts.content
        FROM contacts
        JOIN customers ON contacts.customer_id = customers.id
        ORDER BY contacts.date DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return render_template('contacts.html', contacts=rows)

@app.route('/contract/new')
def contract_new():
    return render_template('contract_new.html')

@app.route('/invoices')
def invoices():
    return render_template('invoices.html')

@app.route('/sales')
def sales():
    month = request.args.get('month')
    selected_month = month or datetime.today().strftime('%Y-%m')

    # 仮のデータ（将来的にはDB連携）
    all_sales = [
        {"id": 1, "customer_name": "株式会社A", "contract_name": "Web制作契約", "sale_date": "2025-05-01", "amount": 150000, "status": "入金済"},
        {"id": 2, "customer_name": "○○高等学校", "contract_name": "キャリア支援契約", "sale_date": "2025-05-08", "amount": 120000, "status": "未入金"},
        {"id": 3, "customer_name": "△△大学", "contract_name": "セミナー講演契約", "sale_date": "2025-04-25", "amount": 200000, "status": "入金済"}
    ]

    filtered = [s for s in all_sales if s['sale_date'].startswith(selected_month)]
    return render_template('sales.html', sales=filtered, selected_month=selected_month)

if __name__ == '__main__':
    app.run(debug=True)
