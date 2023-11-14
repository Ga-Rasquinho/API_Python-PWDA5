import mysql.connector
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MinhaChaveSecreta123'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 180 #3 minutos
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

    except Exception as e:
        return jsonify(f"Falha ao cadastrar: {str(e)}")
    
    return jsonify(Mensagem = 'Usuário cadastro com sucesso')


@app.route('/login', methods = ['POST'])
def login_user():
    """
    Função que realiza o login do usuário
    :return: jsonify("Message")
    """
    cursor = mydb.cursor()
    login = request.json 

    try:
        sql = f"select * from usuario where email = '{login['email']}'"
        cursor.execute(sql)
        user = cursor.fetchone()

        if user[4] == 1 and user[3] == login['senha']:
            return jsonify("Você deve acessar a página de administrador para logar")

        elif check_password_hash(user[3], login['senha']) and user[5] != 0:
            user_id = user[0]
            access_token = create_access_token(identity=user_id)
            return jsonify(access_token=access_token)

        else:
            return jsonify("Erro ao autenticar, tente novamente.")

    except Exception as e:
        return jsonify(f"Error{e}")


@app.route('/update_profile', methods=['PUT'])
def update_profile():
    """
    Função que edita o perfil do usuário
    :return: jsonify("Message")
    """
    cursor = mydb.cursor()
    data = request.json

    try:
        find_user = f"select email, senha from usuario where email = '{data['email']}'"
        cursor.execute(find_user)
        result = cursor.fetchone()

        if result is not None and check_password_hash(result[1], data['senha']):
            sql = "update usuario set nome_usuario = %s where email = %s"
            cursor.execute(sql, (data['nome_usuario'], data['email']))
            mydb.commit()

            return jsonify("Nome cadastrado com sucesso")
        else:
            return jsonify("Usuário não encontrado")

    except Exception as e:
        return jsonify(f"Error:{e}")


@app.route('/add_book', methods=['POST'])
@jwt_required()
def add_book():
    """
    Função que adiciona livros
    :return: jsonify(Message)
    """
    user_id = get_jwt_identity()
    data = request.json

    cursor = mydb.cursor()
    sql = "insert into livros (nome_livro, autor_livro, categoria_livro, preco_livro, usuario_id) values (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (data['nome_livro'], data['autor_livro'], data['categoria_livro'], data['preco_livro'], user_id))
    mydb.commit()
    
    return jsonify(message="Livro adicionado com sucesso")


@app.route('/show_books', methods=['GET'])
@jwt_required()
def show_books():
    """
    Função que lista os livros
    :return: jsonify(books) -> list
    """
    cursor = mydb.cursor()
    cursor.execute("select * from livros where status_livro = 'ATIVO'")
    books = cursor.fetchall() 

    books_list = list()
    for book in books:
        books_list.append(
            {
                'id_livro': book[0],
                'nome_livro': book[1],
                'autor_livro': book[2],
                'categoria_livro': book[3],
                'preco_livro': book[4]	
            }   
        )
    
    return jsonify(books_list)


@app.route('/show_my_sales_books', methods=['GET'])
@jwt_required()
def show_my_sales_books():
    """
    Função que lista os livros
    :return: jsonify(books_list) -> list
    """

    cursor = mydb.cursor()
    user_id = get_jwt_identity()

    sql = f"select * from livros where status_livro != 'INATIVO' and usuario_id = {user_id}"
    cursor.execute(sql)
    books = cursor.fetchall() 

    books_list = list()
    for book in books:
        books_list.append(
            {   
                'id_livro': book[0],
                'nome_livro': book[1],
                'autor_livro': book[2],
                'categoria_livro': book[3],
                'preco_livro': book[4],
                'status_livro': book[5]	
            }   
        )
    
    return jsonify(books_list)


@app.route('/buy_book', methods=['POST'])
@jwt_required()
def buy_book():
    """
    """
    cursor = mydb.cursor()
    data = request.json
    user_id = get_jwt_identity()

    try:
        find_book = f"select status_livro from livros where id_livro = {data['id_livro']} and nome_livro = '{data['nome_livro']}'"
        cursor.execute(find_book)
        result = cursor.fetchone()

        if result is not None and result[0] == "ATIVO":
            sql = f"update livros set status_livro = 'VENDIDO', usuario_comprador = {user_id} where id_livro = {data['id_livro']}"
            cursor.execute(sql)
            mydb.commit()
            return jsonify("Livro comprado com sucesso!")
        else:
            return jsonify("Livro não encontrado ou já vendido!")

    except Exception as e:
        return jsonify(f"Error:{e}")

@app.route("/show_my_purchased_books", methods=["GET"])
@jwt_required()
def show_my_purchased_books():
    """
    Fução que mostra os livros que o usuário comprou
    :return: jsonify(books_list) -> list
    """
    cursor = mydb.cursor()
    user_id = get_jwt_identity()

    sql = f"select * from livros where status_livro != 'INATIVO' and usuario_comprador = {user_id}"
    cursor.execute(sql)
    books = cursor.fetchall() 

    books_list = list()
    for book in books:
        books_list.append(
            {   
                'id_livro': book[0],
                'nome_livro': book[1],
                'autor_livro': book[2],
                'categoria_livro': book[3],
                'preco_livro': book[4]
            }   
        )
    
    return jsonify(books_list)

if __name__ == '__main__':
    """
    Main
    """
    app.run()