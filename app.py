from flask import Flask,jsonify,make_response,render_template,request, send_file, session, redirect, url_for,  send_from_directory, Response
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended import JWTManager
import psutil
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS,cross_origin
from datetime import timedelta, datetime, timezone
import requests,json,os,fnmatch,shutil
import time, locale
from connect_db_odbc import conectar_bd
from correoVerificacion import enviar_correo, enviar_correo_verificacion
import random
import string
import sys
import calendar
import xlwings as xw
from openpyxl import load_workbook
from exchangelib import Credentials, Account, Message, Mailbox, FileAttachment

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from renameFile import changeNameFile
from flask import send_from_directory
from flask_socketio import SocketIO, emit
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from selenium.common.exceptions import NoSuchElementException

from apscheduler.schedulers.background import BackgroundScheduler

# test logs
import logging

requests.packages.urllib3.disable_warnings()
app = Flask(__name__)

# Configuración básica de logging
file_handler = logging.FileHandler('flask_app.log')
file_handler.setLevel(logging.DEBUG)  # Ajusta el nivel de logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)

CORS(app, resources={r"/*": {"origins": "*", "methods": ["POST", "GET"]}})

socketio = SocketIO(app, cors_allowed_origins="*", methods=['GET', 'POST'])

locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
dt = datetime.now()

app.config['JWT_SECRET_KEY'] = 'admin1234'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Duración del token de actualización

app.secret_key = 'admin1234'

jwt = JWTManager(app)

dir_download = "C:\\Users\\Administrador\\Desktop\\Test\\Backend-SantiagoMedical\\static\\files\\"

listCookies = [
    {"name":"cookies1.json", "state":True},
    {"name":"cookies2.json", "state":True},
    {"name":"cookies3.json", "state":True},
    {"name":"cookies4.json", "state":True},
    {"name":"cookies5.json", "state":True}
]

# Definir un prefijo raíz
base_route = "/flask"

URL_NODE = 'https://presupuestos.santiagomedical.cl/node/express/myapp'

path_to_chromedriver = "C:\\Users\\Administrador\\Desktop\\chromedriver-win64\\chromedriver.exe" # actualiza esto con tu ruta

@socketio.on('connect')
def test_connect():
    print('Client connected to flask')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected to flask')

@socketio.on('budget_changed')
def handle_budget_changed(data):
    print('Cambio de presupuesto recibido:', data)
    # Aquí puedes actualizar tus componentes con los nuevos datos
    socketio.emit('budget_changed', data)

@app.route(f"{base_route}")
def hello_world():
    return "<p>API FLASK - SANTIAGO MEDICAL</p>"

def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(window_size)

def switch_to_correct_frame(browser, frame_xpath):
    try:
        # Intenta cambiar al marco deseado
        browser.switch_to.frame(browser.find_element(By.XPATH, frame_xpath))
        return True
    except NoSuchElementException:
        print("El frame deseado no se encontró.")
        return False

def cargaPrestaciones(b,prestacion,precio,horas,dataView):

    if (int(precio) != 0):
        if(int(horas) != 0):
            
            nombre_prestacion =  b.find_element(By.XPATH,'//*[@id="query"]')
            b.execute_script("arguments[0].scrollIntoView();", nombre_prestacion)
            nombre_prestacion.send_keys(prestacion)
            #b.execute_script("arguments[0].value = arguments[1];", nombre_prestacion, prestacion)
            #b.find_element(By.XPATH,'//*[@id="query"]').send_keys(prestacion)
            time.sleep(1)
            if prestacion == 'Honorarios Medicos':
                b.find_element(By.XPATH,'//*[@id="invoice_item_manager_buscar"]/div[1]/ul/li[3]/a').click()
            else:
                b.find_element(By.XPATH,'//*[@id="invoice_item_manager_buscar"]/div[1]/ul/li[1]/a').click()
           

            agregar_buscar = b.find_element(By.XPATH,'//*[@id="agregar_buscar"]')
            #b.execute_script("arguments[0].scrollIntoView();", agregar_buscar)
            agregar_buscar.click()
            #b.execute_script("arguments[0].click();", agregar_buscar)

def kill_chrome_processes():
    os.system("taskkill /f /im chrome.exe")
    os.system("taskkill /f /im chromedriver.exe")

def is_chromedriver_running():
    # Itera sobre todos los procesos en ejecución
    for proc in psutil.process_iter(['pid', 'name']):
        # Comprueba si el nombre del proceso es 'chromedriver'
        if proc.info['name'] == 'chromedriver.exe':
            return True
    return False

@app.route(f'{base_route}/start_scrapping', methods=["POST"])
def start_bot_selenium_4_TEST():
    data = request.json

    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        response = requests.post('http://192.168.4.3:80/scrapping_santiagomedical', json=data, timeout=900)
        response.raise_for_status()  # Lanza una excepción si la respuesta contiene un código de estado HTTP de error

    except requests.exceptions.HTTPError as http_err:
        # Manejo específico para diferentes códigos de estado HTTP
        if response.status_code == 400:
            return jsonify({'message': 'Bad Request'}), 400
        elif response.status_code == 401:
            return jsonify({'message': 'Unauthorized'}), 401
        elif response.status_code == 404:
            return jsonify({'message': 'Not Found'}), 404
        elif response.status_code == 500:
            return jsonify({'message': 'Internal Server Error'}), 500
        else:
            return jsonify({'message': f'HTTP error occurred: {http_err}'}), response.status_code

    except requests.exceptions.RequestException as err:
        return jsonify({'message': f'Error occurred: {err}'}), 500

    try:
        response_data = response.json()

        message = response_data.get('message', 'No message')
        pre_id = response_data.get('pre_id', 'No pre_id')
        filename = response_data.get('filename', 'No filename')
        cookie_name = response_data.get('cookie_name', 'No cookie')

        if response.status_code == 200:
            return jsonify({
                'message': message,
                'pre_id': pre_id,
                'filename': filename,
                'cookie_name': cookie_name
            })

    except ValueError:  # Incluye json.JSONDecodeError
        return jsonify({'message': f'Invalid JSON response: {response.text}'}), 500


