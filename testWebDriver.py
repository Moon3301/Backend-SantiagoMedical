import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.DEBUG)

# Asegúrate de definir `dir_download` y `dataView`
dir_download = "C:\\ruta\\de\\descarga\\"  # Actualiza esta ruta según tu sistema
dataView = "example_directory"  # Actualiza este valor según sea necesario

try:
    # Define la configuración para la instancia del navegador
    profile = {
        "plugins.always_open_pdf_externally": True,  # Disable Chrome's PDF Viewer
        "download.default_directory": dir_download + str(dataView),
        "download.extensions_to_open": "applications/pdf"
    }

    logging.info("Configurando opciones del navegador")

    # Opciones del navegador
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", profile)
    # chrome_options.add_argument('--headless')  # Asegúrate de que esto esté comentado
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')

except Exception as e:
    logging.error("Error al configurar instancia de ChromeDriver", exc_info=True)
    # return jsonify({'message': 'Error al configurar instancia de ChromeDriver'}), 400

# Inicializa la variable `browser` fuera del bloque try
browser = None

# Crea la instancia de Chrome con opciones y servicio
try:
    logging.info("Creando instancia de ChromeDriver")
    # Usando ChromeDriverManager para asegurar la compatibilidad de versiones
    browser = webdriver.Chrome(options=chrome_options)
    logging.info('Instancia de Chrome creada exitosamente')

except Exception as e:
    logging.error(f'Error al crear la instancia de Chrome: {e}', exc_info=True)
    # return jsonify({'message': 'Error al crear la instancia de Chrome'}), 400

if browser:
    try:
        # Registra un mensaje antes de acceder a la web
        logging.debug('Accediendo a la web medilink ...')

        # Navega a una URL de prueba para verificar si el navegador se abre correctamente
        browser.get("https://www.google.com")
        logging.info('Navegador accedió a Google exitosamente')
    except Exception as e:
        logging.error(f'Error al acceder a la web: {e}', exc_info=True)
    finally:
        # Cierra el navegador al finalizar la prueba
        browser.quit()
else:
    logging.error('No se pudo crear la instancia del navegador, por lo que no se pudo ejecutar la prueba.')