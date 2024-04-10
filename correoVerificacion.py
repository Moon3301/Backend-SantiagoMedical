import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading

def enviar_correo(destinatarios, asunto, mensaje):
    # Crea un nuevo hilo que se encargará de enviar el correo
    thread = threading.Thread(target=_enviar_correo, args=(destinatarios, asunto, mensaje))
    # Inicia el hilo
    thread.start()

def _enviar_correo(destinatarios, asunto, mensaje):
    # Configura las credenciales del correo electrónico del remitente
    correo_remitente = "app@acdata.cl"
    contraseña = "jtzgdfwnkmgnkpgy"

    # Crea el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = correo_remitente
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = asunto

    # Agrega el mensaje al correo
    msg.attach(MIMEText(mensaje, 'html'))

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