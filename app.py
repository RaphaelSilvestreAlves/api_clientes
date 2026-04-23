from flask import Flask, jsonify, request

app = Flask(__name__)

clientes = []

def validar_dados_cliente(dados):
    if not dados:
        return 'JSON não enviado'
    if 'nome' not in dados or not dados['nome'].strip():
        return 'O campo nome é obrigatório'
    if 'email' not in dados or not dados['email'].strip():
        return 'O campo email é obrigatório'

    return None

@app.route('/')
def home():
    return 'API FUNCIONANDO!'

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    return jsonify(clientes)

@app.route('/clientes', methods=['POST'])
def criar_cliente():
    dados = request.get_json()
    erro = validar_dados_cliente(dados)
    
    if erro:
        return jsonify({'erro': erro}), 400
    
    novo_cliente =  {
        'id': len(clientes) + 1,
        'nome': dados['nome'].strip(),
        'email': dados['email'].strip().lower()
    }
    
    clientes.append(novo_cliente)
    return jsonify(novo_cliente), 201

@app.route('/clientes/<int:id>', methods=['GET'])
def buscar_cliente(id):
    for cliente in clientes:
        if cliente['id'] == id:
            return jsonify(cliente)
        
    return jsonify({'erro': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:id>', methods=['PUT'])
def atualizar_cliente(id):
    dados = request.get_json()
    erro = validar_dados_cliente(dados)
    
    if erro:
        return jsonify({'erro': erro}), 400
    
    for cliente in clientes:
        if cliente['id'] == id:
            cliente['nome'] = dados['nome'].strip()
            cliente['email'] = dados['email'].strip().lower()
            return jsonify(cliente)    
            
    return jsonify({'erro': 'Cliente não encontrado'}), 404
        

@app.route('/clientes/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    for cliente in clientes:
        if cliente['id'] == id:
            clientes.remove(cliente)
            return jsonify({'mensagem':'Cliente deletado com sucesso'})
    
    return jsonify({'erro': 'Cliente não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)