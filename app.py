from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime
import threading
import webbrowser

app = Flask(__name__)

def init_db():
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                lanche TEXT,
                observacao TEXT DEFAULT '',
                status TEXT,
                hora TEXT,
                visivel INTEGER DEFAULT 1
            )
        """)

def abrir_servidor():
    webbrowser.open("http://127.0.0.1:5001/")

def shutdown_server():
    """Função para parar o servidor Flask."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Não está rodando com o Werkzeug Server')
    func()
    return "Servidor parado."

def mensagem_inicial():
    print("Sempre mantenha o arquivo vendas.db na mesma pasta do app.py.")

@app.route('/')
def index():
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos WHERE visivel = 1 ORDER BY id DESC").fetchall()
    return render_template("paginas/index.html", pedidos=pedidos)

@app.route('/view')
def view():
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos WHERE visivel = 1 ORDER BY id DESC").fetchall()
    return render_template("paginas/view.html", pedidos=pedidos)

@app.route('/adicionar', methods=['POST']) # Adiciona um novo pedido com cliente, lanche e hora atual
def adicionar():
    cliente = request.form['cliente']
    lanche = request.form['lanche']
    observacao = request.form.get('observacao', '')  # Pega a observação do formulário, se não houver, define como vazio
    # observacao = "observação exemplo"
    hora = datetime.now().strftime("%H:%M:%S")
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("INSERT INTO pedidos (cliente, lanche, observacao, status, hora) VALUES (?, ?, ?, ?, ?)",
                     (cliente, lanche, observacao, 'aguardando', hora))
    return redirect('/')

@app.route('/atualizar/<int:id>/<status>') # Atualiza o status do pedido conforme o ID e o novo status
def atualizar(id, status):
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, id))
    return redirect('/')

@app.route('/remover/<int:id>') # Remova da exibição definindo visível como 0
def remover(id):
    with sqlite3.connect("vendas.db") as conn:
        conn.execute("UPDATE pedidos SET visivel = 0 WHERE id = ?", (id,))
    return redirect('/')

@app.route('/display')
def display():
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos WHERE visivel = 1 ORDER BY id DESC LIMIT 25").fetchall()
    return render_template("paginas/display.html", pedidos=pedidos)

@app.route('/relatorio')
def relatorio():
    import csv
    with sqlite3.connect("vendas.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos").fetchall()
    with open("relatorio.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Cliente', 'Lanche', 'Observação', 'Status', 'Hora'])
        writer.writerows(pedidos)

    # Retorna um script para alertar o usuário e volta à página anterior
    return "<script> alert(\"Relatório gerado com sucesso! (arquivo: relatorio.csv)\")</script>" \
           "<script> window.history.back(); </script>"

@app.route('/shutdown', methods=['POST']) # Rota para parar o servidor
def shutdown():
    print("Servidor está sendo parado...")
    return shutdown_server()

if __name__ == '__main__':
    init_db()
    threading.Timer(1.0, abrir_servidor).start()  # Aguarda 1 segundo antes de abrir
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5001)