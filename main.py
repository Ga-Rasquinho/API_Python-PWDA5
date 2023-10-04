import mysql.connector
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#Conexão com o banco de dados
mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '1234',
    database = 'usuarios_pwa5'
)

#Listar usuário
@app.route('/list', methods = ['GET'])
def get_user():
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM usuario')
    users = cursor.fetchall() 

    users_list = list()
    for user in users:
        users_list.append(
            {
                'id': user[0],
                'nome_usuario': user[1],
                'email': user[2],
                'senha': user[3],
                "tipo_usu": user[4]
            }
        )
    return jsonify(users)

#Criar usuário
@app.route('/create', methods = ['POST'])
def create_user():
    cursor = mydb.cursor()
    user = request.json
    hash_password = generate_password_hash(user['senha'], method='pbkdf2:sha256') #Criptografia de senha
    sql = f"INSERT INTO usuario (nome_usuario, email, senha) VALUES ('{user['nome_usuario']}', '{user['email']}', '{hash_password}')"
    cursor.execute(sql)
    mydb.commit()
    return jsonify(Mensagem = 'Usuário cadastro com sucesso')

#Login em desenvolvimento... 
@app.route('/login', methods = ['POST'])
def login_user():
    cursor = mydb.cursor()
    login = request.json     
    
    sql = f"select * from usuario where email = '{login['email']}'"
    cursor.execute(sql)
    user = cursor.fetchone()

    if user and check_password_hash(user[3], login['senha']):
        return jsonify("Login feito com sucesso")
    else:
        return jsonify("Falha ao logar")

#Main
if __name__ == '__main__':
    app.run()