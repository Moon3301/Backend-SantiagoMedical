import pyodbc 
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = 'WIN-V5M4DR7Q1K1\SQLDEV' 
database = 'db_santiago_medical' 
username = 'sa' 
password = 'zxcdewq123.,**' 

def conectar_bd():
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
