import pyodbc 
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
#server = 'WIN-V5M4DR7Q1K1\SQLDEV'
server = 'MOONLIGHT\\SQLEXPRESS'
# 'MOONLIGHT\\SQLEXPRESS'
# 'SOPORTE2\\SQLEXPRESS'
#database = 'db_santiago_medical'
database = 'db_stgo_medical'
username = 'sa' 
password = 'zxcdewq123.,**' 

def conectar_bd():
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

"""
def conectar_bd_test():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        if row:
            print("Conexión establecida correctamente.")
            return conn
        else:
            print("No se pudo establecer conexión.")
            return None
    except Exception as e:
        print("Error al conectar:", e)
        return None

# Ejemplo de uso
conn = conectar_bd_test()

if conn:
    # Realizar operaciones con la conexión
    # ...
    conn.close()
"""