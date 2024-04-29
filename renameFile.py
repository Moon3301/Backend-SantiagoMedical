import os
import datetime
import shutil

dir_download = "C:\\Users\\Administrador\\Desktop\\Backend-SantiagoMedical\\static\\files\\"

def changeNameFile(pre_id):

    Current_Date = datetime.datetime.today().strftime ('%Y-%m-%d_%H_%M_%S')
    nombreNuevo = r'/static/files/'+str(pre_id)+'/Presupuesto_'+str(Current_Date)+'.pdf'
    os.rename(r'./static/files/'+str(pre_id)+'/doc.pdf',r'./static/files/'+str(pre_id)+'/Presupuesto_'+str(Current_Date)+'.pdf')
    
    return str(nombreNuevo)

    