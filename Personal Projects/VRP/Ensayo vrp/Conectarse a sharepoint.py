import re
import os
import sys
import time
import pytz
import json
import psutil
import urllib3
import requests
import keyboard
import pyperclip
import pyautogui
import webbrowser
import numpy as np
import pandas as pd
import tkinter as tk
from io import BytesIO
from datetime import datetime
from tkinter import PhotoImage
from tkinter import messagebox
from shareplum import Office365


user = 'automatic@inmel.co'
password = '//1nm3l.05'
sitio = 'Automatic'
url_base = 'https://inmelingenieria.sharepoint.com'
ruta_respuesta_forms = 'Documentos%20compartidos%2FAplicaciones%2FVRP'
ruta_adjunto_forms = 'Documentos%20compartidos%2FAplicaciones%2FVRP%2FAdjuntos'


# LEER ARCHIVOS DESDE SHAREPOINT (RESPUESTAS FORMS)
def leer_archivo_respuestas_fomulario(user,password,sitio,url_base,ruta_respuesta_forms):
    """ Leer el archivo que contiene los ID y las coordenadas de los tranformadores """
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
def leer_archivo_adjunto_fomulario(user,password,sitio,url_base,ruta_adjunto_forms,nombre_adjunto):
    """ Leer el archivo que contiene los ID y las coordenadas de los tranformadores """
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


df_respuesta_forms = leer_archivo_respuestas_fomulario(user,password,sitio,url_base,ruta_respuesta_forms)
nombre_adjunto = df_respuesta_forms.iloc[-1]['ADJUNTO']
df_adjunto_forms = leer_archivo_adjunto_fomulario(user,password,sitio,url_base,ruta_adjunto_forms,nombre_adjunto)
print(df_adjunto_forms)

time.sleep(20)