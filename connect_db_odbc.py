import pyodbc 
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
#server = 'WIN-V5M4DR7Q1K1\SQLDEV'
#server = 'MOONLIGHT\\SQLEXPRESS'
# 'MOONLIGHT\\SQLEXPRESS'
# 'SOPORTE2\\SQLEXPRESS'

# STGOMED-NEWB0T\SQLEXPRESS
server = 'STGOMED-NEWB0T\\SQLEXPRESS'
#database = 'db_santiago_medical'
database = 'db_stgo_medical'
username = 'sa' 
password = 'zxcdewq123.,**' 

def conectar_bd():
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