def save_cookies(browser, name_cookie):
    # Ruta al archivo
    file_path = name_cookie

    # Verifica si el archivo existe
    if os.path.exists(file_path):
        # Si existe, lo borra
        os.remove(file_path)

    time.sleep(1)

    # Guardar las cookies en un archivo
    with open(file_path, 'w') as file:
        json.dump(browser.get_cookies(), file)

    time.sleep(1)

    for cookie in listCookies:
        if cookie["name"] == name_cookie:
            cookie['state'] = True

def verifyAvaliableCookie():
    
    for cookie in listCookies:

        state = cookie['state']

        if(state == True):
            cookie['state'] = False
            print(listCookies)
            print(cookie)
            return cookie

def break_captcha_medilink():

    for item in listCookies:

        try:
                                
            logging.info("Cargando navegador")
            
            # Opciones del navegador
            chrome_options = Options()
            #chrome_options.add_argument('--headless') 
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            #chrome_options.add_experimental_option("detach", True)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-browser-side-navigation')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--auto-open-devtools-for-tabs')
            chrome_options.add_argument("--disable-background-networking")
            
        except Exception as e:

            logging.info("Error al configurar instancia de ChromeDriver")
            return jsonify({'message':'Error al configurar instancia de ChromeDriver'}), 400
        
        #browserTest = webdriver.Chrome(options=chrome_options)
        with webdriver.Chrome(options=chrome_options) as browserTest:

            try:
                browserTest.execute_script("window.open('http://santiagomedical.new.softwaremedilink.com/sessions/login', '_blank')")
                time.sleep(15)
                
                # Cambia la pagina de medilink
                browserTest.switch_to.window(browserTest.window_handles[1])

                # Se posiciona sobre el frame de CloudFlare
                browserTest.switch_to.frame(0)

                #Presionar el ckeck de validacion CloudFlare
                browserTest.find_element(By.XPATH, '//*[@id="challenge-stage"]/div/label/input').click()
                time.sleep(1)
                
                # Vuelve al contexto del frame principal
                browserTest.switch_to.default_content()

                # Se obtienen los inputs de usuario y contrasena
                eUser = browserTest.find_element(By.XPATH,'//*[@id="login-form"]/div/div[1]/input')
                ePassword = browserTest.find_element(By.XPATH,'//*[@id="login-form"]/div/div[2]/input')

                # Se obtiene el boton para iniciar sesion
                eButton = browserTest.find_element(By.XPATH,'//*[@id="login-form"]/div/input')

                # Se insertan las credenciales de acceso en los inputs
                eUser.send_keys('mvalenzuela')
                ePassword.send_keys('mvalenzuela')

                time.sleep(1)
                # Presionar el boton iniciar sesion con las credenciales de acceso
                eButton.click()
                time.sleep(1)
                
                browserTest.get("https://santiagomedical.new.softwaremedilink.com/")

                time.sleep(2)

                name_cookie = item['name']
                save_cookies(browserTest, name_cookie)

            except:
                
                return jsonify({'message':'Error al resolver captcha web medilink'}), 400
            
            finally:
                
                # Cerrar el navegador
                browserTest.quit()
                time.sleep(1)
                if not is_chromedriver_running():
                
                    kill_chrome_processes()
                else:
                    print('Ya existe una ejecucion de chrome Activa')
    
