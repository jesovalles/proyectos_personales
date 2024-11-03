import os
import cv2
import time
import pickle
import requests
import schedule
import numpy as np
import pandas as pd
import face_recognition
import RPi.GPIO as GPIO
from datetime import datetime
from shareplum import Office365


################################## RUTA PRINCIPAL #########################################################
ruta_principal = "/home/steven/Asistencia/"

################################## INICIALIZAR LED'S ######################################################

pin_37 = 37 # LED verde
pin_29 = 29 # LED rojo

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_37,GPIO.OUT)
GPIO.output(pin_37,GPIO.LOW)
GPIO.setup(pin_29,GPIO.OUT)
GPIO.output(pin_29,GPIO.LOW)

###################################### FUNCION PARA GUARDAR DATOS DE REGISTROS EN CSV ######################
# Accedemos a la carpeta de los empleados
carpeta_empleados = ruta_principal + "Empleados_Claro_Cedula"
imagenes_empleados = os.listdir(carpeta_empleados) 
nombres_empleados = []

# leemos los rostros de la base de datos
for lis in imagenes_empleados:
    # Almacenamos el nombre
    nombres_empleados.append(os.path.splitext(lis)[0])

def registrosHorarioIngresos(nombre):
    hoy = datetime.now()
    fecha_hoy = hoy.strftime('%d-%m-%Y')
    file=f'Registro_ingresos.csv'
    if os.path.isfile(file) == False:
        open(file, 'w')
    # Abrimos el archivo en modo lectura y escritura
    with open(file,'r+') as registrosHorarioIngresos:
        # Leemos la información
        datos = registrosHorarioIngresos.readlines()
        # Creamos lista de nombres
        listanombres = []        
        # Itereamos cada linea del cod
        for linea in datos:
            # Buscamos la entrada y la diferencia con
            entrada = linea.split(',')
            # Almacenamos los nombres
            listanombres.append(entrada[0])
        # Verificar si ya hemos almacenado el nombre
        # if nombre not in listanombres:
        # Extraemos informacion actual
        info = datetime.now()
        # Extraemos fecha
        fecha = info.strftime('%Y-%m-%d')
        # Extraemos hora
        hora = info.strftime('%H:%M:%S')
        # Hora entera
        hora_entera = info.strftime('%H')
        # nombre proyecto - sede
        sede = '011D'
        # Guardamos la información
        registrosHorarioIngresos.writelines(f'\n{nombre},{fecha},{hora},{sede}')

################################### CAPTURA ROSTRO ###############        
def captura_rostro(frame,nombre):
    fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H-%M-%S") # es importante poner el formato
    if nombre == 'DESCONOCIDO':
        ruta_foto = f'/home/steven/Asistencia/Rostros_Desconocidos/{nombre} {fecha_hora_actual} 011D.jpg'
    else:
        ruta_foto = f'/home/steven/Asistencia/Rostros_Conocidos/{nombre} {fecha_hora_actual} 011D.jpg'
    cv2.imwrite(ruta_foto,frame)
########################################## CARGA A SHAREPOINT #################################################
    
config = dict()
config['sp_user'] = "bi.admin@inmel.co"
config['sp_password'] = "tFC+Bqig.b47M"
config['sp_base_path'] = 'https://inmelingenieria.sharepoint.com'
config['sp_site_name'] = 'Automatic'
config['sp_doc_library'] = 'Registro%20de%20Asistencia/RegistroAsistencia'
    
