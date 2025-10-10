from flask import Flask, jsonify, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import threading
import webbrowser
import os

app = Flask(__name__)

def init_db():
    # Cria tabelas de lanches e configuração no banco.db
    with sqlite3.connect("banco.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lanches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS configuracao (
                id INTEGER PRIMARY KEY,
                logo_path TEXT
            )
        """)
            # Cria tabela de pedidos no banco.db
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
    print("Sempre mantenha o arquivo banco.db na mesma pasta do app.py.")

@app.route('/')
def index():
    with sqlite3.connect('banco.db') as conn:
        pedidos = conn.execute('SELECT * FROM pedidos WHERE visivel = 1').fetchall()
        lanches = conn.execute('SELECT nome FROM lanches').fetchall()
        logo = conn.execute('SELECT logo_path FROM configuracao WHERE id=1').fetchone()
        print("Logo path:", logo)
    return render_template('paginas/index.html', pedidos=pedidos, lanches=lanches, logo=logo[0] if logo else None)

@app.route('/view')
def view():
    with sqlite3.connect("banco.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos WHERE visivel = 1 ORDER BY id DESC").fetchall()
    return render_template("paginas/view.html", pedidos=pedidos)

@app.route('/adicionar', methods=['POST']) # Adiciona um novo pedido com cliente, lanche e hora atual
def adicionar():
    cliente = request.form['cliente']
    lanche = request.form['lanche']
    observacao = request.form.get('observacao', '')  # Pega a observação do formulário, se não houver, define como vazio
    # observacao = "observação exemplo"
    hora = datetime.now().strftime("%H:%M:%S")
    with sqlite3.connect("banco.db") as conn:
        conn.execute("INSERT INTO pedidos (cliente, lanche, observacao, status, hora) VALUES (?, ?, ?, ?, ?)",
                     (cliente, lanche, observacao, 'aguardando', hora))
    return redirect('/')

@app.route('/atualizar/<int:id>/<status>') # Atualiza o status do pedido conforme o ID e o novo status
def atualizar(id, status):
    with sqlite3.connect("banco.db") as conn:
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, id))
    return redirect('/')

@app.route('/remover/<int:id>') # Remova da exibição definindo visível como 0
def remover(id):
    with sqlite3.connect("banco.db") as conn:
        conn.execute("UPDATE pedidos SET visivel = 0 WHERE id = ?", (id,))
    return redirect('/')

@app.route('/display')
def display():
    with sqlite3.connect("banco.db") as conn:
        pedidos = conn.execute("SELECT * FROM pedidos WHERE visivel = 1 ORDER BY id DESC LIMIT 25").fetchall()
        logo = conn.execute("SELECT logo_path FROM configuracao WHERE id=1").fetchone()
    logo_url = url_for('static', filename=logo[0]) if logo and logo[0] else None
    return render_template("paginas/display.html", pedidos=pedidos, logo=logo_url)

@app.route('/relatorio')
def relatorio():
    import csv
    with sqlite3.connect("banco.db") as conn:
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

def get_lanches():
    with sqlite3.connect('banco.db') as conn:
        return conn.execute('SELECT id, nome FROM lanches').fetchall()

@app.route('/config', methods=['GET'])
def config():
    lanches = get_lanches()
    with sqlite3.connect('banco.db') as conn:
        logo = conn.execute('SELECT logo_path FROM configuracao WHERE id=1').fetchone()
    logo_url = url_for('static', filename=logo[0]) if logo and logo[0] else None
    return render_template('paginas/config.html', lanches=lanches, logo=logo_url)

@app.route('/config/lanches', methods=['POST'])
def config_lanches():
    with sqlite3.connect('banco.db') as conn:
        if 'adicionar' in request.form:
            novo = request.form['novo_lanche']
            if novo:
                conn.execute('INSERT OR IGNORE INTO lanches (nome) VALUES (?)', (novo,))
        elif 'remover' in request.form:
            conn.execute('DELETE FROM lanches WHERE id=?', (request.form['remover'],))
        conn.commit()
    return redirect(url_for('config'))

@app.route('/config/logo', methods=['POST'])
def config_logo():
    file = request.files['logo']
    print("Arquivo recebido:", file.filename)
    if file:
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        path = os.path.join(static_dir, file.filename)
        file.save(path)
        # Salva apenas o nome do arquivo no banco
        with sqlite3.connect('banco.db') as conn:
            conn.execute('INSERT OR REPLACE INTO configuracao (id, logo_path) VALUES (1, ?)', (file.filename,))
            conn.commit()
        return jsonify({'success': True, 'message': 'Logo atualizada com sucesso'})
    else:
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})

@app.route('/config/logo/remover', methods=['POST'])
def remover_logo():
    with sqlite3.connect('banco.db') as conn:
        conn.execute('DELETE FROM configuracao WHERE id=1')
        conn.commit()
    return redirect(url_for('config'))

if __name__ == '__main__':
    init_db()
    threading.Timer(0.5, abrir_servidor).start()  # Aguarda 0.5 segundos antes de abrir
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5001)