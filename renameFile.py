import os
import datetime

def changeNameFile(pre_id):
    Current_Date = datetime.datetime.today().strftime ('%Y-%m-%d_%H_%M_%S')
    nombreNuevo = r'/static/files/'+str(pre_id)+'/Presupuesto_'+str(Current_Date)+'.pdf'
    os.rename(r'./static/files/'+str(pre_id)+'/doc.pdf',r'./static/files/'+str(pre_id)+'/Presupuesto_'+str(Current_Date)+'.pdf')
    return str(nombreNuevo)