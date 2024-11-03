import math
import pandas as pd
# from Modelo_VRP_2 import VRP
from Modelo_CVRP_2 import CVRP
from parametros import respuestas_fomulario, adjunto_fomulario

# Función para ajustar el punto decimal en latitud
def ajustar_latitud(lat):
    lat_str = str(lat)
    if '.' not in lat_str:
        # Insertar el punto decimal después del primer dígito
        lat_str = lat_str[:1] + '.' + lat_str[1:]
    elif lat_str.index('.') != 1:
        # Mover el punto decimal a la posición correcta si no está en el segundo lugar
        lat_str = lat_str.replace('.', '')
        lat_str = lat_str[:1] + '.' + lat_str[1:]
    return float(lat_str)

def ajustar_longitud(lon):
    lon_str = str(lon)
    if '.' not in lon_str:
        # Insertar el punto decimal después del segundo dígito
        lon_str = lon_str[:3] + '.' + lon_str[3:]
    elif lon_str.index('.') != 3:
        # Mover el punto decimal a la posición correcta si no está en el cuarto lugar
        lon_str = lon_str.replace('.', '')
        lon_str = lon_str[:3] + '.' + lon_str[3:]
    return float(lon_str)

# PARAMETROS ESPERADOS PARA PASARSELOS AL MODELO QUE SE VAYA A EJECUTAR
# form = pd.read_excel('C:/Automatic/VRP/Excel_Parametros.xlsx')
# form = respuestas_fomulario()
# print(form)
# print()
# adjunto = adjunto_fomulario()
adjunto = pd.read_excel('C:\\Users\\steven.acosta\\Desktop\\SolucionFuncionalVRPServidor\\OT_industria_7_oct_German Neira Marin.xlsx')
# print(adjunto)

# Ruta donde vamos a guardar las salidas generadas para llevarlas al correo y sharepoint correspondientes
ruta_base = 'C:\\Users\\steven.acosta\\Desktop\\SolucionFuncionalVRPServidor\\ResultadoExistente'


# # OBTENER PARAMETROS
# model_to_run = form.iloc[-1]['MODELO'] # Modelo correspondiente a la última fecha y hora
# cant_cuadrilla = form.iloc[-1]['CANTIDAD_CUADRILLAS']
# max_carga_cuadrilla = form.iloc[-1]['MAXIMO_ORDENES']
# max_dist_cuadrilla = 100000
# nombre_adjunto = form.iloc[-1]['NOMBRE_ADJUNTO']
# destinatarios = [f"{form.iloc[-1]['CORREO']}"]
# nombre_usuario = destinatarios[0]
# nombre_usuario = nombre_usuario.split('@')[0]
# nombre_usuario = nombre_usuario.replace('.',' ')
# nombre_usuario = nombre_usuario.title()

# # CONDICIONES PARA ELEGIR LAS COORDENAS DE LA SALIDA SEGUN ELECCION EN EL FORMULARIO
# coordenadas_bodega_sede = form.iloc[-1]['COORDENADAS_BODEGA']
# bodega = coordenadas_bodega_sede.split('(')[-1]
# bodega = bodega.split(')')[0]

# latitud_bodega = bodega.split(';')[0]
# latitud_bodega = latitud_bodega.replace(',','.')
# latitud_bodega = float(latitud_bodega)

# longitud_bodega = bodega.split(';')[-1]
# longitud_bodega = longitud_bodega.replace(',','.')
# longitud_bodega = float(longitud_bodega)



# OBTENER PARAMETROS
model_to_run = 'Distancia y Capacidad - CVRP'
max_carga_cuadrilla = 139
cant_cuadrilla = 1
nombre_adjunto = 'OT_industria_7_oct_German Neira Marin.xlsx'

# CONDICIONES PARA ELEGIR LAS COORDENAS DE LA SALIDA SEGUN ELECCION EN EL FORMULARIO
coordenadas_bodega_sede = 'MANIZALES (5,464;-74,65175)'
bodega = coordenadas_bodega_sede.split('(')[-1]
bodega = bodega.split(')')[0]

latitud_bodega = bodega.split(';')[0]
latitud_bodega = latitud_bodega.replace(',','.')
latitud_bodega = float(latitud_bodega)

longitud_bodega = bodega.split(';')[-1]
longitud_bodega = longitud_bodega.replace(',','.')
longitud_bodega = float(longitud_bodega)




print( f'coordenadas {latitud_bodega},{longitud_bodega}')
# -------------------------------------------------------------------------------------

# Eliminar duplicados basados en la columna 'ID_ORDEN'
fuente = adjunto.drop_duplicates(subset=['ID_ORDEN'])

#--------------------------------------------------------------------------#
# Convertir los valores no numéricos a NaN
fuente['LATITUD'] = pd.to_numeric(fuente['LATITUD'], errors='coerce')
# Filtrar eliminando las filas que contienen NaN
fuente = fuente.dropna(subset=['LATITUD'])

# Convertir los valores no numéricos a NaN
fuente['LONGITUD'] = pd.to_numeric(fuente['LONGITUD'], errors='coerce')
# Filtrar eliminando las filas que contienen NaN
fuente = fuente.dropna(subset=['LONGITUD'])
#--------------------------------------------------------------------------#

# Aplicamos la función a la columna de latitud
fuente['LATITUD'] = fuente['LATITUD'].apply(ajustar_latitud)
fuente['LONGITUD'] = fuente['LONGITUD'].apply(ajustar_longitud)

if model_to_run == 'Distancia y Capacidad - CVRP':
    print('Ejecutando CVRP...')
    CVRP(fuente = fuente
        ,ruta_base = ruta_base
        ,len_cuadr = cant_cuadrilla
        ,capacity = max_carga_cuadrilla
        ,nombre_adjunto = nombre_adjunto
        ,latitud_bodega = latitud_bodega
        ,longitud_bodega = longitud_bodega
        )

# elif model_to_run == 'Solo por distancia - VRP':
#     print('Ejecutando VRP...')
#     VRP(fuente = fuente
#         ,ruta_base = ruta_base
#         ,len_cuadr = cant_cuadrilla
#         ,capacity = max_carga_cuadrilla
#         ,nombre_adjunto = nombre_adjunto
#         ,latitud_bodega = latitud_bodega
#         ,longitud_bodega = longitud_bodega
#         ,max_dist_cuadrilla = max_dist_cuadrilla
#         )