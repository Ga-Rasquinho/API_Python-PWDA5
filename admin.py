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


@app.route('/list', methods = ['GET'])
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
        
    return jsonify(users)


@app.route('/disable/<int:user_id>', methods=['PUT'])
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


@app.route('/able/<int:user_id>', methods=['PUT'])
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
            return jsonify("Falha ao desativar, usuário não encontrado")
        
    except Exception as e:
        return jsonify(f"Falha ao ativar usuário: {str(e)}")

    cursor.execute(sql)
    mydb.commit()
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
    cursor.execute(sql)
    user = cursor.fetchone()

    if user[4] == 1 and user[3] == login['senha'] :
        return jsonify("Logado como admin")
    else:
      return jsonify("Falha ao logar")


#Main
if __name__ == '__main__':
    app.run()