@app.route(f'{base_route}/start_scrappingTEST',methods=["POST"])
def start_bot_selenium_4():

    try:

        data = request.json

        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        dataView = data["pre_id"]
        presupuesto = data["presupuesto"]
        presupuestoPaciente = data["presupuestoPaciente"]
        presupuestoMedico = data["presupuestoMedico"]
        presupuestoCirugia = data["presupuestoCirugia"]
        presupuestoVaser = data["presupuestoVaser"]
        presupuestoAnestesia = data["presupuestoAnestesia"]
        presupuestoRecuperacion = data["presupuestoRecuperacion"]

        max_retries = 3  # Número máximo de reintentos
        retries = 0

        # Se obtiene el ID del presupuesto a ingresar
        logging.info(f'dataView: {dataView}')

        # Se define la variable myobj y se le asigna el ID del presupuesto
        myobj = {"pre_id":dataView}

        y = presupuestoPaciente[0]
        logging.info(f'Obteniendo registro de presupuesto paciente: {y}')

        yP = presupuesto
        logging.info(f'Obteniendo registro de presupuesto: {yP}')
    
    except Exception as e:

        logging.info(f'Error al cargar registros de presupuesto. Verifique los datos ingresados.: {e}')
        return jsonify({'message':'Error al cargar registros de presupuesto. Verifique los datos ingresados.'}), 400

    
    # Define la configuracion para la isntancia del navegador: Desactiva el visor PDF (para descargar automaticamente en lugar de abrirse en el navegador)
    profile = {"plugins.always_open_pdf_externally": True, # Disable Chrome's PDF Viewer
                "download.default_directory": dir_download + str(dataView) , "download.extensions_to_open": "applications/pdf"}
    
    try:
                                
        logging.info("Cargando navegador")
        
        
        # Opciones del navegador
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", profile)
        #chrome_options.add_argument('--headless') 
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        #chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--auto-open-devtools-for-tabs')
        chrome_options.add_argument("--disable-background-networking")
        
    except Exception as e:

        logging.info("Error al configurar instancia de ChromeDriver")
        return jsonify({'message':'Error al configurar instancia de ChromeDriver'}), 400
    
    #browserTest = webdriver.Chrome(options=chrome_options)
    with webdriver.Chrome(options=chrome_options) as b:

        
        try:
            b.execute_script("window.open('http://santiagomedical.new.softwaremedilink.com/sessions/login', '_blank')")
            time.sleep(15)
            
            # Cambia la pagina de medilink
            b.switch_to.window(b.window_handles[1])

            # Se posiciona sobre el frame de CloudFlare
            b.switch_to.frame(0)

            #Presionar el ckeck de validacion CloudFlare
            b.find_element(By.XPATH, '//*[@id="challenge-stage"]/div/label/input').click()
            time.sleep(1)
            
            # Vuelve al contexto del frame principal
            b.switch_to.default_content()

            # Se obtienen los inputs de usuario y contrasena
            eUser = b.find_element(By.XPATH,'//*[@id="login-form"]/div/div[1]/input')
            ePassword = b.find_element(By.XPATH,'//*[@id="login-form"]/div/div[2]/input')

            # Se obtiene el boton para iniciar sesion
            eButton = b.find_element(By.XPATH,'//*[@id="login-form"]/div/input')

            # Se insertan las credenciales de acceso en los inputs
            eUser.send_keys('mvalenzuela')
            ePassword.send_keys('mvalenzuela')

            time.sleep(1)
            # Presionar el boton iniciar sesion con las credenciales de acceso
            eButton.click()
            time.sleep(2)
         
        except:
            
            b.close()
            time.sleep(1)

            return jsonify({'message':'Error al resolver captcha web medilink'}), 400
        
        try:
            
            b.get('https://santiagomedical.new.softwaremedilink.com/')

            time.sleep(1)

            # Se define la variable b y se le asigna la variable de la intancia del navegador
            
            # Se elimina el directorio definido en la ruta, ignorando cualquier error ocurrido durante la eliminacion.
            logging.info("Eliminando directorio definido en la ruta ./static/files/'+str(dataView)") 
            shutil.rmtree('./static/files/'+str(dataView), ignore_errors=True)

            logging.info("asignando directorio")
            directory = str(dataView)
            parent_dir = './static/files/'
            pathFolder = os.path.join(parent_dir, directory)
            os.mkdir(pathFolder)

            logging.info("Buscando paciente ...")
            searchPaciente = b.find_element(By.XPATH,'//*[@id="buscador-header"]')

            logging.info("Obteniendo rut del paciente ...")
            
            if  y and len(y) > 0:
                searchRut = y["prepa_rut"][:-2]
                logging.info("Rut truncado:", searchRut)
            else:
                paciente = presupuestoPaciente[0]
                logging.info("Error: 'presupuestoPaciente' está vacío o no es una lista.")
                return jsonify({'message':f'Prespuesto paciente esta vacio o no es una lista. paciente: {paciente["prepa_rut"][:-2]}, presupuesto: {presupuesto}, presupuestoPaciente: {presupuestoPaciente}'}), 400

            searchPaciente.send_keys(searchRut)
            logging.info("Ingresando rut en input del buscador ...")
            time.sleep(4)
            logging.info("Sacando Screenshot de pantalla")
            
            largoPacientes = b.execute_script("return document.querySelectorAll('body > div.navbar- > div > div > table > tbody > tr > td:nth-child(2) > div > ul > li').length")
            
            if largoPacientes > 2:
                time.sleep(3)
                b.find_element(By.XPATH,'/html/body/div[13]/div/div/table/tbody/tr/td[2]/div/ul/li[1]/a').click()
                
            else:
                
                time.sleep(3)
                b.get('https://santiagomedical.new.softwaremedilink.com/clientes')
                
                time.sleep(2)
                b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[1]/div[1]/div/div[1]/a').click()
                
                b.execute_script("document.querySelector('#nombre').id = 'apellido'")
                b.find_element(By.XPATH,'//*[@id="apellido"]').send_keys(y["prepa_nombre"])
                b.find_element(By.XPATH,'//*[@id="nombre"]').send_keys(y["prepa_apellido"])
                b.find_element(By.XPATH,'//*[@id="rut"]').send_keys(y["prepa_rut"])
                
                elemento_email = b.find_element(By.XPATH,'//*[@id="email-form"]')

                # Borrar el contenido previo
                elemento_email.clear()

                # Obtener el nuevo email_cargado (como en tu código anterior)
                email_cargado = y["prepa_email"]
                if len(email_cargado) == 0:
                    email_cargado = "email@sanatorio.com"

                # Enviar el nuevo contenido
                elemento_email.send_keys(email_cargado)
                
                b.execute_script('document.querySelector("#sexo").value = "{}"'.format(y["prepa_sexo"]))
                
                b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[1]/div/form/div[11]/div/input').send_keys(y["prepa_direccion"])
                ciudad_input = b.find_element(By.NAME,'ciudad')
                ciudad_input.send_keys("Ciudad Ejemplo")
                comuna_input = b.find_element(By.NAME,'comuna')
                comuna_input.send_keys("Comuna Ejemplo")
                telefono_input = b.find_element(By.ID,'celular')
                telefono_input.send_keys(y["prepa_celular"])

                b.find_element(By.XPATH,'//*[@id="siguiente"]').click()
                
                b.get('https://santiagomedical.new.softwaremedilink.com/')
                
                searchPaciente = b.find_element(By.XPATH,'//*[@id="buscador-header"]')
                searchPaciente.send_keys(searchRut)
                time.sleep(4)
                
                b.find_element(By.XPATH,'/html/body/div[13]/div/div/table/tbody/tr/td[2]/div/ul/li[1]/a').click()
                
            b.find_element(By.XPATH,'//*[@id="section_content"]/div[2]/div[1]/div[1]/div/div/div[3]/a').click()
            b.find_element(By.XPATH,'//*[@id="section_content"]/div[2]/div[1]/div[1]/div/div/div[3]/ul/li[9]/a').click()
            
            yMed = presupuestoMedico[0]

            atencion = yMed["premed_valor"]
            medico = yMed["pro_ID"]

            if medico == 27:
                medico = 69

            findAtencion = b.find_element(By.XPATH,'//*[@id="nombre-atencion"]')
            
            findAtencion.send_keys(atencion)

            b.execute_script("document.querySelector('#nuevo-inmediato > div.modal-body > select').value = {}".format(medico))

            b.find_element(By.XPATH,'//*[@id="nuevo-inmediato"]/div[3]/a[1]').click()
            b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div[1]/a[2]').click()
            b.find_element(By.XPATH,'//*[@id="client-sidebar"]/div[6]/div[1]/a').click()

            datosTratamiento = b.execute_script(open('./validaTratamiento.js').read())
            datosSplit = datosTratamiento.split()

            secitionAtenciones = b.execute_script(open('./sectionAtenciones.js').read())
            logging.info(secitionAtenciones)

            if secitionAtenciones == 'PRÓXIMA ATENCIÓN':
                b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[2]').click() 
                
            else:
                if datosSplit[0] == 'Procedimiento':    
                    print(b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[2]/div[2]/table/tbody/tr[1]/td/div').text.strip().split()[0])            
                    if b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[2]/div[2]/table/tbody/tr[1]/td/div').text.strip().split()[0] == 'Procedimiento':
                        b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[3]').click()     
                        
                    else:
                        b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[2]').click()     
                        
                elif datosSplit[0] == 'Consulta':      
                    b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[2]').click() 
                    
                else:
                    b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[6]/div[1]/div[2]/ul/li[1]').click()
            
            b.find_element(By.XPATH,'//*[@id="display_consulta"]/div/div[14]/div/a').click()
            
            time.sleep(1)

            success_button = b.find_element(By.XPATH, '//*[@id="cargar-prestaciones-success"]')

            yCir = presupuestoCirugia
        
            yVase = presupuestoVaser
            
            yAne = presupuestoAnestesia
         
            yRec = presupuestoRecuperacion
         
            print("Cargando prestaciones ...")
            
            for i in yCir:

                cargaPrestaciones(b,i["precir_nombre"],int(i["precir_precio"]),int(i["precir_horas"]),dataView)
            
            for i in yAne:
                cargaPrestaciones(b,i["preane_nombre"],i["preane_precio"],i["preane_horas"],dataView)

            for i in yRec:
                cargaPrestaciones(b,i["prerec_nombre"],i["prerec_precio"],i["prerec_horas"],dataView)
            
            for i in yVase:
                cargaPrestaciones(b,i["preva_nombre"],i["preva_precio"],i["preva_horas"],dataView)
            
            time.sleep(1)

            # Desplazarse hasta el botón para asegurarse de que esté visible
            b.execute_script("arguments[0].scrollIntoView(true);", success_button)
            # Hacer clic en el botón
            success_button.click()

            time.sleep(1)

            datosM = b.execute_script(open('./index.js').read())

            if not datosM:
                print('error')
                return jsonify({'message':'Error al cargar datosM.'}), 400

            descuentoFlag = 20
          
            for i,idx in enumerate(yCir):
                yCir[i].update({'precir_flag': False})

            for i in yCir:
                
                for j in datosM:

                    str2 = j["nombre"].replace(u'Más Información','')
                    str3 = str2.replace(u'Eliminar','')
                    str4 = str3.replace(u'-','').strip()

                    strD = i["precir_nombre"].replace(u'-','').strip()            
                    
                    if str4 == '210409300 INSUMOS TUNEL CARPEANO':
                        if str4 == strD and int(descuentoFlag) != int(i['precir_descuento']):
                            descuentoFlag = i['precir_descuento']
                            
                            if i["precir_flag"]:                
                                
                                precioZ = int(i["precir_precio"])
                            else:
                                
                                precioZ = int(i["precir_precio"])
                            print('CODIGO',j["codigo"],'PRECIOS:',int(precioZ),int(j["precio"])) 
                            if(int(precioZ) != 0):
                                if int(j["precio"]) != int(precioZ):
                                    
                                    time.sleep(1)
                                    b.execute_script('togglePrecio("{}")'.format(j["codigo"]))
                                    time.sleep(1)
                                    b.execute_script('document.querySelector("#precio_field_accion_{}").value = "{}"'.format(j["codigo"],int(precioZ)))
                                    b.execute_script('updatePrecioDetalle("precio_field_accion_{}","{}","isIntegerZero");'.format(j["codigo"],j["codigo"]))
                                
                                if int(j["descuento"]) != int(i["precir_descuento"]):
                                
                                    time.sleep(1)
                                    b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                    time.sleep(1)
                                    print(len(str(i["precir_descuento"])))
                                    if len(str(i["precir_descuento"])) <= 1:
                                        b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.0{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                    else:
                                        b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                    
                                    b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))
                    else:

                        if str4 == strD:
                            descuentoFlag = i['precir_descuento']
                            
                            if i["precir_flag"]:                
                                
                                precioZ = i["precir_precio"]
                            else:
                                
                                precioZ = i["precir_precio"]
                            
                            if(precioZ != 0):
                                if int(j["precio"]) != precioZ:
                                    
                                    time.sleep(1)
                                    b.execute_script('togglePrecio("{}")'.format(j["codigo"]))
                                    time.sleep(1)

                                    b.execute_script('document.querySelector("#precio_field_accion_{}").value = "{}"'.format(j["codigo"],precioZ))
                                    b.execute_script('updatePrecioDetalle("precio_field_accion_{}","{}","isIntegerZero");'.format(j["codigo"],j["codigo"]))
                                
                                if int(j["descuento"]) != i["precir_descuento"]:
                                
                                    time.sleep(1)
                                    b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                    time.sleep(1)
                                    
                                    if len(str(i["precir_descuento"])) <= 1:
                                        b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.0{}"'.format(j["codigo"],i["precir_descuento"]))
                                    else:
                                        b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],i["precir_descuento"]))
                                    
                                    b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))
            
            # Verificar que presupuestoAnestesia no esté vacío
            if len(yAne) > 0:
                anestesia_message = "presupuestoAnestesia no está vacía"
                
                for i in yAne:
                    for j in datosM:
                        str2 = j["nombre"].replace(u'Más Información','')
                        str3 = str2.replace(u'Eliminar','')
                        str4 = str3.replace(u'-','').strip()
                        strD = i["preane_nombre"].replace(u'-','').strip()
                        if str4 == strD:
                            
                            precioF = int(i["preane_precio"])
                            
                            if(int(precioF) != 0):
                                if int(j["precio"]) != int(precioF):
                                    time.sleep(1)
                                    b.execute_script('togglePrecio("{}")'.format(j["codigo"]))
                                    time.sleep(1)
                                    b.execute_script('document.querySelector("#precio_field_accion_{}").value = "{}"'.format(j["codigo"],int(precioF)))
                                    b.execute_script('updatePrecioDetalle("precio_field_accion_{}","{}","isIntegerZero");'.format(j["codigo"],j["codigo"]))
                                if int(j["descuento"]) != int(i["preane_descuento"]):
                                    time.sleep(1)
                                    b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                    time.sleep(1)
                                    b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["preane_descuento"])))
                                    b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))

            for i in yVase:
                for j in datosM:
                    str2 = j["nombre"].replace(u'Más Información','')
                    str3 = str2.replace(u'Eliminar','')
                    str4 = str3.replace(u'-','').strip()
                    strD = i["preva_nombre"].replace(u'-','').strip()
                    if str4 == strD:
                        
                        precioF = int(i["preva_precio"])
                        
                        if(int(precioF) != 0):
                            if int(j["precio"]) != int(precioF):
                                time.sleep(1)
                                b.execute_script('togglePrecio("{}")'.format(j["codigo"]))
                                time.sleep(1)
                                b.execute_script('document.querySelector("#precio_field_accion_{}").value = "{}"'.format(j["codigo"],int(precioF)))
                                b.execute_script('updatePrecioDetalle("precio_field_accion_{}","{}","isIntegerZero");'.format(j["codigo"],j["codigo"]))
                            if int(j["descuento"]) != int(i["preva_descuento"]):
                                time.sleep(1)
                                b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                time.sleep(1)
                                b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["preva_descuento"])))
                                b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))
        
            for i in yRec:
                
                for j in datosM:
                    
                    str2 = j["nombre"].replace(u'Más Información','')
                    str3 = str2.replace(u'Eliminar','')
                    str4 = str3.replace(u'-','').strip()
                    strD = i["prerec_nombre"].replace(u'-','').strip()
                    if str4 == strD:
                        precioX = int(i["rec_precio"]) * int(i["prerec_horas"])
                        if(int(precioX) != 0):
                            if int(j["precio"]) != int(precioX):
                                time.sleep(1)
                                b.execute_script('togglePrecio("{}")'.format(j["codigo"]))
                                time.sleep(1)
                                b.execute_script('document.querySelector("#precio_field_accion_{}").value = "{}"'.format(j["codigo"],int(precioX)))
                                b.execute_script('updatePrecioDetalle("precio_field_accion_{}","{}","isIntegerZero");'.format(j["codigo"],j["codigo"]))
                            if int(j["descuento"]) != int(i["prerec_descuento"]):
                                time.sleep(1)
                                b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                time.sleep(1)
                                b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["prerec_descuento"])))
                                b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))

            time.sleep(5)
            
            b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div/div[2]/ul/li[2]/a').click()
            b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div/div[2]/ul/li[2]/ul/li[1]/a').click()

            time.sleep(10)
        
            f = changeNameFile(dataView)

            b.find_element(By.TAG_NAME,'body').screenshot('./static/img/%s.png' % dataView)

            return jsonify({'message': 'Validado', 'pre_id':dataView,'filename':str(f)}), 200

        except Exception as e:
            
            time.sleep(1)
            return jsonify({'message':'Error indefinido ..'}), 400
            
        finally:

            b.close()
            time.sleep(1)
            
