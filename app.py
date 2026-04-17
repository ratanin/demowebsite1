from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("sushi.db")

# สร้าง table
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sushi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER,
        category_id INTEGER,
        image TEXT,
        FOREIGN KEY (category_id) REFERENCES category(id)
    )
    """)

    # insert category ถ้ายังไม่มี
    cur.execute("SELECT COUNT(*) FROM category")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO category (name) VALUES (?)", [
            ("Nigiri",),
            ("Roll",),
            ("Sashimi",)
        ])

    # insert sushi ตัวอย่าง
    cur.execute("SELECT COUNT(*) FROM sushi")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO sushi (name, price, stock, category_id, image)
        VALUES (?, ?, ?, ?, ?)
        """, [
            ("Salmon Nigiri", 120, 10, 1, "https://upload.wikimedia.org/wikipedia/commons/6/60/Sushi_platter.jpg"),
            ("Tuna Roll", 150, 5, 2, "https://upload.wikimedia.org/wikipedia/commons/0/0b/California_roll.jpg"),
            ("Ebi Sashimi", 180, 8, 3, "https://upload.wikimedia.org/wikipedia/commons/2/2c/Sashimi.jpg")
        ])

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT sushi.id, sushi.name, sushi.price, sushi.stock, category.name, sushi.image
        FROM sushi
        JOIN category ON sushi.category_id = category.id
    """)
    sushi = cur.fetchall()
    conn.close()
    return render_template("index.html", sushi=sushi)

@app.route('/add', methods=['GET', 'POST'])
def add():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category_id']
        image = request.form['image']

        cur.execute("""
        INSERT INTO sushi (name, price, stock, category_id, image)
        VALUES (?, ?, ?, ?, ?)
        """, (name, price, stock, category_id, image))

        conn.commit()
        conn.close()
        return redirect('/')

    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()
    conn.close()
    return render_template("add.html", categories=categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category_id']
        image = request.form['image']

        cur.execute("""
        UPDATE sushi
        SET name=?, price=?, stock=?, category_id=?, image=?
        WHERE id=?
        """, (name, price, stock, category_id, image, id))

        conn.commit()
        conn.close()
        return redirect('/')

    cur.execute("SELECT * FROM sushi WHERE id=?", (id,))
    sushi = cur.fetchone()

    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()

    conn.close()
    return render_template("edit.html", sushi=sushi, categories=categories)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM sushi WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)