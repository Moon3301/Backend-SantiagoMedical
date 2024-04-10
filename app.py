from flask import Flask,jsonify,make_response,render_template,request, session, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS,cross_origin
from datetime import datetime, timedelta
import requests,json,os,fnmatch,shutil
import time, locale
from connect_db_odbc import conectar_bd
from correoVerificacion import enviar_correo
import random
import string

requests.packages.urllib3.disable_warnings()
app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
dt = datetime.now()

app.config['JWT_SECRET_KEY'] = 'admin1234'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30.0)

app.secret_key = 'admin1234'

jwt = JWTManager(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World! fuck</p>"

@app.route('/loginToken', methods=['POST'])
def loginToken():

    print("Validando credenciales ...")

    try:

        username = request.json['username']
        password = request.json['password']

    except Exception as e:
        print(f'No se pudieron obtener las credenciales del usuario. Error: {e}')
    
    if not username or not password:
        print("Se requiere tanto el nombre de usuario como la contrasena")
        return 'Datos vacios'

    # Se realiza la conexion a la BD
    connect = conectar_bd()

    cursor = connect.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE name_usuario = ?", (username))
    usuario = cursor.fetchone()

    print(usuario)

    print(check_password_hash(usuario.pass_usuario, password))

    if usuario.user_eliminado == 1:

        print('Usuario deshabilitado')
        return jsonify({'message': 'Usuario deshabilitado'}),200
    
    if not usuario or not check_password_hash(usuario.pass_usuario, password):

        print("Contraseña almacenada en la base de datos:", usuario.pass_usuario)
        print("Contraseña proporcionada en el formulario:", password)

        return jsonify({'message': 'Usuario o clave invalida'}),200
    
    else:

        print(f"Log usuario: {username}")
        user_activo = True

        cursor.execute("UPDATE usuarios SET user_activo = ? WHERE name_usuario = ?", (user_activo, username))
        connect.commit()

        user_data = {

            'ID': usuario.ID,
            'username': usuario.name_usuario,
            'correo': usuario.correo_usuario,
            'password': usuario.pass_usuario,
            'role': usuario.rol
        }

        session['user_data'] = user_data

        print("Generando token.....")
        # Generar token JWT
        access_token = create_access_token(identity=user_data)
        
        cursor.close()
        connect.close()

        #return response
        return jsonify({'access_token': access_token, 'message': 'Inicio de sesión exitoso'}), 200
    

@app.route('/logout', methods=['POST'])
def logout():

    conn = conectar_bd()
    cursor = conn.cursor()

    # Crea una respuesta con una redirección a la página de inicio
    response = make_response()
    # Elimina el token de acceso de las cookies
    #response.set_cookie('access_token_cookie', '', expires=0)

    user_data = session["user_data"]
    username = user_data["username"]

    print(f'Usuario logout: {username}')

    user_activo = False

    cursor.execute("UPDATE usuarios SET user_activo = ? WHERE name_usuario = ?", (user_activo, username))
    conn.commit()

    session.clear()

    cursor.close()
    conn.close()
    
    return response

@app.route('/users')
@jwt_required()
def Usuarios():

    try:

        current_user = get_jwt_identity()
        #current_user = 'Administrador'
        print('Validando rol de usuario ...')

        if(current_user['role'] == 'Administrador'):
        #if(current_user == 'Administrador'):

            print('Conectandose a la BD ...')
            # Establecer la conexión a la base de datos
            conn = conectar_bd()
            # Crear un cursor para ejecutar consultas SQL
            cursor = conn.cursor()

            print('Obteniendo usuarios ...')
            # Consulta SQL para seleccionar los datos de los usuarios
            sql_query = "SELECT * FROM usuarios"

            # Ejecutar la consulta y obtener los resultados
            cursor.execute(sql_query)
            usuarios = cursor.fetchall()

            usuarios = [tuple(row) for row in usuarios]  # Convertir cada fila en un diccionario

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()

            #print(f'Usuario actual: {current_user["username"]}')

            #return render_template('agregarUsuario.html', usuarios = usuarios, current_user = current_user)
            return jsonify({'Usuarios': usuarios}), 200
        else:
            print("No tiene permisos para acceder a esta ruta!")
            #return render_template('login.html')
            return jsonify({'Acceso denegado'})
        
    except Exception as e:
        print(e)


@app.route('/add-user', methods=['POST'])
def AddUser():

    try:
        user_data = session.get('user_data')

        print(f'Data Usuario: {user_data}')

        if user_data and user_data["role"] == 'Administrador':

            try:

                username = request.form['username']
                password = request.form['password']
                role = request.form['role']
                correo = request.form['correo']

                print(f'Datos Recopilados del HTML: Usuario: {username}, Clave: {password}, Rol: {role}, correo: {correo}')

                # Generar el hash de la contraseña
                pass_hash = generate_password_hash(password)

                role_user = ''

                if role == "1":
                    role_user = 'Usuario'
                elif role == "2":
                    role_user = 'Administrador'
                else:
                    print("Error al definir rol de usuario. Rol no reconocido !")

            except Exception as e:

                print(f'Error: {e}')
                return 'Error al obtener los datos del usuario'

            try:
                conn = conectar_bd()
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM usuarios WHERE name_usuario = ?', (username,))
                if cursor.fetchone():

                    return 'El nombre de usuario ya está en uso'
     
                cursor.execute("INSERT INTO usuarios (name_usuario, pass_usuario, correo_usuario, user_activo, user_eliminado, rol) VALUES (?, ?, ?, ?, ?, ?)", (username, pass_hash,correo, 0, 0, role_user))

                # Confirmar los cambios y cerrar la conexión
                conn.commit()
                conn.close()

            except Exception as e:

                print(f'Error con la BD: {e}')
                return 'Error con la BD'

            return 'Validado'
        
        else:

            print('Sin privilegios')
            return 'Sin privilegios'
    
    except Exception as e:
        print(f'Error al crear usuario: {e}')
        return 'Error al crear usuario'
    
@app.route('/cambiar_rol/<int:idUsuario>', methods=['POST'])
def change_role(idUsuario):

    new_role = request.form.get('nuevoRol')

    try:
        # Establecer la conexión a la base de datos
        conn = conectar_bd()
        # Crear un cursor para ejecutar consultas SQL
        cursor = conn.cursor()

        # Consulta SQL para actualizar el estado del usuario
        sql_query = "UPDATE usuarios SET rol = ? WHERE ID = ?"
        cursor.execute(sql_query, (new_role, idUsuario))

        # Confirmar la transacción 
        conn.commit()

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        return "Rol modificado exitosamente"

    except Exception as e:

        print(f"Error al modificar rol: {e}")
        return "Error al modificar rol"

@app.route('/deshabilitar_usuario/<int:idUsuario>', methods=['POST'])
def deshabilitar_usuario(idUsuario):

    resultado = ''

    if request.method == 'POST':
        
        # Llamar a la función que actualiza el estado del usuario en la base de datos
        resultado = actualizar_estado_usuario(idUsuario, 1)
        print(resultado)
        return resultado
        
    else:
        resultado = 'Metodo no permitido !'
        return resultado
    

@app.route('/habilitar_usuario/<int:idUsuario>', methods=['POST'])
def habilitar_usuario(idUsuario):

    resultado = ''

    if request.method == 'POST':
        
        # Llamar a la función que actualiza el estado del usuario en la base de datos
        resultado = actualizar_estado_usuario(idUsuario, 0)
        print(resultado)
        return resultado
        
    else:
        resultado = 'Metodo no permitido !'
        return resultado
    
def actualizar_estado_usuario(idUsuario, estado):

    try:
        # Establecer la conexión a la base de datos
        conn = conectar_bd()
        # Crear un cursor para ejecutar consultas SQL
        cursor = conn.cursor()

        # Consulta SQL para actualizar el estado del usuario
        sql_query = "UPDATE usuarios SET user_eliminado = ? WHERE ID = ?"
        cursor.execute(sql_query, (estado, idUsuario))

        # Confirmar la transacción 
        conn.commit()

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        return "Usuario modificado exitosamente"
    
    except Exception as e:

        print(f"Error al modificar usuario: {e}")
        return "Error al modificar usuario"

@app.route('/reset-password', methods=['POST'])
def reset_password():

    username = request.form['username']

    if username:

        print(f'data: {username}')
        # Establecer la conexión a la base de datos

        try:

            conn = conectar_bd()
            #Crear un cursor para ejecutar consultas SQL
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM usuarios WHERE name_usuario = ?', (username,))
            usernameBD = cursor.fetchone()

            cursor.close()
            conn.close()

        except Exception as e:

            print(f'Error al validar usuario en la BD: {e}')
            return 'Error consultar en la BD.'

        # Valida que el usuario exista en la bd
        if usernameBD:

            print(usernameBD)
            codigo_verificacion = generar_codigo()

            session['verify_code'] = {

                'username': username, 
                'codigo':codigo_verificacion,
                'tiempo':datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Store the current time as a string

            }
           
            print(f'Codigo de verificacion: {codigo_verificacion}')

            # logica enviar correo con codigo .....

            destinatarios = [usernameBD.correo_usuario]

            # Asunto y mensaje
            asunto = "CODIGO DE VERIFICACION"
            
            mensaje = f"""<p>Estimado usuario:</p>
                        <p>Hemos recibido una solicitud para restablecer su contraseña en nuestra plataforma. Para continuar con este proceso, por favor ingrese el siguiente código de verificación en la página correspondiente:</p>
                        <p><b>Código de verificación: <h2>{codigo_verificacion}</h2></b></p>
                        <p>Gracias,<br>El equipo de Soporte</p>"""
            
            enviar_correo(destinatarios, asunto, mensaje)
            
            return 'Validado'
        
        else:

            print(f'Usuario no existe')
            return 'El Usuario no existe en la BD'

    else:

        return 'Error usuario'

def generar_codigo():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

@app.route('/verify-code', methods=['POST'])
def verify_code():

    code1 = request.form['code1']
    code2 = request.form['code2']
    code3 = request.form['code3']
    code4 = request.form['code4']
    code5 = request.form['code5']
    code6 = request.form['code6']

    code_verify = f'{code1}{code2}{code3}{code4}{code5}{code6}'
    print(f'Codigo Servidor: {session['verify_code']['codigo']}')
    print(f'Codigo HTML: {code_verify}')

    if session['verify_code']['codigo'] == code_verify:
        
        tiempo_emision = datetime.strptime(session['verify_code']['tiempo'], "%Y-%m-%d %H:%M:%S")

        if datetime.now() - tiempo_emision > timedelta(minutes=5):

            session.pop('verify_code', None)

            print('El código ha expirado.')

            return 'Expirado'
    
        #if session['verify_code']['tiempo']

        print('Codigo validado !')

        return 'Validado'

    else:

        print('Codigo no coinciden ... Intente nuevamente!')
        return 'Error'

@app.route('/change-password', methods=['POST'])
def change_password():

    password = request.form['password']

    if password:

        print(f'Nueva clave: {password}')

        # Generar el hash de la contraseña
        pass_hash = generate_password_hash(password)

        username = session['verify_code']['username']

        if username:

            print(f'Usuario a cambiar clave: {username}')

            try:

                conn = conectar_bd()
                # Crear un cursor para ejecutar consultas SQL
                cursor = conn.cursor()

                # Consulta SQL para actualizar el estado del usuario
                sql_query = "UPDATE usuarios SET pass_usuario = ? WHERE name_usuario = ?"
                cursor.execute(sql_query, (pass_hash, username))

                conn.commit()

                cursor.close()
                conn.close()
            
            except Exception as e:

                print(f'{e}')
                return f'Error al actualizar clave en la BD: {e}'

            session.pop('verify_code', None)

            return 'Validado'
        
        else:

            return 'Error'
        
    else:

        return 'Error'
    
if __name__ == "__main__":
    app.run(debug = True,host="0.0.0.0")