@app.route(f'{base_route}/get_pdf', methods=['POST'])  # Cambiar a POST ya que se espera un JSON en el cuerpo de la solicitud
def get_pdf():
    
    data = request.json

    if 'pre_file' not in data:
        return jsonify({'error': 'Missing file name'}), 400
    
    pre_file = data['pre_file']  # Ruta completa desde la solicitud JSON

    file_path, file_name = os.path.split(pre_file)  # Devuelve el directorio y el nombre del archivo
    # Obtener el nombre del archivo desde la solicitud JSON

    data = request.json
    if 'pre_file' not in data:
        return jsonify({'error': 'Missing file name'}), 400
    
    file_path = '.'+file_path+'/'

    # Definir la ruta del archivo usando os.path.join
    file_path_ = os.path.join(file_path)
    file_name_ = os.path.join(file_name)  # Ajustar ruta según tu configuración
    
    print('file_path_: '+file_path_)
    print('file_name_: '+file_name_)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Devolver el archivo PDF
    try:
     
        return send_from_directory(file_path_, file_name_)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{base_route}/loginToken', methods=['POST'])
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
    
    if usuario.account_status == 1:

        print('Usuario Activo')
        # Mensaje socket
        
        socketio.emit('budget_changed', f'Iniciando sesion usuario: {username}, inhabilitando sesiones activas')
        
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
        tiempo_futuro_utc = tiempo_actual_utc + timedelta(minutes=30)

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
                        'access_token_expiration': access_token_expiration,
                        'data_user':user_data
                        }), 200
    