def upload():
    # get data from configuration
    username = config['sp_user']
    password = config['sp_password']
    site_name = config['sp_site_name']
    base_path = config['sp_base_path']
    doc_library = config['sp_doc_library']
    hoy = datetime.now()
    fecha_hoy = hoy.strftime('%d-%m-%Y')
    file_name = f'Registro_ingresos.csv'
    df = pd.read_csv(file_name)
    df_sin_duplicados = df.drop_duplicates(['documento','fecha','centro_operacion'],keep='first')
    df_sin_duplicados.to_csv(file_name,index=False)
    time.sleep(1)
    # Obtain auth cookie
    authcookie = Office365(base_path, username=username, password=password).GetCookies()
    session = requests.Session()
    session.cookies = authcookie
    session.headers.update({'user-agent': 'python_bite/v1'})
    session.headers.update({'accept': 'application/json;odata=verbose'})
    # dirty workaround.... I'm getting the X-RequestDigest from the first failed call
    session.headers.update({'X-RequestDigest': 'FormDigestValue'})
    response = session.post( url=base_path + "/sites/" + site_name + "/_api/web/GetFolderByServerRelativeUrl('" + doc_library + "')/Files/add(url='a.txt',overwrite=true)",
                            data="")
    session.headers.update({'X-RequestDigest': response.headers['X-RequestDigest']})
    # perform the actual upload
    with open( file_name, 'rb') as file_input:
        try: 
            response = session.post( 
                url=base_path + "/sites/" + site_name + "/_api/web/GetFolderByServerRelativeUrl('" + doc_library + "')/Files/add(url='" 
                + file_name + "',overwrite=true)",
                data=file_input)
        except Exception as err: 
            print("Some error occurred: " + str(err))

# guardar archivo csv cada hora
schedule.every(10).minutes.do(upload)
#schedule.every().hour.do(upload)


# configuracion webcam
cap = cv2.VideoCapture(0)
cap.set(3,640) # ancho
cap.set(4,480) # alto

# background e imagenes
img_background = cv2.imread(ruta_principal + "Recursos/background_original.png")

# importar las imagnes de los estados. (los estados que va a tener la persona que reconozca)
ruta_carpeta_estados = ruta_principal + "Recursos/Estados"
lista_ruta_estados = os.listdir(ruta_carpeta_estados)
lista_img_estados = []


for ruta_estado in lista_ruta_estados:
    lista_img_estados.append(cv2.imread(os.path.join(ruta_carpeta_estados,ruta_estado)))

# cargar archivo de codificaciones
ruta_archivo = ruta_principal + "RostrosCodificadosClaro.p"
archivo = open(ruta_archivo,'rb')
rostros_conocidos_codificados = pickle.load(archivo)
archivo.close()

tipos_estados = 0
ingresos_registrados = 0
imagen_empleado = []
primer_registro_fecha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

