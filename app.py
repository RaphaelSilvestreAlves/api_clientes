import sqlite3
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

def conectar_banco():
    conexao = sqlite3.connect('clientes.db')
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_tabela():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT
        )
 ''')
    
    conexao.commit()
    conexao.close()

criar_tabela()

def validar_dados_cliente(dados):
    if not dados:
        return 'JSON não enviado'
    if 'nome' not in dados or not dados['nome'].strip():
        return 'O campo nome é obrigatório'
    if 'email' not in dados or not dados['email'].strip():
        return 'O campo email é obrigatório'

    return None

def buscar_usuarios_api_externa():
    url = 'https://jsonplaceholder.typicode.com/users'
    resposta = requests.get(url, timeout = 10)
    resposta.raise_for_status()
    return resposta.json()

def transformar_usuario_em_cliente(usuario):
    return {
        'nome': usuario['name'].strip(),
        'email': usuario['email'].strip().lower(),
        'telefone': usuario.get('phone', '').strip()
    }

@app.route('/')
def home():
    return 'API FUNCIONANDO!'





@app.route('/clientes', methods=['GET'])
def listar_clientes():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    
    conexao.close()
    
    return jsonify([dict(cliente) for cliente in clientes])

@app.route('/clientes', methods=['POST'])
def criar_cliente():
    dados = request.get_json()
    erro = validar_dados_cliente(dados)
    
    if erro:
        return jsonify({'erro': erro}), 400
    
    nome = dados['nome'].strip()
    email = dados['email'].strip().lower()
    telefone = dados.get('telefone', '').strip()
    
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute(
        'INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)',
        (nome, email, telefone)
        )
    
    conexao.commit()
    id_cliente = cursor.lastrowid
    conexao.close()
    
    
    novo_cliente =  {
        'id': id_cliente,
        'nome': nome,
        'email': email,
        'telefone': telefone
    }
    
    return jsonify(novo_cliente), 201

@app.route('/importar-clientes', methods=['POST'])
def importar_clientes():
    try:
        usuarios_externos = buscar_usuarios_api_externa()
        
        conexao = conectar_banco()
        cursor = conexao.cursor()
        
        clientes_importados = []
        
        for usuario in usuarios_externos:
            cliente = transformar_usuario_em_cliente(usuario)
            
            cursor.execute(
                'INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)',
                (cliente['nome'], cliente['email'], cliente['telefone'])
            )
            
            cliente['id'] = cursor.lastrowid
            clientes_importados.append(cliente)
            
        conexao.commit()
        conexao.close()
        
        return jsonify(clientes_importados), 201
    except requests.RequestException:
        return jsonify({'erro': 'Erro ao consumir a API externa'}), 502

@app.route('/clientes/<int:id>', methods=['GET'])
def buscar_cliente(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    cliente = cursor.fetchone()
    
    conexao.close()
    
    if cliente:
        return jsonify(dict(cliente))
        
    return jsonify({'erro': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:id>', methods=['PUT'])
def atualizar_cliente(id):
    dados = request.get_json()
    erro = validar_dados_cliente(dados)
    
    if erro:
        return jsonify({'erro': erro}), 400
    
    nome = dados['nome'].strip()
    email = dados['email'].strip().lower()
    telefone = dados.get('telefone', '').strip()
    
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    cliente = cursor.fetchone()

    if not cliente:
        conexao.close()
        return jsonify({'erro': 'Cliente não encontrado'}), 404
    
    cursor.execute(
        'UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?',
        (nome, email, telefone, id)
    )
    
    conexao.commit()
    conexao.close()
    
    cliente_atualizado = {
        'id': id,
        'nome': nome,
        'email': email,
        'telefone': telefone
    }
      
            
    return jsonify(cliente_atualizado)
        

@app.route('/clientes/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    cliente = cursor.fetchone()
    
    if not cliente:
        conexao.close()
        return jsonify({'erro':'Cliente não encontrado'}), 404
    
    cursor.execute('DELETE FROM clientes WHERE id =?', (id,))
    conexao.commit()
    conexao.close()
    
    return jsonify({'mensagem':'Cliente deletado com sucesso'})
    
if __name__ == '__main__':
    app.run(debug=True)