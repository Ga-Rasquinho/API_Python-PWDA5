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


@app.route('/create', methods = ['POST'])
def create_user():
    """
    Função que cria o usuário
    :return: jsonify("Message")
    """
    cursor = mydb.cursor()
    user = request.json
    hash_password = generate_password_hash(user['senha'], method='pbkdf2:sha256') #Criptografia de senha

    try: 
        sql = f"INSERT INTO usuario (nome_usuario, email, senha) VALUES ('{user['nome_usuario']}', '{user['email']}', '{hash_password}')"
        cursor.execute(sql)
        mydb.commit()
    except Exception as e:
        return jsonify(f"Falha ao cadastrar: {str(e)}")
    
    return jsonify(Mensagem = 'Usuário cadastro com sucesso')


#Precisa ser aprimorado
@app.route('/login', methods = ['POST'])
def login_user():
    """
    Função que realiza o login do usuário
    :return: jsonify("Message")
    """
    try:
        cursor = mydb.cursor()
        login = request.json     
        
        sql = f"select * from usuario where email = '{login['email']}'"
        cursor.execute(sql)
        user = cursor.fetchone()

        if user[4] == 1:
            return jsonify("Logado como admin")
        else:
            if user and check_password_hash(user[3], login['senha']):
                return jsonify("Login feito com sucesso")
            else:
                return jsonify("Falha ao logar")
            
    except:
        return jsonify(f"Falha ao logar, credências incorretas")


if __name__ == '__main__':
    """
    Main
    """
    app.run()