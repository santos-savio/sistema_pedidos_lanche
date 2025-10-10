# Sistema de Pedidos de Lanche
Aplicação web desenvolvida em Flask para o controle de pedidos de lanches. <br>
Permite exibir páginas HTML para gestão e acompanhamento dos pedidos


## 🧩 Tecnologias
Python (Flask) <br>
HTML / CSS <br>
Jinja2 (templates) <br>


## ⚙️ Funcionalidades
Executado localmente, acessível na rede local <br>
Acesso via porta 5001 <br>
Upload de imagens (JPG, PNG) <br>
Páginas principais: <br>
index → controle dos pedidos (administrativo) <br>
view → acompanhamento da cozinha, permitindo marcar pedidos como prontos <br>
display → visualização pública dos pedidos <br>
config → Definição das opções de pedidos e logotipo do display (opcional)


## 🗂️ Estrutura do projeto
<pre>
sistema_pedidos_lanche/  
├── app.py
├── static/
├── templates/
│    └── paginas/
│        ├── index.html
│        ├── view.html
│        └── display.html
│        └── config.html
└── LICENSE
</pre>

## 🖥️ Acesse em qualquer dispositivo da rede: <br>
http://IP-do-computador:5001
