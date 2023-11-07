import mysql.connector
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MinhaChaveSecreta123'
jwt = JWTManager(app)

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
        search_user = f"select email from usuario where email = '{user['email']}'"
        cursor.execute(search_user)
        result = cursor.fetchone()

        if result is not None:
            return jsonify("Falha ao cadastrar, usuário já existente")

        sql = f"INSERT INTO usuario (nome_usuario, email, senha) VALUES ('{user['nome_usuario']}', '{user['email']}', '{hash_password}')"
        cursor.execute(sql)
        mydb.commit()
        
        cursor.close()
        mydb.close()

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
    cursor = mydb.cursor()
    login = request.json     
    
    sql = f"select * from usuario where email = '{login['email']}'"
    try:
        cursor.execute(sql)
        user = cursor.fetchone()

        if user[4] == 1 and user[3] == login['senha']:
            return jsonify("Você deve acessar a página de administrador para logar")
        else:
            user_id = user[0]
            access_token = create_access_token(identity=user_id)
            return jsonify(access_token=access_token)

    except Exception as e:
        return jsonify(f"Error{e}")


@app.route('/show_books', methods=['GET'])
@jwt_required()
def show_books():
    """
    Função que lista os livros
    :return: jsonify(books) -> list
    """
    cursor = mydb.cursor()
    cursor.execute('select * from livros')
    books = cursor.fetchall() 

    books_list = list()
    for book in books:
        books_list.append(
            {
                'nome_livro': book[0],
                'autor_livro': book[1],
                'categoria_livro': book[2],
                'preco_livro': book[3]	
            }   
        )
    
    return jsonify(books_list)


if __name__ == '__main__':
    """
    Main
    """
    app.run()