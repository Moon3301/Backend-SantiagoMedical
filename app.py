from flask import Flask,jsonify,make_response,render_template,request, session, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS,cross_origin
from datetime import timedelta, datetime, timezone
import requests,json,os,fnmatch,shutil
import time, locale
from connect_db_odbc import conectar_bd
from correoVerificacion import enviar_correo
import random
import string
import calendar

requests.packages.urllib3.disable_warnings()
app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
dt = datetime.now()

app.config['JWT_SECRET_KEY'] = 'admin1234'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=2)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Duración del token de actualización

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
        return jsonify({'message': 'No se puedieron obtener las credenciales de usuario.'}),400
    
    if not username or not password:
        print("Se requiere tanto el nombre de usuario como la contrasena")
        return jsonify({'message': 'No se indicaron las credenciales de acceso.'}),400

    # Se realiza la conexion a la BD
    connect = conectar_bd()

    cursor = connect.cursor()

    cursor.execute("SELECT * FROM accounts WHERE account_username = ?", (username))
    usuario = cursor.fetchone()

    print(usuario)

    print(check_password_hash(usuario.account_password, password))

    if usuario.account_active == 0:

        print('Usuario deshabilitado')
        return jsonify({'message': 'Usuario deshabilitado, porfavor contactese con el administrador.'}),400
    
    if not usuario or not check_password_hash(usuario.account_password, password):

        print("Contraseña almacenada en la base de datos:", usuario.account_password)
        print("Contraseña proporcionada en el formulario:", password)

        return jsonify({'message': 'Usuario o clave invalida'}),401
    
    else:

        print(f"Log usuario: {username}")
        user_activo = True

        cursor.execute("UPDATE accounts SET account_status = ? WHERE account_username = ?", (user_activo, username))
        connect.commit()

        cursor.execute("SELECT * from rol_accounts WHERE rol_ID = ?", (usuario.rol_ID))
        rol_name = cursor.fetchone()

        print(f'Rol: {rol_name.rol_nombre}')

        user_data = {

            'ID': usuario.account_ID,
            'username': usuario.account_username,
            'correo': usuario.account_email,
            'role': rol_name.rol_nombre
        }

        print("Generando token.....")
        # Generar token JWT
        access_token = create_access_token(identity=user_data)
        refresh_token = create_refresh_token(identity=user_data)

        # Calcula el tiempo actual en UTC
        tiempo_actual_utc = datetime.now(timezone.utc)

        # Suma 2 minutos al tiempo actual
        tiempo_futuro_utc = tiempo_actual_utc + timedelta(minutes=2)

        # Convierte a tiempo UNIX (segundos desde el epoch)
        tiempo_unix_utc = tiempo_futuro_utc.timestamp()

        # Redondea el tiempo UNIX
        access_token_expiration = round(tiempo_unix_utc)

        cursor.close()
        connect.close()

        #return response
        return jsonify({'access_token': access_token,
                        'message': 'Inicio de sesión exitoso',
                        'refresh_token': refresh_token,
                        'access_token_expiration': access_token_expiration
                        }), 200
    
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()

    # Calcula el tiempo actual en UTC
    tiempo_actual_utc = datetime.now(timezone.utc)

    # Suma 2 minutos al tiempo actual
    tiempo_futuro_utc = tiempo_actual_utc + timedelta(minutes=2)

    # Convierte a tiempo UNIX (segundos desde el epoch)
    tiempo_unix_utc = tiempo_futuro_utc.timestamp()

    # Redondea el tiempo UNIX
    access_token_expiration = round(tiempo_unix_utc)
   
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token':access_token, 'access_token_expiration':access_token_expiration})

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():

    try:

        print("Cerrando sesion...")

        print("Obteniendo credenciales de usuario ...")
        current_user = get_jwt_identity()

        print("Conectando a la BD ...")
        conn = conectar_bd()
        cursor = conn.cursor()

        # Crea una respuesta con una redirección a la página de inicio
        
        # Elimina el token de acceso de las cookies
        #response.set_cookie('access_token_cookie', '', expires=0)

        username = current_user["username"]
        print(f'Usuario logout: {username}')

        user_activo = False

        print("Actualizando estado de usuario en la BD ...")
        cursor.execute("UPDATE accounts SET account_status = ? WHERE account_username = ?", (user_activo, username))

        print("Guardando cambios ...")
        conn.commit()

        print("Cerrando conexion de la BD ...")
        cursor.close()
        conn.close()

    except Exception as e:

        print(e)
        jsonify({'message': 'Error al cerrar sesion, intentelo nuevamente'})

    return jsonify({'message': 'Sesion terminada con exito'})

