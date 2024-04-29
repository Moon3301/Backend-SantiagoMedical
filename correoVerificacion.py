import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
from email.mime.base import MIMEBase
from email import encoders

def enviar_correo(destinatarios, filename):
    # Crea un nuevo hilo que se encargará de enviar el correo
    thread = threading.Thread(target=envioCorreo, args=(destinatarios, filename))
    # Inicia el hilo
    thread.start()

def envioCorreo(e,f):

    email = "katherine.ergas@santiagomedical.cl"
    # password = "Smedical..534"
    password = "Smedical.2021"

    destinatarios = [e]
    file = f
    # Iniciamos los parámetros del script
    remitente = email
    
    asunto = '[PRE] Presupuesto Medico'
    cuerpo = 'Se adjunta documento presupuesto medico solicitado.'
    ruta_adjunto = '.'+file
    nombre_adjunto = 'Presupuesto2024.pdf'
    #cc = ['katherine.ergas@santiagomedical.cl']
    # Creamos el objeto mensaje
    mensaje = MIMEMultipart()
    
    # Establecemos los atributos del mensaje
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
    #mensaje['CC'] = 'katherine.ergas@santiagomedical.cl'
    print(remitente)
    # Agregamos el cuerpo del mensaje como objeto MIME de tipo texto
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    
    # Abrimos el archivo que vamos a adjuntar
    archivo_adjunto = open(ruta_adjunto, 'rb')
    
    # Creamos un objeto MIME base
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload((archivo_adjunto).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
    # Y finalmente lo agregamos al mensaje
    mensaje.attach(adjunto_MIME)
    
    # Creamos la conexión con el servidor
    sesion_smtp = smtplib.SMTP_SSL('mail.santiagomedical.cl', 465)
    
    # Ciframos la conexión
    # sesion_smtp.starttls()

    # Iniciamos sesión en el servidor
    sesion_smtp.login(email,password)

    # Convertimos el objeto mensaje a texto
    texto = mensaje.as_string()

    # Enviamos el mensaje
    sesion_smtp.sendmail(remitente, destinatarios, texto)
    # return sesion_smtp
    print(sesion_smtp)
    # Cerramos la conexión
    sesion_smtp.quit()

def _enviar_correo(destinatarios, pdf):
    # Configura las credenciales del correo electrónico del remitente
    correo_remitente = "app@acdata.cl"
    contraseña = "jtzgdfwnkmgnkpgy"

    asunto = '[PRE] Presupuesto Medico'
    cuerpo = 'Se adjunta documento presupuesto medico solicitado.'
    nombre_adjunto = 'Presupuesto2024.pdf'
    cc = ['katherine.ergas@santiagomedical.cl']

    # Crea el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = correo_remitente
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = asunto
    #msg['CC'] = 'katherine.ergas@santiagomedical.cl'

    # Agrega el mensaje al correo
    msg.attach(MIMEText(cuerpo, 'plain'))

   
    # Configura el servidor SMTP de Gmail
    servidor_smtp = "smtp.office365.com"
    puerto_smtp = 587

    # Inicia sesión en el servidor de correo y envía el correo
    server = smtplib.SMTP(servidor_smtp, puerto_smtp)
    server.starttls()

    try:
        
        server.login(correo_remitente, contraseña)

    except Exception as e:

        return 'Error en autenticacion'
    
    try:

        server.send_message(msg)
        return 'correo enviado'
    
    except Exception as e:

        return f'Error al enviar correo: {e}'
    finally:
        server.quit()