while True:
    ret, frame = cap.read()
    # voltear imagen en modo espejocargar archivo de codificaciones
    # frame = cv2.flip(frame,1)
    # redimensionar a 1/4 de la imagen original 
    frame_2 = cv2.resize(frame,(0,0),None, 0.5, 0.5)
    # cambiar de BGR a RGB, opencv funciona con BGR y face_recognicion funciona con RGB por eso la conversion, de lo contrario no funcionaria
    frame_2_rgb = cv2.cvtColor(frame_2, cv2.COLOR_BGR2RGB)    
    # localizar rostro del video
    rostro_actual = face_recognition.face_locations(frame_2_rgb)
    # codificar rostro actual
    rostro_actual_codificado = face_recognition.face_encodings(frame_2_rgb,rostro_actual)
    # Cargar las imagenes del estado
    img_background[162 : 162+480, 55 : 55+640] = frame
    img_background[44 : 44+633, 826 : 826+414] = lista_img_estados[tipos_estados]
    
    # si existe un rostro actual
    if rostro_actual:
        primer_rostro =  [rostro_actual[0]]
        # comparar rostro actual con los anterioemente codificados
        for rostro_codificado, rostro_localizado in zip(rostro_actual_codificado,rostro_actual):
            coincidencia = face_recognition.compare_faces(rostros_conocidos_codificados, rostro_codificado, tolerance=0.45)
            distancia = face_recognition.face_distance(rostros_conocidos_codificados, rostro_codificado)        
            indice_coincidencia = np.argmin(distancia)
            
            # coordenadas del rostro
            multilicador = 2
            y1, x2, y2, x1 = rostro_localizado
            y1, x2, y2, x1 = y1 * multilicador, x2 * multilicador, y2 * multilicador, x1 * multilicador            
            
            if coincidencia[indice_coincidencia]:
                color_recuadro = (0, 255, 0) # recuadro de color verde              
                nombre = nombres_empleados[indice_coincidencia]
                tipos_estados = 2
                registrosHorarioIngresos(nombre)
                captura_rostro(frame,nombre)
                GPIO.output(pin_37,GPIO.HIGH)
                GPIO.output(pin_29,GPIO.LOW)
            elif coincidencia[indice_coincidencia] == False:
                color_recuadro = (0, 0, 255) # recuadro de color rojo 
                nombre = "DESCONOCIDO"
                #registrosHorarioIngresos(nombre)
                tipos_estados = 1
                captura_rostro(frame,nombre)
                GPIO.output(pin_29,GPIO.HIGH)
                GPIO.output(pin_37,GPIO.LOW)
                
            # esquina superior izquierda 
            cv2.ellipse(img_background,(x1+55, y1+160), (10, 70), 0, 0, 90, color_recuadro, -1)
            cv2.ellipse(img_background,(x1+55, y1+160), (70, 10), 0, 0, 90, color_recuadro, -1)
            # esquina superior derecha
            cv2.ellipse(img_background,(x2+55, y1+160), (10, 70), 90, 0, 90, color_recuadro, -1)
            cv2.ellipse(img_background,(x2+55, y1+160), (70, 10), 90, 0, 90, color_recuadro, -1)
            # esquina inferiror izquierda
            cv2.ellipse(img_background,(x1+55, y2+160), (10, 70), 270, 0, 90, color_recuadro, -1)
            cv2.ellipse(img_background,(x1+55, y2+160), (70, 10), 270, 0, 90, color_recuadro, -1)
            # esquina inferiror derecha
            cv2.ellipse(img_background,(x2+55, y2+160), (10, 70), 180, 0, 90, color_recuadro, -1)
            cv2.ellipse(img_background,(x2+55, y2+160), (70, 10), 180, 0, 90, color_recuadro, -1)
            
        
        if tipos_estados == 1 or tipos_estados == 2:

            fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # es importante poner el formato 

            # mostrar nombre del empleado
            ## ajustar el texto del nombre para que quede en el centro de la imagen de informacion
            (w, h), _ = cv2.getTextSize(nombre, cv2.FONT_HERSHEY_COMPLEX,1,1)
            ajuste = (414 - w ) // 2
            cv2.putText(img_background, #en que imagen
                        str(nombre), # lo que deseo escribir
                        (808 + ajuste, 200), # ubicacion del texto 445
                        cv2.FONT_HERSHEY_COMPLEX, # tipo de letra
                        1.3, # tamaño
                        (0,0,0), # color del texto
                        2 # grosor
                        )
            
            # mostrar fecha y hora de ingreso
            cv2.putText(img_background, #en que imagen
                        str(fecha_hora_actual), # lo que deseo escribir
                        (925, 623), # ubicacion del texto
                        cv2.FONT_HERSHEY_COMPLEX, # tipo de letra
                        0.7, # tamaño
                        (0,0,0), # color del texto
                        1 # grosor
                        )

    else:
        tipos_estados = 0
        GPIO.output(pin_29,GPIO.LOW)
        GPIO.output(pin_37,GPIO.LOW)
        
    cv2.imshow('Control de asistencia - Auto Arranque',img_background)
    # ejecutar la accion de schedule
    try:
        schedule.run_pending()
    except:
        pass
    # Leemos el teclado
    teclado = cv2.waitKey(5)
    if teclado == 27:
        break
        
cap.release()
cv2.destroyAllWindows()
GPIO.output(pin_37,GPIO.LOW)
GPIO.output(pin_29,GPIO.LOW)
GPIO.cleanup()