@app.route(f'{base_route}/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()

    # Calcula el tiempo actual en UTC
    tiempo_actual_utc = datetime.now(timezone.utc)

    # Suma 2 minutos al tiempo actual
    tiempo_futuro_utc = tiempo_actual_utc + timedelta(minutes=30)

    # Convierte a tiempo UNIX (segundos desde el epoch)
    tiempo_unix_utc = tiempo_futuro_utc.timestamp()

    # Redondea el tiempo UNIX
    access_token_expiration = round(tiempo_unix_utc)
   
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token':access_token, 'access_token_expiration':access_token_expiration})

@app.route(f'{base_route}/logout', methods=['POST'])
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
        return jsonify({'message': 'Error al cerrar sesion, intentelo nuevamente'})

    return jsonify({'message': 'Sesion terminada con exito'})

@app.route(f'{base_route}/users')
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


@app.route(f'{base_route}/add-user', methods=['POST'])
@jwt_required()
def AddUser():

    current_user = get_jwt_identity()

    try:

        print(f'Data Usuario: {current_user['username']} : {current_user}')

        if current_user['role'] == 'Administrador':

            try:
               
                account_username = request.json['account_username']
                account_password = request.json['account_password']
                account_status = request.json['account_status']
                account_active = request.json['account_active']
                rol_ID = request.json['rol_ID']
                account_email = request.json['account_email']

                if rol_ID == 'Usuario':
                    rol_ID = 1
                
                if(rol_ID == 'Administrador'):
                    rol_ID = 2

                print(f'Datos Recopilados del HTML: Usuario: {account_username}, Clave: {account_password}, Rol: {rol_ID}, Correo: {account_email}')

                # Generar el hash de la contraseña
                pass_hash = generate_password_hash(account_password)

                role_user = ''

            except Exception as e:

                print(f'Error: {e}')
                return jsonify({'message':'Error al obtener los datos del usuario.'}), 400
            
            try:
                
                conn = conectar_bd()
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM accounts WHERE account_username = ?', (account_username,))
                
                if cursor.fetchone():

                    return jsonify({'message':'El nombre de usuario ya está en uso.'}), 400

                cursor.execute("INSERT INTO accounts (account_username, account_password, account_status, account_active, rol_ID, account_email) VALUES (?, ?, ?, ?, ?, ?)", (account_username, pass_hash, 0, 1, rol_ID, account_email))
                # Confirmar los cambios y cerrar la conexión
                conn.commit()

                cursor.execute('SELECT * FROM accounts WHERE account_username = ?', (account_username,))
                user = cursor.fetchone()

                print(user)
                conn.close()

            except Exception as e:

                print(f'Error con la BD: {e}')
                return jsonify({'message':'Error con la BD'}), 400

            return jsonify({'message':'Validado', 'user':user.account_ID}), 200
        
        else:

            print('Sin privilegios')
            return jsonify({'message':'Sin privilegios.'}), 401
    
    except Exception as e:
        print(f'Error al crear usuario: {e}')
        return jsonify({'message':'Error al crear usuario.'}), 400
    
@app.route(f'{base_route}/cambiar_rol/<int:idUsuario>', methods=['POST'])
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

@app.route(f'{base_route}/deshabilitar_usuario/<int:idUsuario>', methods=['POST'])
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
    

@app.route(f'{base_route}/habilitar_usuario/<int:idUsuario>', methods=['POST'])
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

@app.route(f'{base_route}/reset-password', methods=['POST'])
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
            
            mensaje = f"""  <p>Estimado usuario:</p>
                            <p>Hemos recibido una solicitud para restablecer su contraseña en nuestra plataforma. Para continuar con el proceso, por favor ingrese el siguiente código de verificación en la página correspondiente:</p>
                            <p><b>Código de verificación: <h2>{codigo_verificacion}</h2></b></p>
                            <p style="font-size: 10px"> (Recuerde que el código es sensible a mayúsculas y minúsculas) </p>
                            <p>Gracias,<br>El equipo de soporte.</p>
                       """
            
            enviar_correo_verificacion(destinatarios, asunto, mensaje)
            
            return jsonify({'message':'Validado', 'account_ID':accountID}), 200
        
        else:

            print(f'Usuario no existe')
            return jsonify({'message':'El Usuario no existe en la BD'}), 400

    else:

        return jsonify({'message':'Error al obtener el nombre de usuario'}), 400

def generar_codigo():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

@app.route(f'{base_route}/verify-code', methods=['POST'])
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

@app.route(f'{base_route}/change-password', methods=['POST'])
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


@app.route(f'{base_route}/obtener_especialidades', methods=['GET'])
@jwt_required()
def getEspecialidades():

    try:

        conn = conectar_bd()
        cursor = conn.cursor()

        # Buscar el código de verificación en la base de datos
        cursor.execute('SELECT * FROM especialidades')
        esp_BD = cursor.fetchall()

        especialidades_json = []
        for esp in esp_BD:
            esp_dict = {
                "ID": esp[0],
                "Nombre":esp[1]
            }
            especialidades_json.append(esp_dict)

        if esp_BD:

            print(esp_BD)

            return jsonify({'message':'Validado', 'especialidades':especialidades_json}), 200
            
        else:
            
           
            return jsonify({'message':'No se logro obtener la data'}), 400
        
    except Exception as e:

        print(f'Error al consultar registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400

@app.route(f'{base_route}/agregar_especialista', methods=['POST'])
@jwt_required()
def addEspecialista():

    try:

        med_nombre = request.json['med_nombre']
        med_apellido = request.json['med_apellido']
        esp_ID = request.json['esp_ID']
        med_estado = 1

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO medicos (med_nombre, med_apellido, esp_ID, med_estado) VALUES (?, ?, ?, ?)", (med_nombre, med_apellido,esp_ID, med_estado))
        conn.commit()

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado'}), 200
            
    except Exception as e:

        print(f'Error al consultar registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400


@app.route(f'{base_route}/listar_especialistas', methods=['GET'])
@jwt_required()
def listarEspecialistas():

    try:

        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute(""" EXEC listado_medicos """)

        #SELECT med_ID, med_nombre, med_apellido, med_estado, esp_nombre FROM medicos
        #JOIN especialidades ON medicos.esp_ID = especialidades.esp_ID;

        especialistasBD = cursor.fetchall()

        especialistas_json = []
        for esp in especialistasBD:
            esp_dict = {

                "med_ID": esp[0],
                "med_nombre":esp[1],
                "med_apellido":esp[2],
                "med_estado":esp[3],
                "esp_nombre":esp[4],
                "account_username":esp[5]
            }
            especialistas_json.append(esp_dict)

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado', 'especialistas':especialistas_json}), 200
            
    except Exception as e:

        print(f'Error al obtener registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400
    
@app.route(f'{base_route}/listar_especialistas_disponibles', methods=['GET'])
@jwt_required()
def listarEspecialistasDisponibles():

    try:

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""

            SELECT med_ID, med_nombre, med_apellido, med_estado, esp_nombre FROM medicos
            JOIN especialidades ON medicos.esp_ID = especialidades.esp_ID WHERE med_estado = 1;
                       
        """)
        especialistasBD = cursor.fetchall()

        especialistas_json = []
        for esp in especialistasBD:
            esp_dict = {

                "med_ID": esp[0],
                "med_nombre":esp[1],
                "med_apellido":esp[2],
                "med_estado":esp[3],
                "esp_nombre":esp[4],

            }
            especialistas_json.append(esp_dict)

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado', 'especialistas':especialistas_json}), 200
            
    except Exception as e:

        print(f'Error al obtener registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400

@app.route('/listar_total_especialistas', methods=['GET'])
@jwt_required()
def listarTotalEspecialistas():

    try:

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""

            SELECT med_ID, med_nombre, med_apellido, esp_nombre FROM medicos
            JOIN especialidades ON medicos.esp_ID = especialidades.esp_ID
                       
        """)
        especialistasBD = cursor.fetchall()

        especialistas_json = []
        for esp in especialistasBD:
            esp_dict = {

                "med_ID": esp[0],
                "med_nombre":esp[1],
                "med_apellido":esp[2],
                "esp_nombre":esp[3],

            }
            especialistas_json.append(esp_dict)

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado', 'especialistas':especialistas_json}), 200
            
    except Exception as e:

        print(f'Error al obtener registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400
    
@app.route(f'{base_route}/obtenerPermisosUsuario', methods=['POST'])
@jwt_required()
def getPermisosUsuario():

    try:

        account_ID = request.json['account_ID']

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM permisos_account WHERE account_ID = ?",(account_ID))
        permisos_account = cursor.fetchone()

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado', 'permisos_account':permisos_account}), 200
            
    except Exception as e:

        print(f'Error al consultar registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400

@app.route(f'{base_route}/agregar-permisosUsuario', methods=['POST'])
@jwt_required()
def agregar_permisosUsuario():

    try:

        account_ID = request.json['account_ID']
        per_porc_desc = request.json['per_porc_desc']

        print(f'ID obtenido desde el front:  {account_ID}')
        print(f'Porcentaje de descuento obtenido desde el front:  {per_porc_desc}')

        descuento = int(per_porc_desc)
        
        print(f'Porcentaje de desc a insertar en la BD: {descuento}')

        print('conectando a la BD')
        conn = conectar_bd()
        cursor = conn.cursor()

        print('Verificando si usuario ya tiene permisos creados ...')
        cursor.execute("SELECT * FROM permisos_account WHERE account_ID = ?", (account_ID))
        
        if cursor.fetchone():
            
            print('Usuario ya tiene permisos creados, debe actualizar los permisos.')
            return jsonify({'message': f'Permiso ya existente para el usuario, debe modificar el permiso del usuario {account_ID}'})

        print('Insertando registros en tabla permisos...')
        cursor.execute("INSERT INTO permisos_account (account_ID, per_porc_desc) VALUES (?, ?)",(account_ID, descuento))
        conn.commit()

        print('Permisos insertados de forma correcta ...')
        print('Cerrando conexion ...')

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado'}), 200
            
    except Exception as e:

        print(f'Error al insertar registro en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400
    
@app.route(f'{base_route}/update-permisosUsuario', methods=['POST'])
@jwt_required()
def update_permisosUsuario():

    try:

        account_ID = request.json['account_ID']
        per_porc_desc = request.json['per_porc_desc']

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM permisos_account WHERE account_ID = ?", (account_ID))
        permisos = cursor.fetchone

        if(permisos):
           
            cursor.execute("UPDATE permisos_account SET per_porc_desc = ? WHERE account_ID = ? ",(per_porc_desc, account_ID))
            conn.commit()

            cursor.close()
            conn.close()
        
            return jsonify({'message':'Validado'}), 200
        
        else:
            return jsonify({'message':'No existe el permiso creado para el usuario'})
        
    except Exception as e:

        print(f'Occurio un error al realizar al insertar los datos en la BD: {e}')
        return jsonify({'message':'Error BD'}), 400
    
@app.route(f'{base_route}/asociarAccountMedico', methods=['POST'])
@jwt_required()
def asociarAccountMedico():

    try:

        account_ID = request.json['account_ID']
        med_ID = request.json['med_ID']

        print(f'Account_ID: {account_ID}')

        print(f'Med_ID: {med_ID}')

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM medicos WHERE med_ID = ?",(med_ID))
        medico = cursor.fetchone()

        if(medico.med_estado == 1):

            cursor.execute("INSERT INTO accounts_medicos (account_ID, med_ID) VALUES (?, ?)",(account_ID, med_ID))
            conn.commit()

            cursor.execute("UPDATE medicos SET med_estado = ? WHERE med_ID = ?",(0, med_ID))
            conn.commit()

            cursor.close()
            conn.close()

            socketio.emit('update_med_disp', 'Se ha asociado un medico a un usuario. Actualizando lista.')
            return jsonify({'message':'Validado'}), 200
        
        else:

            return jsonify({'message':'Medico ya se encuentra asignado a un usuario'}), 400
        
    except Exception as e:

        print(f'Error al asociar account con medico: {e}')
        return jsonify({'message':'Error al asociar account con medico'}), 400
    
@app.route(f'{base_route}/eliminarAccountMedico', methods=['POST'])
@jwt_required()
def eliminarAccountMedico():

    try:

        account_ID = request.json['account_ID']
        med_ID = request.json['med_ID']

        #acc_med_ID = request.json['acc_med_ID']

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM accounts_medicos WHERE account_ID = ? AND med_ID = ?",(account_ID, med_ID))
        conn.commit()

        cursor.execute("UPDATE medicos SET med_estado = ? WHERE med_ID = ?",(1, med_ID))
        conn.commit()

        cursor.close()
        conn.close()

        socketio.emit('update_med_disp', 'Se ha quitado la asignacion de un medico, actualizando lista de medicos')
        return jsonify({'message':'Validado'}), 200
    
    except Exception as e:

        print(f'Error al eliminar account con medico: {e}')
        return jsonify({'message':'Error al eliminar account con medico'}), 400
    
@app.route(f'{base_route}/getDataShowUsers', methods=['POST'])
@jwt_required()
def getDataShowUsers():

    try:

        account_ID = request.json['account_ID']

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""
                       
            SELECT accounts.account_ID, accounts.account_username, accounts.account_email ,accounts.account_status, accounts.account_active, rol_accounts.rol_nombre, permisos_account.per_porc_desc FROM accounts
                JOIN permisos_account ON accounts.account_ID = permisos_account.account_ID
                JOIN rol_accounts ON accounts.rol_ID = rol_accounts.rol_ID
                WHERE accounts.account_ID = ?;
                       
        """,(account_ID))
        
        account = cursor.fetchall()

        account_json = []
        for esp in account:
            esp_dict = {
                "account_ID": esp[0],
                "account_username":esp[1],
                "account_email":esp[2],
                "account_status":esp[3],
                "account_active":esp[4],
                "rol_nombre":esp[5],
                "per_porc_desc":esp[6],
            }
            account_json.append(esp_dict)

        conn.commit()

        rol_account = account_json[0]['rol_nombre']
        
        if (rol_account == 'Administrador'):

            cursor.execute("""

                SELECT m.med_ID, med_nombre, med_apellido, esp_ID FROM medicos as m

            """)

        else:

            cursor.execute("""

                SELECT medicos.*
                    FROM medicos
                    JOIN accounts_medicos ON medicos.med_ID = accounts_medicos.med_ID
                    WHERE accounts_medicos.account_ID = ?;

            """, (account_ID))
            
        listaMedicos = cursor.fetchall()

        listaMedicos_json = []
        for esp in listaMedicos:
            esp_dict = {
                "med_ID": esp[0],
                "med_nombre":esp[1],
                "med_apellido":esp[2],
                "esp_ID":esp[3],
            }
            listaMedicos_json.append(esp_dict)            

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado', 'account':account_json, 'listaMedicos':listaMedicos_json}), 200
    
    except Exception as e:

        print(f'Error al obtener la data de la cuenta: {e}')
        return jsonify({'message':'Error en la BD'}), 400

@app.route(f'{base_route}/update-user', methods=['POST'])
@jwt_required()
def updateUser():

    try:

        account_ID = request.json['account_ID']

        account_email = request.json['account_email']
        account_active = request.json['account_active']
        rol_ID = request.json['rol_ID']
        
        if rol_ID == 'Usuario':
            rol_ID = 1
                
        if(rol_ID == 'Administrador'):
            rol_ID = 2

        per_porc_desc = request.json['per_porc_desc']

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("UPDATE accounts SET account_email = ?, account_active = ?, rol_ID = ? WHERE account_ID = ? ",(account_email, account_active, rol_ID, account_ID))
        conn.commit()

        cursor.execute("UPDATE permisos_account SET per_porc_desc = ? WHERE account_ID = ? ",(per_porc_desc, account_ID))
        conn.commit()

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado'}), 200
    
    except Exception as e:

        print(f'Error al asociar account con medico: {e}')
        return jsonify({'message':'Error al asociar account con medico'}), 400
    
@app.route(f'{base_route}/EnviarPRE',methods=["POST"])
def enviarPre():

    data = request.json
    
    if 'email' not in data or 'filename' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    email = data['email']  # Correo del destinatario
    filename = data['filename']  # Ruta del archivo recibido del frontend
    
    print('email: '+email)
    print('filename: '+filename)
    # Verificar que el archivo existe antes de intentar adjuntarlo
    if not os.path.exists('.'+filename):
        return jsonify({'error': 'File not found'}), 404

    enviar_correo(email,filename)
  
    return 'Correo Enviado'

@app.route(f'{base_route}/time', methods=['GET'])
def get_current_time():
    # Obtener la hora actual
    now = datetime.now()
    # Formatear la hora en el formato local
    formatted_time = now.strftime('%A, %d de %B de %Y %H:%M:%S')
    return jsonify({'current_time': now})

if __name__ == "__main__":
    socketio.run(host='0.0.0.0', debug = True)