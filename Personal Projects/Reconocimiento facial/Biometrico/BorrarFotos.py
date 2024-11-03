import os
import datetime

# Define la ruta de la carpeta
ruta_carpeta_desconocidos = "/home/steven/Asistencia/Rostros_Desconocidos"
ruta_carpeta_conocidos = "/home/steven/Asistencia/Rostros_Conocidos"
# Fecha de 7 días atrás desde hoy
limite = datetime.datetime.now().date() - datetime.timedelta(days=7)

try:
    # Recorre los archivos en la carpeta de desconocidos
    for desconocido in os.listdir(ruta_carpeta_desconocidos):
        ruta_archivo_desconocidos = os.path.join(ruta_carpeta_desconocidos, desconocido)
        # Verifica si es un archivo (no un directorio)
        if os.path.isfile(ruta_archivo_desconocidos):        
            # Obtén la fecha de modificación del archivo
            fecha_modificacion_desconocido = datetime.datetime.fromtimestamp(os.path.getmtime(ruta_archivo_desconocidos)).date()
            # Si el archivo es más antiguo que el límite, bórralo
            if fecha_modificacion_desconocido < limite:
                os.remove(ruta_archivo_desconocidos)

    # Recorre los archivos en la carpeta de conocidos
    for conocido in os.listdir(ruta_carpeta_conocidos):
        ruta_archivo_conocidos = os.path.join(ruta_carpeta_conocidos, conocido)
        # Verifica si es un archivo (no un directorio)
        if os.path.isfile(ruta_archivo_conocidos):        
            # Obtén la fecha de modificación del archivo
            fecha_modificacion_conocido = datetime.datetime.fromtimestamp(os.path.getmtime(ruta_archivo_conocidos)).date()
            # Si el archivo es más antiguo que el límite, bórralo
            if fecha_modificacion_conocido < limite:
                os.remove(ruta_archivo_conocidos)

except FileNotFoundError:
    print('El sistema no puede encontrar la ruta especificada')


# Nombre del archivo a crear
nombre_archivo = '1 archivo_ejemplo.txt'

# Texto a escribir en el archivo
texto = '¡Hola, este es un archivo de texto creado con Python!'

# Abrir el archivo para escritura (crea el archivo si no existe)
with open(nombre_archivo, 'w') as archivo:
    archivo.write(texto)

print(f'1 Archivo {nombre_archivo} creado con éxito.')
