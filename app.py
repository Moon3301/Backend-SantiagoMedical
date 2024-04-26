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

import xlwings as xw
from openpyxl import load_workbook
from exchangelib import Credentials, Account, Message, Mailbox, FileAttachment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from renameFile import changeNameFile

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

@app.route('/start_scrapping',methods=["POST"])
def start_bot_selenium_4():
    
    print("Iniciando scrapping ...")

    # Se obtiene el ID del presupuesto a ingresar
    dataView = request.json["pre_id"]

    print(f'dataView: {dataView}')

    # Se define la url del paciente a obtener
    url = 'http://localhost:3000/presupuesto-paciente'

    # Se define la variable myobj y se le asigna el ID del presupuesto
    myobj = {"pre_id":dataView}

    # Se realiza la solicitud a la api 
    x = requests.post(url,json=myobj, verify=False)

    # Se obtiene el registro en formato de texto
    y = json.loads(x.text)
    print(f'Obteniendo registro de presupuesto paciente: {y}')

    # Se define la url del presupuesto a obtener
    urlP = 'http://localhost:3000/presupuesto'

    # Se realiza la solicitud a la api con el paramtro myobj
    xP = requests.post(urlP,json=myobj, verify=False)

    # Se obtiene el registro en formato de texto
    yP = json.loads(xP.text)
    print(f'Obteniendo registro de presupuesto: {yP}')
    # Se obtiene el correo de la lista de presupuesto
    #correo = yP[0]["pre_email"]

    #prefs = {
    #    "download.default_directory": "C:\\Apache24\\htdocs\\santiagomedical\\static\\files\\" + str(dataView)
    #}

    # Define la configuracion para la isntancia del navegador: Desactiva el visor PDF (para descargar automaticamente en lugar de abrirse en el navegador)
    profile = {"plugins.always_open_pdf_externally": True, # Disable Chrome's PDF Viewer
                "download.default_directory": "C:\\Apache24\\htdocs\\santiagomedical\\static\\files\\" + str(dataView) , "download.extensions_to_open": "applications/pdf"}
    
    print("Cargando navegador")

    # Opciones del navegador
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", profile)
    #chrome_options.add_argument('--headless') <== Se habilita esta opcion para no tener una intefaz de scrapping, pero la accion se ejecuta de igual forma.
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')

    # Crea la instancia de Chrome con opciones y servicio
    try:
        browser = webdriver.Chrome(options=chrome_options)
        print('Instancia de Chrome creada exitosamente')
    except Exception as e:
        print(f'Error al crear la instancia de Chrome: {e}')

    # Registra un mensaje antes de acceder a la web
    print('Accediendo a la web medilink ...')

    # Intenta acceder a la web
    try:
        browser.get('http://santiagomedical.new.softwaremedilink.com/sessions/login')
        print('Acceso a la web exitoso')
    except Exception as e:
        print(f'Error al acceder a la web: {e}')

    # Se obtienen los inputs de usuario y contrasena
    eUser = browser.find_element(By.XPATH,'//*[@id="login-form"]/div/div[1]/input')
    ePassword = browser.find_element(By.XPATH,'//*[@id="login-form"]/div/div[2]/input')

    # Se obtiene el boton para iniciar sesion
    eButton = browser.find_element(By.XPATH,'//*[@id="login-form"]/div/input')

    # Se insertan las credenciales de acceso en los inputs
    eUser.send_keys('mvalenzuela')
    ePassword.send_keys('mvalenzuela')

    time.sleep(1)
    # Presionar el boton iniciar sesion con las credenciales de acceso
    eButton.click()
    time.sleep(1)

    # Se define la variable b y se le asigna la variable de la intancia del navegador
    b = browser

    # Se elimina el directorio definido en la ruta, ignorando cualquier error ocurrido durante la eliminacion.
    print("Eliminando directorio definido en la ruta ./static/files/'+str(dataView)") 
    shutil.rmtree('./static/files/'+str(dataView), ignore_errors=True)

    print("asignando directorio")
    directory = str(dataView)
    parent_dir = './static/files/'
    pathFolder = os.path.join(parent_dir, directory)
    os.mkdir(pathFolder)

    print("Realizando screenshoot y guardando en ruta: ./static/img/%s.png")
    b.save_screenshot('./static/img/%s.png' % dataView)

    try:
        print("Buscando paciente ...")
        searchPaciente = b.find_element(By.XPATH,'//*[@id="buscador-header"]')

        print("Obteniendo rut del paciente ...")

        if "presupuestoPaciente" in y and len(y["presupuestoPaciente"]) > 0:
            searchRut = y["presupuestoPaciente"][0]["prepa_rut"][:-2]
            print("Rut truncado:", searchRut)
        else:
            print("Error: 'presupuestoPaciente' está vacío o no es una lista.")

        searchPaciente.send_keys(searchRut)
        print("Ingresando rut en input del buscador ...")

        time.sleep(4)
        print("Sacando Screenshot de pantalla")
        b.save_screenshot('./static/img/%s.png' % dataView)

        largoPacientes = b.execute_script("return document.querySelectorAll('body > div.navbar- > div > div > table > tbody > tr > td:nth-child(2) > div > ul > li').length")
        if largoPacientes > 2:
            time.sleep(3)
            b.find_element(By.XPATH,'/html/body/div[13]/div/div/table/tbody/tr/td[2]/div/ul/li[1]/a').click()
            b.save_screenshot('./static/img/%s.png' % dataView)
        else:
            time.sleep(3)
            b.get('https://santiagomedical.new.softwaremedilink.com/clientes')
            b.save_screenshot('./static/img/%s.png' % dataView)
            time.sleep(2)
            b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[1]/div[1]/div/div[1]/a').click()
            b.save_screenshot('./static/img/%s.png' % dataView)
            b.execute_script("document.querySelector('#nombre').id = 'apellido'")
            b.find_element(By.XPATH,'//*[@id="apellido"]').send_keys(y["presupuestoPaciente"][0]["prepa_nombre"])
            b.find_element(By.XPATH,'//*[@id="nombre"]').send_keys(y["presupuestoPaciente"][0]["prepa_apellido"])
            b.find_element(By.XPATH,'//*[@id="rut"]').send_keys(y["presupuestoPaciente"][0]["prepa_rut"])
            
            elemento_email = b.find_element(By.XPATH,'//*[@id="email-form"]')

            # Borrar el contenido previo
            elemento_email.clear()

            # Obtener el nuevo email_cargado (como en tu código anterior)
            email_cargado = y["presupuestoPaciente"][0]["prepa_email"]
            if len(email_cargado) == 0:
                email_cargado = "email@sanatorio.com"

            # Enviar el nuevo contenido
            elemento_email.send_keys(email_cargado)
            
            b.execute_script('document.querySelector("#sexo").value = "{}"'.format(y["presupuestoPaciente"][0]["prepa_sexo"]))
            b.save_screenshot('./static/img/%s.png' % dataView)
            b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[1]/div/form/div[11]/div/input').send_keys(y["presupuestoPaciente"][0]["prepa_direccion"])
            ciudad_input = b.find_element(By.NAME,'ciudad')
            ciudad_input.send_keys("Ciudad Ejemplo")
            comuna_input = b.find_element(By.NAME,'comuna')
            comuna_input.send_keys("Comuna Ejemplo")
            #b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[1]/div/form/div[13]/div/div/input').send_keys(y[0]["prepa_celular"])
            telefono_input = b.find_element(By.ID,'celular')
            telefono_input.send_keys(y["presupuestoPaciente"][0]["prepa_celular"])

            # b.find_element(By.XPATH,'/html/body/table[2]/tbody/tr/td/div[3]/div[1]/div/form/div[16]/div/textarea').send_keys(y[0]["prepa_observacion"])
            b.find_element(By.XPATH,'//*[@id="siguiente"]').click()
            b.save_screenshot('./static/img/%s.png' % dataView)
            b.get('https://santiagomedical.new.softwaremedilink.com/')
            b.save_screenshot('./static/img/%s.png' % dataView)
            searchPaciente = b.find_element(By.XPATH,'//*[@id="buscador-header"]')
            #searchPaciente.send_keys(y[0]["prepa_rut"])
            searchPaciente.send_keys(searchRut)
            time.sleep(4)
            #b.find_element(By.XPATH,'//*[@id="client-sidebar"]/div[1]/a[1]').click()
            b.find_element(By.XPATH,'/html/body/div[13]/div/div/table/tbody/tr/td[2]/div/ul/li[1]/a').click()
            b.save_screenshot('./static/img/%s.png' % dataView)
        b.find_element(By.XPATH,'//*[@id="section_content"]/div[2]/div[1]/div[1]/div/div/div[3]/a').click()
        b.find_element(By.XPATH,'//*[@id="section_content"]/div[2]/div[1]/div[1]/div/div/div[3]/ul/li[9]/a').click()
        
        urlMedico = 'http://localhost:3000/presupuesto-medico'
        xMed = requests.post(urlMedico,json=myobj, verify=False)
        yMed = json.loads(xMed.text)

        atencion = yMed["presupuestoMedico"][0]["premed_valor"]
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
        print(secitionAtenciones)
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

        print("Obteniendo prestaciones ...")

        print("Obteniendo Cirugias ...")
        urlCirugias = 'http://localhost:3000/lista-presupuesto-cirugia'
        xCir = requests.post(urlCirugias,json=myobj, verify=False)
        yCir = json.loads(xCir.text)
        yCir = yCir["presupuestoCirugias"]
        print(f"Cirugias obtenidas: {yCir}")

        print("Obteniendo Vaser ...")
        urlVaser = 'http://localhost:3000/lista-presupuesto-vaser'
        xVas = requests.post(urlVaser,json=myobj, verify=False)
        yVase = json.loads(xVas.text)
        yVase = yVase["listaVaser"]
        print(f"Vaser obtenido: {yVase}")

        print("Obteniendo Anestesia ...")
        urlAnestesia = 'http://localhost:3000/lista-presupuesto-anestesias'
        xAne = requests.post(urlAnestesia,json=myobj, verify=False)
        yAne = json.loads(xAne.text)
        yAne = yAne["presupuestoAnestesias"]
        print(f"Anestesia obtenida: {yAne}")

        print("Obteniendo Recuperacion ...")
        urlRecuperacion = 'http://localhost:3000/presupuesto-recuperacion'
        xRec = requests.post(urlRecuperacion,json=myobj, verify=False)
        yRec = json.loads(xRec.text)
        yRec = yRec["presupuestoRecuperacion"]
        print(f"Recuperacion obtenida: {yRec}")

        print(f"Sacando print de pantalla...")
        b.save_screenshot('./static/img/%s.png' % dataView)

        print("Cargando prestaciones ...")
        for i in yCir:
            if int(i["precir_flag"]) == 1:
                print("Cargando Cirugias")
                cargaPrestaciones(b,i["precir_nombre"],i["precir_precio"],i["precir_horas"],dataView)    
            else:
                cargaPrestaciones(b,i["precir_nombre"],i["precir_precio"],i["precir_horas"],dataView)    
                    
        for i in yAne:
            cargaPrestaciones(b,i["preane_nombre"],i["preane_precio"],i["preane_horas"],dataView)

        for i in yRec:
            cargaPrestaciones(b,i["prerec_nombre"],i["prerec_precio"],i["prerec_horas"],dataView)
        
        for i in yVase:
           cargaPrestaciones(b,i["preva_nombre"],i["preva_precio"],i["preva_horas"],dataView)
            
        b.save_screenshot('./static/img/%s.png' % dataView)
        time.sleep(3)
        b.find_element(By.XPATH,'//*[@id="cargar-prestaciones-success"]').click()
        time.sleep(3)
        datosM = b.execute_script(open('./index.js').read())
        descuentoFlag = 20
        arra = []        
        for i,idx in enumerate(yCir):
            yCir[i].update({'flag':0})
        for i in yCir:
            # if i["precir_precio"] != 0:
            for j in datosM:
                str2 = j["nombre"].replace(u'Más Información','')
                str3 = str2.replace(u'Eliminar','')
                str4 = str3.replace(u'-','').strip()
                strD = i["precir_nombre"].replace(u'-','').strip()            
                #print(int(j["descuento"]),int(i["precir_descuento"]))
                print(str4,strD,str4 == strD)
                
                if str4 == '210409300 INSUMOS TUNEL CARPEANO':
                    if str4 == strD and int(descuentoFlag) != int(i['precir_descuento']):
                        descuentoFlag = i['precir_descuento']
                        b.save_screenshot('./static/img/%s.png' % dataView)
                        if int(i["precir_flag"]) == 1:                
                            #precioZ = int(i["cir_precio"]) * int(i["precir_horas"])
                            #precioZ = int(i["precir_precio"]) * int(i["precir_horas"])
                            precioZ = int(i["precir_precio"])
                        else:
                            #precioZ = int(i["cir_precio_insumo"]) * int(i["precir_horas"])
                            #precioZ = int(i["precir_precio"]) * int(i["precir_horas"])
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
                            # if int(i["precir_descuento"]) != 0:
                                time.sleep(1)
                                b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                time.sleep(1)
                                print(len(str(i["precir_descuento"])))
                                if len(str(i["precir_descuento"])) <= 1:
                                    b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.0{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                else:
                                    b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                # b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                
                                b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))
                else:
                    if str4 == strD:
                        descuentoFlag = i['precir_descuento']
                        b.save_screenshot('./static/img/%s.png' % dataView)
                        if int(i["precir_flag"]) == 1:                
                            #precioZ = int(i["cir_precio"]) * int(i["precir_horas"])
                            #precioZ = int(i["precir_precio"]) * int(i["precir_horas"])
                            precioZ = int(i["precir_precio"])
                        else:
                            #precioZ = int(i["cir_precio_insumo"]) * int(i["precir_horas"])
                            #precioZ = int(i["precir_precio"]) * int(i["precir_horas"])
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
                            # if int(i["precir_descuento"]) != 0:
                                time.sleep(1)
                                b.execute_script('jQuery("#porcentaje_edit_accion_{}").toggle();'.format(j["codigo"]))
                                time.sleep(1)
                                print(len(str(i["precir_descuento"])))
                                if len(str(i["precir_descuento"])) <= 1:
                                    b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.0{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                else:
                                    b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                # b.execute_script('document.querySelector("#porcentaje_field_accion_{}").value = "0.{}"'.format(j["codigo"],int(i["precir_descuento"])))
                                
                                b.execute_script('updatePorcentajeDetallePresupuesto("porcentaje_field_accion_{}","{}");'.format(j["codigo"],j["codigo"]))
        for i in yAne:
            for j in datosM:
                str2 = j["nombre"].replace(u'Más Información','')
                str3 = str2.replace(u'Eliminar','')
                str4 = str3.replace(u'-','').strip()
                strD = i["preane_nombre"].replace(u'-','').strip()
                if str4 == strD:
                    #precioF = int(i["ane_precio"]) * int(i["preane_horas"])
                    precioF = int(i["preane_precio"])
                    b.save_screenshot('./static/img/%s.png' % dataView)
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
                    #precioF = int(i["ane_precio"]) * int(i["preane_horas"])
                    precioF = int(i["preva_precio"])
                    b.save_screenshot('./static/img/%s.png' % dataView)
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
            # if i["prerec_precio"] != 0:
            for j in datosM:
                b.save_screenshot('./static/img/%s.png' % dataView)
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
        b.save_screenshot('./static/img/%s.png' % dataView)
        b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div/div[2]/ul/li[2]/a').click()
        b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div/div[2]/ul/li[2]/ul/li[1]/a').click()
        b.save_screenshot('./static/img/%s.png' % dataView)
        time.sleep(10)
        b.save_screenshot('./static/img/%s.png' % dataView)
        f = changeNameFile(dataView)

        print('https://stgomedical.acbingenieria.cl%s' % str(f))
        S = lambda X: b.execute_script('return document.body.parentNode.scroll'+X)
        b.set_window_size(S('Width'),S('Height'))                                                                                                            
        b.find_element(By.TAG_NAME,'body').screenshot('./static/img/%s.png' % dataView)
        # el.save_screenshot('%s.png' % dataView)
        print('CERRANDO BROWSER %s' % dataView)
        b.close()
        # file = find('doc.pdf','./static')   
        # lenFile = len(file)
        # if lenFile > 0:
        #     os.remove('./static/doc.pdf')
        # b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div/div[2]/ul/li[2]/a').click()
        # b.find_element(By.XPATH,'//*[@id="section_content"]/div[1]/div/div[2]/ul/li[2]/ul/li[1]/a').click()
        # paths = WebDriverWait(b, 120, 1).until(every_downloads_chrome)   
        # b.close()
        # if paths != '':
        #     p = paths[0].replace('file:///','') 
        #     # print(paths)
        #     f = changeNameFile()
        #     filePath= r'C:/Apache24/htdocs/santiagomedical/'+str(f)+''
        #     print(f)
        #     print(p)

        url = 'http://localhost:3000/update_file'
        myobj = {"pre_id":dataView,"filename":str(f)}    
        x = requests.post(url,json=myobj, verify=False)

        #     #envia_correo(filePath,correo)    
        return 'OK'
    except Exception as e:
        print(e)
        b.save_screenshot('Error%s.png' % dataView) 
        url = 'http://localhost:3000/update_presupuestoF'   
        requests.post(url,json=myobj, verify=False)
        b.close()

def cargaPrestaciones(b,prestacion,precio,horas,dataView):
    if (int(precio) != 0):
        if(int(horas) != 0):
            b.save_screenshot('./static/img/%s.png' % dataView)
            time.sleep(2)
            b.find_element(By.XPATH,'//*[@id="query"]').send_keys(prestacion)
            time.sleep(1)
            if prestacion == 'Honorarios Medicos':
                b.find_element(By.XPATH,'//*[@id="invoice_item_manager_buscar"]/div[1]/ul/li[3]/a').click()
            else:
                b.find_element(By.XPATH,'//*[@id="invoice_item_manager_buscar"]/div[1]/ul/li[1]/a').click()
            time.sleep(1)
            b.find_element(By.XPATH,'//*[@id="agregar_buscar"]').click()

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
                        'access_token_expiration': access_token_expiration,
                        'data_user':user_data
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


@app.route('/obtener_especialidades', methods=['GET'])
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

@app.route('/agregar_especialista', methods=['POST'])
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


@app.route('/listar_especialistas', methods=['GET'])
@jwt_required()
def listarEspecialistas():

    try:

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""

            SELECT med_ID, med_nombre, med_apellido, med_estado, esp_nombre FROM medicos
            JOIN especialidades ON medicos.esp_ID = especialidades.esp_ID;
                       
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

@app.route('/obtenerPermisosUsuario', methods=['POST'])
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

@app.route('/agregar-permisosUsuario', methods=['POST'])
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
    
@app.route('/update-permisosUsuario', methods=['POST'])
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
    
@app.route('/asociarAccountMedico', methods=['POST'])
@jwt_required()
def asociarAccountMedico():

    try:

        account_ID = request.json['account_ID']
        med_ID = request.json['med_ID']

        print(f'Account_ID: {account_ID}')

        print(f'Med_ID: {med_ID}')

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO accounts_medicos (account_ID, med_ID) VALUES (?, ?)",(account_ID, med_ID))
        conn.commit()

        cursor.execute("UPDATE medicos SET med_estado = ? WHERE med_ID = ?",(0, med_ID))
        conn.commit()

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado'}), 200
    
    except Exception as e:

        print(f'Error al asociar account con medico: {e}')
        return jsonify({'message':'Error al asociar account con medico'}), 400
    
@app.route('/eliminarAccountMedico', methods=['POST'])
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
    
        return jsonify({'message':'Validado'}), 200
    
    except Exception as e:

        print(f'Error al eliminar account con medico: {e}')
        return jsonify({'message':'Error al eliminar account con medico'}), 400
    
@app.route('/getDataShowUsers', methods=['POST'])
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

@app.route('/updateUser', methods=['POST'])
@jwt_required()
def updateUser():

    try:

        account_ID = request.json['account_ID']

        account_email = request.json['account_email']
        account_status = request.json['account_status']
        rol_ID = request.json['rol_ID']

        per_porc_desc = request.json['per_porc_desc']

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("UPDATE accounts SET account_email = ?, account_status = ?, rol_ID = ? WHERE account_ID = ? ",(account_email, account_status, rol_ID, account_ID))
        conn.commit()

        cursor.execute("UPDATE permisos_account SET per_porc_desc = ? WHERE account_ID = ? ",(per_porc_desc, account_ID))
        conn.commit()

        cursor.close()
        conn.close()
    
        return jsonify({'message':'Validado'}), 200
    
    except Exception as e:

        print(f'Error al asociar account con medico: {e}')
        return jsonify({'message':'Error al asociar account con medico'}), 400
    

if __name__ == "__main__":
    app.run(debug = True)