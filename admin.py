import mysql.connector
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

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


@app.route('/list', methods = ['GET'])
@jwt_required()
def get_users():
    """
    Função que lista usuários
    :return: jsonify(user) -> list
    """
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
                'tipo_usu': user[4],
                'usuario_ativo': user[5]	
            }   
        )
        
    return jsonify(users_list)


@app.route('/disable/<int:user_id>', methods=['PUT'])
@jwt_required()
def disable_user(user_id):
    """
    Função que desabilita usuário
    :return: jsonify("Message")
    """

    cursor = mydb.cursor()

    sql = f"update usuario set usuario_ativo = 0 where id = {user_id}"

    cursor.execute(sql)

    try:
        authorization_query = f"select id from usuario where id = {user_id}"
        cursor.execute(authorization_query)
        result = cursor.fetchone()

        if not result:
            return jsonify("Falha ao desativar, usuário não encontrado")
        
    except Exception as e:
        return jsonify(f"Falha ao desativar usuário: {str(e)}")
    
    mydb.commit()
    return jsonify("Usuário desativado com sucesso!")


@app.route('/enable/<int:user_id>', methods=['PUT'])
@jwt_required()
def able_user(user_id):
    """
    Função que habilitado usuário
    :return: jsonify("Message")
    """
    cursor = mydb.cursor()

    sql = f"update usuario set usuario_ativo = 1 where id = {user_id}"

    try:
        authorization_query = f"select id from usuario where id = {user_id}"
        cursor.execute(authorization_query)
        result = cursor.fetchone()

        if not result:
            return jsonify("Falha ao ativar, usuário não encontrado")
        
    except Exception as e:
        return jsonify(f"Falha ao ativar usuário: {str(e)}")

    cursor.execute(sql)
    mydb.commit()
    return jsonify("Usuário ativado com sucesso!")


@app.route('/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Função que deleta usuário
    :return: jsonify("Message")
    """
    cursor = mydb.cursor()

    sql = f"delete from usuario where id = {user_id}"

    if user_id == 5:    
        return jsonify("Impossível deletar admin")

    try:
        authorization_query = f"select id from usuario where id = {user_id}"
        cursor.execute(authorization_query)
        result = cursor.fetchone()

        if not result:
            return jsonify("Falha ao deletar, usuário não encontrado")
        
        cursor.execute(sql)
        mydb.commit()

    except Exception as e:
        return jsonify(f"Falha ao ativar usuário: {str(e)}")

    return jsonify("Usuário excluído com sucesso!")


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

        if user[4] == 1 and user[3] == login['senha'] :
            user_id = user[0]
            access_token = create_access_token(identity=user_id)
            return jsonify(access_token=access_token)
        else:
            return jsonify("Falha ao Autenticar")
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
                'id_livro': book[0],
                'nome_livro': book[1],
                'autor_livro': book[2],
                'categoria_livro': book[3],
                'preco_livro': book[4],
                'status_livro': book[5],
                'usuario_id': book[6]	
            }   
        )
        
    return jsonify(books_list)


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
    sql = f"insert into livros (nome_livro, autor_livro, categoria_livro, preco_livro, usuario_id) values (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (data['nome_livro'], data['autor_livro'], data['categoria_livro'], data['preco_livro'], user_id))
    mydb.commit()
    
    return jsonify(message="Livro adicionado com sucesso")


@app.route('/disable_book/<int:id_livro>', methods=['PUT'])
@jwt_required()
def disable_book(id_livro):
    """
    Função que habilita livros
    :return: jsonify(Message)
    """
    teste = "INATIVO"
    try:
        cursor = mydb.cursor()
        sql = f"update livros set status_livro = 'INATIVO' where id_livro = {id_livro}"   
        cursor.execute(sql)

        if cursor.rowcount == 0:
            return jsonify("Falha ao desativar livro, livro não encontrado")

        mydb.commit()
    
    except Exception as e:
        return jsonify(f"Error:{e}")
    
    return jsonify("Livro desativado com sucesso")


@app.route('/delete_book/<int:id_livro>', methods=['DELETE'])
@jwt_required()
def delete_book(id_livro): 
    """
    Função que deleta livros
    :return: jsonify(message)
    """
    cursor = mydb.cursor()

    sql = f'delete from livros where id_livro = {id_livro}'

    try:
        authorization_query = f"select id_livro from livros where id = {id_livro}"
        cursor.execute(authorization_query)
        result = cursor.fetchone()

        if not result:
            return jsonify("Falha ao deletar, livro não encontrado")
        
        cursor.execute(sql)
        mydb.commit()

    except Exception as e:
        return jsonify(f"Falha ao deletar livro: {str(e)}")

    return jsonify("Livro excluído com sucesso!")


@app.route('/edit_book', methods=['PUT'])
@jwt_required()
def edit_book():
    """
    Função que edita os livros
    :return: jsonify(Message)
    """
    cursor = mydb.cursor()
    book = request.json
    sql = "UPDATE livros SET nome_livro = %s, autor_livro = %s, categoria_livro = %s, preco_livro = %s WHERE id_livro = %s"

    try:
        authorization_query = f"select id_livro from livros where id_livro = {book['id_livro']}"
        cursor.execute(authorization_query)
        result = cursor.fetchone()

        if not result:
            return jsonify("Falha ao editar, livro não encontrado")
        
    except Exception as e:
        return jsonify(f"Falha ao editar livro: {str(e)}")

    cursor.execute(sql, (book['nome_livro'], book['autor_livro'], book['categoria_livro'], book['preco_livro'], book['id_livro']))
    mydb.commit()
    return jsonify("Livro editado com sucesso!")


@app.route('/search_book', methods=['GET'])
@jwt_required()
def search_books():
    """
    """
    find = False
    cursor = mydb.cursor()
    book = request.json 
    try:
        if 'nome_livro' in book and book is not None:
            search = cursor.execute(f"select nome_livro, autor_livro, categoria_livro, preco_livro from livros where nome_livro = '{book['nome_livro']}' and status_livro != 'INATIVO'")
            if search is not None:
                find = True

        elif 'categoria_livro' in book:
            search = cursor.execute(f"select nome_livro, autor_livro, categoria_livro, preco_livro from livros where categoria_livro = '{book['categoria_livro']}' and status_livro != 'INATIVO'")
            if search is not None:
                find = True

        #Lista Livros selecionados
        if find is True:    
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
        else:
            return jsonify('Nenhum resultado encontrado.')
        
    except Exception as e:
        return jsonify(f"Erro:{e}")


#Main
if __name__ == '__main__':
    app.run()