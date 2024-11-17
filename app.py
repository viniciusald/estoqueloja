from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Inicializar o banco de dados
def init_db():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

# Rotas
@app.route('/')
def index():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        conn = sqlite3.connect('database/app.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, quantity) VALUES (?, ?)', (product_name, quantity))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/sales', methods=['POST'])
def sales():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT quantity FROM products WHERE id = ?', (product_id,))
    current_quantity = cursor.fetchone()[0]
    if current_quantity >= quantity:
        cursor.execute('INSERT INTO sales (product_id, quantity, date) VALUES (?, ?, DATE("now"))', (product_id, quantity))
        cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (quantity, product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/report')
def report():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT p.name, s.quantity, s.date FROM sales s JOIN products p ON s.product_id = p.id')
    sales = cursor.fetchall()
    conn.close()
    return render_template('report.html', sales=sales)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)