@app.route('/users')
@jwt_required()
def Usuarios():

    try:

        current_user = get_jwt_identity()
        #current_user = 'Administrador'
        print('Validando rol de usuario ...')

        if(current_user["role"] == 'Administrador'):
        #if(current_user == 'Administrador'):

            print('Conectandose a la BD ...')
            # Establecer la conexión a la base de datos
            conn = conectar_bd()
            # Crear un cursor para ejecutar consultas SQL
            cursor = conn.cursor()

            print('Obteniendo usuarios ...')
            # Consulta SQL para seleccionar los datos de los usuarios
            sql_query = "SELECT * FROM accounts"

            # Ejecutar la consulta y obtener los resultados
            cursor.execute(sql_query)
            usuarios = cursor.fetchall()

            # Convertir los resultados en un formato JSON más legible
            usuarios_json = []
            for usuario in usuarios:
                usuario_dict = {
                    "ID": usuario[0],
                    "username": usuario[1],
                    "password": usuario[2],
                    "account_status": usuario[3],
                    "account_active": usuario[4],
                    "rol_ID": usuario[5],
                    "account_email": usuario[6]
                }
                usuarios_json.append(usuario_dict)

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()

            return jsonify({'message':'Acceso otorgado','usuarios': usuarios_json}), 200
        
        else:

            print("No tiene permisos para acceder a esta ruta.")
            #return render_template('login.html')
            return jsonify({'message':'Acceso denegado'}), 401
        
    except Exception as e:
        print(e)
        return jsonify({'message':'Error al obtener los datos de usuarios.'}), 401


@app.route('/add-user', methods=['POST'])
@jwt_required()
def AddUser():

    current_user = get_jwt_identity()

    try:

        print(f'Data Usuario: {current_user['username']} : {current_user}')

        if current_user['role'] == 'Administrador':

            try:

                username = request.json['username']
                password = request.json['password']
                role = request.json['role']
                correo = request.json['correo']

                print(f'Datos Recopilados del HTML: Usuario: {username}, Clave: {password}, Rol: {role}, correo: {correo}')

                # Generar el hash de la contraseña
                pass_hash = generate_password_hash(password)

                role_user = ''

                if role == "Administrador":
                    role_user = 'Administrador'
                elif role == "Usuario":
                    role_user = 'Usuario'
                else:
                    print("Error al definir rol de usuario. Rol no reconocido !")
                    return jsonify({'message':'Error al definir rol de usuario. Rol no reconocido.'}), 400

            except Exception as e:

                print(f'Error: {e}')
                return jsonify({'message':'Error al obtener los datos del usuario.'}), 400
            
            try:
                
                conn = conectar_bd()
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM usuarios WHERE name_usuario = ?', (username,))
                if cursor.fetchone():

                    return jsonify({'message':'El nombre de usuario ya está en uso.'}), 400

                cursor.execute("INSERT INTO usuarios (name_usuario, pass_usuario, correo_usuario, user_activo, user_eliminado, rol) VALUES (?, ?, ?, ?, ?, ?)", (username, pass_hash,correo, 0, 0, role_user))

                # Confirmar los cambios y cerrar la conexión
                conn.commit()
                conn.close()

            except Exception as e:

                print(f'Error con la BD: {e}')
                return jsonify({'message':'Error con la BD.'}), 400

            return jsonify({'message':'Validado.'}), 200
        
        else:

            print('Sin privilegios')
            return jsonify({'message':'Sin privilegios.'}), 401
    
    except Exception as e:
        print(f'Error al crear usuario: {e}')
        return jsonify({'message':'Error al crear usuario.'}), 400
    
@app.route('/cambiar_rol/<int:idUsuario>', methods=['POST'])
@jwt_required()
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

        return jsonify({'message':'Rol modificado exitosamente.'}), 200
    
    except Exception as e:

        print(f"Error al modificar rol: {e}")
        return jsonify({'message':'Error al modificar rol.'}), 200

@app.route('/deshabilitar_usuario/<int:idUsuario>', methods=['POST'])
@jwt_required()
def deshabilitar_usuario(idUsuario):

    resultado = ''

    if request.method == 'POST':
        
        # Llamar a la función que actualiza el estado del usuario en la base de datos
        
        resultado = actualizar_estado_usuario(idUsuario, 1)
        print(resultado)
        return jsonify({'message':resultado}), 200
         
    else:

        resultado = 'Metodo no permitido.'
        return jsonify({'message':resultado}), 400
    

