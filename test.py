import datetime

# Tiempo UNIX proporcionado
tiempo_unix = 1713319713

# Convierte el tiempo UNIX a una fecha y hora legibles
fecha_hora = datetime.datetime.fromtimestamp(tiempo_unix)

print("Fecha y hora:", fecha_hora)