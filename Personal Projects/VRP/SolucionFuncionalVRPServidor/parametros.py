import requests
import pandas as pd
from io import BytesIO
from shareplum import Office365



# LEER ARCHIVOS DESDE SHAREPOINT (RESPUESTAS FORMS)
def respuestas_fomulario():    

    """ Leer el archivo que contiene los ID y las coordenadas de los tranformadores """

    user = 'automatic@inmel.co'
    password = '//1nm3l.05'
    sitio = 'Automatic'
    url_base = 'https://inmelingenieria.sharepoint.com'
    ruta_respuesta_forms = 'Documentos%20compartidos%2FAplicaciones%2FVRP'

    config = {
        'sp_usuario': user,
        'sp_password': password,
        'sp_ruta_base': f'{url_base}',
        'sp_nombre_sitio': f'{sitio}',
        'sp_documentos_compartidos': f'{ruta_respuesta_forms}'
        }
    usuario = config['sp_usuario']
    password = config['sp_password']
    nombre_sitio = config['sp_nombre_sitio']
    ruta_base = config['sp_ruta_base']
    ruta_documentos = config['sp_documentos_compartidos']
    # Obtener cookie de autenticación
    authcookie = Office365(ruta_base, username=usuario, password=password).GetCookies()
    session = requests.Session()
    session.cookies = authcookie
    session.headers.update({'user-agent': 'python_bite/v1'})
    session.headers.update({'accept': 'application/json;odata=verbose'})
    # Obtener lista de archivos en la carpeta
    try:
        response = session.get(url=ruta_base + "/sites/" + nombre_sitio + "/_api/web/GetFolderByServerRelativeUrl('" + ruta_documentos + "')/Files")
        response.raise_for_status()
        archivos = response.json()
        enlace_completo = f"{ruta_respuesta_forms}/"
        lista_ruta_archivos = [enlace_completo + info_archivos['Name'] for info_archivos in archivos['d']['results']]
        # Leer y mostrar 
        for archivo in lista_ruta_archivos:
            if 'AUTOMATIC_Flujo_procesamiento_datos' in archivo and archivo.lower().endswith('.xlsx'):
                # Crear la ruta completa para leer archivo de Excel con pandas
                archivo_url = f"{ruta_base}/sites/{nombre_sitio}/{archivo}"
                archivo_response = session.get(archivo_url)
                archivo_response.raise_for_status()
                # Leer el contenido del archivo con pandas directamente desde la memoria
                contenido_archivo = BytesIO(archivo_response.content)
                df_respuesta_forms = pd.read_excel(contenido_archivo)
                return df_respuesta_forms            
    except Exception as e:
        print(f"Error al obtener la lista de archivos: {e}")
        return []
    

# LEER ARCHIVOS DESDE SHAREPOINT (RESPUESTAS FORMS)
def adjunto_fomulario():
    """ Leer el archivo que contiene los ID y las coordenadas de los tranformadores """

    user = 'automatic@inmel.co'
    password = '//1nm3l.05'
    sitio = 'Automatic'
    url_base = 'https://inmelingenieria.sharepoint.com'
    ruta_adjunto_forms = 'Documentos%20compartidos%2FAplicaciones%2FVRP%2FAdjuntos'

    df_respuesta_forms = respuestas_fomulario()
    nombre_adjunto = df_respuesta_forms.iloc[-1]['NOMBRE_ADJUNTO']

    config = {
        'sp_usuario': user,
        'sp_password': password,
        'sp_ruta_base': f'{url_base}',
        'sp_nombre_sitio': f'{sitio}',
        'sp_documentos_compartidos': f'{ruta_adjunto_forms}'
        }
    usuario = config['sp_usuario']
    password = config['sp_password']
    nombre_sitio = config['sp_nombre_sitio']
    ruta_base = config['sp_ruta_base']
    ruta_documentos = config['sp_documentos_compartidos']
    # Obtener cookie de autenticación
    authcookie = Office365(ruta_base, username=usuario, password=password).GetCookies()
    session = requests.Session()
    session.cookies = authcookie
    session.headers.update({'user-agent': 'python_bite/v1'})
    session.headers.update({'accept': 'application/json;odata=verbose'})
    # Obtener lista de archivos en la carpeta
    try:
        response = session.get(url=ruta_base + "/sites/" + nombre_sitio + "/_api/web/GetFolderByServerRelativeUrl('" + ruta_documentos + "')/Files")
        response.raise_for_status()
        archivos = response.json()
        enlace_completo = f"{ruta_adjunto_forms}/"
        lista_ruta_archivos = [enlace_completo + info_archivos['Name'] for info_archivos in archivos['d']['results']]
        # Crear la ruta completa para leer archivo de Excel con pandas
        archivo_url = f"{ruta_base}/sites/{nombre_sitio}/{ruta_adjunto_forms}/{nombre_adjunto}"
        archivo_response = session.get(archivo_url)
        archivo_response.raise_for_status()
        # Leer el contenido del archivo con pandas directamente desde la memoria
        contenido_archivo = BytesIO(archivo_response.content)
        df_respuesta_forms = pd.read_excel(contenido_archivo)
      
        return df_respuesta_forms            
    except Exception as e:
        print(f"Error al obtener la lista de archivos: {e}")
        return []


df_respuesta_forms = respuestas_fomulario()
bodega = df_respuesta_forms.iloc[-1]['COORDENADAS_BODEGA']
print('bodega solo arriba: ',bodega)
bodega = bodega.split('(')[-1]
bodega = bodega.split(')')[0]
latitud_bodega = bodega.split(';')[0]
longitud_bodega = bodega.split(';')[-1]

print(f"""
latitud_bodega:{latitud_bodega}
longitud_bodega:{longitud_bodega}
""")
modelo = df_respuesta_forms.iloc[-1]['MODELO']
maximo_ordenes = df_respuesta_forms.iloc[-1]['MAXIMO_ORDENES']
cantidad_cuadrillas = df_respuesta_forms.iloc[-1]['CANTIDAD_CUADRILLAS']
nombre_adjunto = df_respuesta_forms.iloc[-1]['NOMBRE_ADJUNTO']
fecha_hora_ejecucion = df_respuesta_forms.iloc[-1]['FECHA_HORA']
df_adjunto_forms = adjunto_fomulario()

print('df_adjunto_forms',df_adjunto_forms)
print('modelo',modelo)
print('maximo_ordenes',maximo_ordenes)
print('cantidad_cuadrillas',cantidad_cuadrillas)
print('nombre_adjunto',nombre_adjunto)
print('fecha_hora_ejecucion',fecha_hora_ejecucion)