@app.route('/habilitar_usuario/<int:idUsuario>', methods=['POST'])
@jwt_required()
def habilitar_usuario(idUsuario):

    resultado = ''

    if request.method == 'POST':
        
        # Llamar a la función que actualiza el estado del usuario en la base de datos
        resultado = actualizar_estado_usuario(idUsuario, 0)
        print(resultado)
        return jsonify({'message':resultado}), 200
        
    else:

        resultado = 'Metodo no permitido.'
        return jsonify({'message':resultado}), 400
    
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

    username = request.json['username']

    if username:

        print(f'data: {username}')
        # Establecer la conexión a la base de datos

        try:

            conn = conectar_bd()
            #Crear un cursor para ejecutar consultas SQL
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM accounts WHERE account_username = ?', (username,))
            usernameBD = cursor.fetchone()

        except Exception as e:

            print(f'Error al validar usuario en la BD: {e}')
            return jsonify({'message':'Error consultar en la BD.'}), 400

        # Valida que el usuario exista en la bd
        if usernameBD:

            print(usernameBD)
            codigo_verificacion = generar_codigo()

            cursor.execute("INSERT INTO codigos_verificacion (account_ID, cod_codigo, cod_tiempo_emision) VALUES (?, ?, ?)",
                               (usernameBD.account_ID, codigo_verificacion, datetime.now()))

            conn.commit()
            conn.close()
           
            print(f'Codigo de verificacion: {codigo_verificacion}')
            accountID = usernameBD.account_ID
            # logica enviar correo con codigo .....

            destinatarios = [usernameBD.account_email]

            # Asunto y mensaje
            asunto = "CODIGO DE VERIFICACION"
            
            mensaje = f"""<p>Estimado usuario:</p>
                        <p>Hemos recibido una solicitud para restablecer su contraseña en nuestra plataforma. Para continuar con este proceso, por favor ingrese el siguiente código de verificación en la página correspondiente:</p>
                        <p><b>Código de verificación: <h2>{codigo_verificacion}</h2></b></p>
                        <p>Gracias,<br>El equipo de Soporte</p>"""
            
            enviar_correo(destinatarios, asunto, mensaje)
            
            return jsonify({'message':'Validado', 'account_ID':accountID}), 200
        
        else:

            print(f'Usuario no existe')
            return jsonify({'message':'El Usuario no existe en la BD'}), 400

    else:

        return jsonify({'message':'Error al obtener el nombre de usuario'}), 400

def generar_codigo():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

@app.route('/verify-code', methods=['POST'])
def verify_code():

    code_verify = request.json['code_verify']
    accountID = request.json['accountID']

    print(f'Codigo verificacion obtenido: {code_verify}')
    print(f'accountID: {accountID}')

    try:

        conn = conectar_bd()
        cursor = conn.cursor()

        # Buscar el código de verificación en la base de datos
        cursor.execute('SELECT * FROM codigos_verificacion WHERE account_ID = ? AND cod_codigo = ?', (int(accountID), code_verify))
        codigo_bd = cursor.fetchone()

        if codigo_bd:

            tiempo_emision = codigo_bd[3]

            print(f'Tiempo de emsision obtenido desde la BD: {tiempo_emision}')

            # Convertir el string de tiempo en un objeto datetime
            # Convertir el string de tiempo en un objeto datetime sin microsegundos
            
            if datetime.now() - tiempo_emision > timedelta(minutes=5):
                # El código ha expirado
                return jsonify({'message':'Expirado'}), 401
            
            else:
                # El código es válido
                return jsonify({'message':'Validado'}), 200
            
        else:
            # El código no coincide
           
            return jsonify({'message':'Codigo incorrecto'}), 401
        
    except Exception as e:

        print(f'Error al verificar el código en la BD: {e}')
        return jsonify({'message':'Error al verificar el código'}), 400

@app.route('/change-password', methods=['POST'])
def change_password():

    password = request.json['password']
    password_rep = request.json['reppassword']

    username = request.json['username']

    if password == password_rep:
        print('Las claves coinciden ..')

    if password:

        print(f'Nueva clave: {password}')

        # Generar el hash de la contraseña
        pass_hash = generate_password_hash(password)

        if username:

            print(f'Usuario a cambiar clave: {username}')

            try:

                conn = conectar_bd()
                # Crear un cursor para ejecutar consultas SQL
                cursor = conn.cursor()

                # Consulta SQL para actualizar el estado del usuario
                sql_query = "UPDATE accounts SET account_password = ? WHERE account_username = ?"
                cursor.execute(sql_query, (pass_hash, username))

                conn.commit()

                cursor.close()
                conn.close()
            
            except Exception as e:

                print(f'{e}')
                return jsonify({'message':'Error al actualizar clave en la BD'}), 400
            
            return jsonify({'message':'Validado'}), 200
        
        else:

            return jsonify({'message':'No se pudo obtener el usuario'}), 400
        
    else:

        return jsonify({'message':'No se pudo validar la contrasena, intentelo nuevamente.'}), 400
    
if __name__ == "__main__":
    app.run(debug = True)