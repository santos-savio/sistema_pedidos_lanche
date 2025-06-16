from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                lanche TEXT,
                status TEXT,
                hora TEXT
            )
        """)

@app.route('/')
def index():
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    return render_template("index.html", pedidos=pedidos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    cliente = request.form['cliente']
    lanche = request.form['lanche']
    hora = datetime.now().strftime("%H:%M:%S")
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("INSERT INTO pedidos (cliente, lanche, status, hora) VALUES (?, ?, ?, ?)",
                     (cliente, lanche, 'aguardando', hora))
    return redirect('/')

@app.route('/atualizar/<int:id>/<status>')
def atualizar(id, status):
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, id))
    return redirect('/')

@app.route('/display')
def display():
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos ORDER BY id DESC LIMIT 25").fetchall()
    return render_template("display.html", pedidos=pedidos)

@app.route('/relatorio')
def relatorio():
    import csv
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos").fetchall()
    with open("relatorio.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Cliente', 'Lanche', 'Status', 'Hora'])
        writer.writerows(pedidos)
    return "Relatório gerado com sucesso! (arquivo: relatorio.csv)"

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
