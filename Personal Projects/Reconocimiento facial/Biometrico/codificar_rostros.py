import time
inicio = time.time()

import os
import cv2
import pickle
import face_recognition

###################################### FUNCION PARA CODIFICAR ROSTROS Y GUARDAR EN PICKLE ############################

# importar imagenes empleados
ruta_carpeta_rostros = "/home/steven/Asistencia/Empleados_Claro_Cedula"
lista_ruta_rostros = os.listdir(ruta_carpeta_rostros)
lista_img_rostros = []

for ruta_rostro in lista_ruta_rostros:
    imagen_original =  cv2.imread(os.path.join(ruta_carpeta_rostros,ruta_rostro))
    escala = 50
    ancho = int(imagen_original.shape[1] * escala / 100)
    largo = int(imagen_original.shape[0] * escala / 100)
    dimension = (ancho, largo)  
    if ancho > 80:
        imagen_redimensioanda = cv2.resize(imagen_original,dimension)
        lista_img_rostros.append(imagen_redimensioanda)
    else:
        lista_img_rostros.append(imagen_original)
    #print(ruta_rostro,'',ancho)

def codificar_rostro(lista_rostros):
    rostros_codificados = []
    c = 1
    for rostro, ruta in zip(lista_rostros,lista_ruta_rostros):
        print('contador => ', c, 'cedula => ',ruta)
        rostro = cv2.cvtColor(rostro, cv2.COLOR_BGR2RGB)
        rostro_codificado = face_recognition.face_encodings(rostro)[0]
        rostros_codificados.append(rostro_codificado)
        print('terminada')
        c += 1

    return rostros_codificados

print('Comenzar Codificacion De Rostros')
print('Codificacion De Rostros En Proceso...')
# print(codificar_rostro(lista_img_rostros))
rotros_conocidos_codificados = codificar_rostro(lista_img_rostros)
print('Codificacion Completada')

# archivo = open("/home/steven/Desktop/Control_de_asistencia/RostrosCodificadosClaroCedula.p",'wb')
archivo = open("/home/steven/Asistencia/RostrosCodificadosClaro.p",'wb')
pickle.dump(rotros_conocidos_codificados,archivo)
archivo.close()
print('Archivo Guardado')

######################################################################################################################
fin = time.time()

print(f'el tiempo que tarda codificando {len(lista_img_rostros)} rostros es de aproximadamente {fin - inicio} segundos → {(fin - inicio)/60} minutos')
