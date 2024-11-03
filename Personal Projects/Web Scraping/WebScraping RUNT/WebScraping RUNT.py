############################################################## AGREGAR CARPETA DE PAQUETES AL PATH ##############################################################
import sys
import os
# Obtén la ruta al directorio principal de tu proyecto
ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Añade la ruta al directorio principal de tu proyecto a sys.path
sys.path.append(ruta_proyecto)

############################################################### IMPORTANDO LIBRERIAS A USAR #####################################################################
import cv2
import time
import easyocr
import logging
import datetime
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
from selenium import webdriver
from email.message import EmailMessage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException, WebDriverException
import requests
from requests.exceptions import HTTPError

##################################################### FUNCIONES DE PROCESAMIENTO #################################################################################################
def resolver_captcha(driver, ocr):
    try:
        driver.execute_script("document.body.style.zoom='88%'")
        # Obtener las coordenadas del elemento de interés (por ejemplo, un botón)
        element = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[8]/div[1]/div[1]/img[1]')
        location = element.location
        size = element.size
        # Obtener la captura de pantalla completa
        screenshot = driver.get_screenshot_as_png()
        # Convertir la captura de pantalla a un objeto de imagen PIL
        screenshot = Image.open(BytesIO(screenshot))
        # Calcular las coordenadas de la región de interés
        left = location['x'] * 1.5
        top = location['y']
        right = location['x'] + size['width'] * 1.5 # amplia la ri mas a la derecha
        bottom = location['y'] + size['height']
        # Recortar la imagen a la región de interés
        region = screenshot.crop((left, top, right, bottom))
        captura_np = np.array(region)
        # Convertir de BGR a RGB (OpenCV usa BGR por defecto)
        captura_rgb = cv2.cvtColor(captura_np, cv2.COLOR_BGR2RGB)  
        # Convertir la imagen invertida a escala de grises
        captura_gris = cv2.cvtColor(captura_rgb, cv2.COLOR_RGB2GRAY)    
        # Aplicar suavizado gaussiano
        sigma = 2
        captura_suavizada = cv2.GaussianBlur(captura_gris, (5, 5), sigmaX=sigma, sigmaY=sigma)    
        # Aplicar dilatación para separar letras cercanas
        _, captura_umbralizada = cv2.threshold(captura_suavizada, 20,255, cv2.THRESH_BINARY)
        kernel_opening = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
        opening = cv2.morphologyEx(captura_umbralizada, cv2.MORPH_OPEN, kernel_opening)
        # Definir el factor de zoom
        zoom_factor = 0.7
        # Obtener las dimensiones de la imagen original
        height, width = captura_umbralizada.shape[:2]
        # Calcular nuevas dimensiones
        new_width, new_height = int(width * zoom_factor), int(height * zoom_factor)
        # Redimensionar la imagen
        zoomed_image = cv2.resize(opening, (new_width, new_height))
        # cv2.imshow('window_name', zoomed_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        captch_ocr = ocr.readtext(zoomed_image, paragraph=True)
        captch_ocr = str(captch_ocr[0][1])
        captch_ocr = captch_ocr.replace(' ','')
        return captch_ocr
    except:
        # Obtener las coordenadas del elemento de interés (por ejemplo, un botón)
        element = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[8]/div[1]/div[1]/img[1]')
        location = element.location
        size = element.size
        # Obtener la captura de pantalla completa
        screenshot = driver.get_screenshot_as_png()
        # Convertir la captura de pantalla a un objeto de imagen PIL
        screenshot = Image.open(BytesIO(screenshot))
        # Calcular las coordenadas de la región de interés
        left = location['x'] 
        # top = location['y'] - 38
        top = location['y'] - 70
        right = location['x'] + size['width'] + 700
        bottom = location['y'] + size['height'] - 28
        # Recortar la imagen a la región de interés
        region = screenshot.crop((left, top, right, bottom))
        captura_np = np.array(region)
        # Convertir de BGR a RGB (OpenCV usa BGR por defecto)
        captura_rgb = cv2.cvtColor(captura_np, cv2.COLOR_BGR2RGB)  
        # Convertir la imagen invertida a escala de grises
        captura_gris = cv2.cvtColor(captura_rgb, cv2.COLOR_RGB2GRAY)  
        # Aplicar suavizado gaussiano
        sigma = 2
        captura_suavizada = cv2.GaussianBlur(captura_gris, (5, 5), sigmaX=sigma, sigmaY=sigma)    
        # Aplicar dilatación para separar letras cercanas
        _, captura_umbralizada = cv2.threshold(captura_suavizada, 20,255, cv2.THRESH_BINARY)
        kernel_opening = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
        opening = cv2.morphologyEx(captura_umbralizada, cv2.MORPH_OPEN, kernel_opening)
        # Definir el factor de zoom
        zoom_factor = 0.7
        # Obtener las dimensiones de la imagen original
        height, width = captura_umbralizada.shape[:2]
        # Calcular nuevas dimensiones
        new_width, new_height = int(width * zoom_factor), int(height * zoom_factor)
        # Redimensionar la imagen
        zoomed_image = cv2.resize(opening, (new_width, new_height))
        # cv2.imshow('window_name', zoomed_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        captch_ocr = ocr.readtext(zoomed_image, paragraph=True)
        captch_ocr = str(captch_ocr[0][1])
        captch_ocr = captch_ocr.replace(' ','')
        return captch_ocr

##################################################### INGRESAR CAPTCHA CUANDO SEA CEDULA #################################################################################
def intento_captcha(driver, placa, documento):
    # DAR CLIC AL BOTON ACEPTAR
    boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
    boton_aceptar.click()
    driver.refresh()
    time.sleep(3)
    # SCROLL HACIA ABAJO
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")            
    # SCRIBIR PLACA Y CEDULA
    ingresar_placa = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noPlaca"]')))
    ingresar_placa.send_keys(placa)
    time.sleep(0.5)
    ingresar_documento = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noDocumento"]')))
    ingresar_documento.send_keys(documento)
    # DAR CLIC AL SELECTOR DE TIPO DE DOCUMENTO
    selector_tipo_documento = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#tipoDocumento')))
    # CREAR SELECTOR
    selector = Select(selector_tipo_documento)
    # ELEGIR "NIT"
    selector.select_by_visible_text('NIT')
    captch_ocr = resolver_captcha(driver, ocr)
    ingresar_captch = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="captchatxt"]')))
    ingresar_captch.send_keys(captch_ocr)
    time.sleep(0.5)            
    clic_consultar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[9]/button')))
    clic_consultar.click()

##################################################### INGRESAR CAPTCHA CUANDO SEA NIT ################################################################################
def intento_con_cedula_ciudadania(driver, placa, documento):
    # DAR CLIC AL BOTON ACEPTAR
    boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
    boton_aceptar.click()
    driver.refresh()
    time.sleep(3)
    # SCROLL HACIA ABAJO
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")            
    # SCRIBIR PLACA Y CEDULA
    ingresar_placa = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noPlaca"]')))
    ingresar_placa.send_keys(placa)
    time.sleep(0.5)
    ingresar_documento = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noDocumento"]')))
    ingresar_documento.send_keys(documento)
    # DAR CLIC AL SELECTOR DE TIPO DE DOCUMENTO
    selector_tipo_documento = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#tipoDocumento')))
    # CREAR SELECTOR
    selector = Select(selector_tipo_documento)
    # ELEGIR "NIT"
    selector.select_by_visible_text('Cédula Ciudadania')
    captch_ocr = resolver_captcha(driver, ocr)
    ingresar_captch = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="captchatxt"]')))
    ingresar_captch.send_keys(captch_ocr)
    time.sleep(0.5)            
    clic_consultar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[9]/button')))
    clic_consultar.click()

##################################################### OBTENER SOAT #################################################################################################
def soat(driver, titulos_columnas_soat):
    # Realiza el scroll hacia abajo según la cantidad de píxeles
    driver.execute_script(f"window.scrollBy(0, 1000);")
    time.sleep(1)
    # Dar clic al boton del soat
    boton_soat = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[5]/div[1]/h4/a')))
    boton_soat.click()
    time.sleep(2)
    # obtener la informacion del contenedor del soat
    informacion_soat = driver.find_elements(By.XPATH, '//*[@id="pnlPolizaSoatNacional"]/div/div/div/table/tbody/tr[1]') 
    # verificar si la lista del contenedor esta vacia y llenar la informacion en cada titulo correspondiente
    if len(informacion_soat) == 0:
        data_dict_soat = {titulos_columnas_soat[i]: 'NA' for i in range(len(titulos_columnas_soat))}
    else:
        # VERIFICAR QUE LOS DATOS EXISTAN
        verificar_informacion_soat = driver.find_element(By.XPATH, '//*[@id="pnlPolizaSoatNacional"]/div/div/div/table/tbody/tr[1]/td[1]')
        if verificar_informacion_soat.text == '':
            boton_soat.click()
            time.sleep(2)
            # obtener la informacion del contenedor del soat
            informacion_soat = driver.find_elements(By.XPATH, '//*[@id="pnlPolizaSoatNacional"]/div/div/div/table/tbody/tr[1]') 
        for soat in informacion_soat:
            soat_data = soat.find_elements(By.TAG_NAME, "td")
            data_dict_soat = {titulos_columnas_soat[i]: soat_data[i].text for i in range(len(titulos_columnas_soat))}
    return data_dict_soat


##################################################### OBTENER RESPOSABILIDAD CIVIL #########################################################################################
def civil(driver, titulos_columnas_responsabilidad_civil):
    # Realiza el scroll hacia abajo según la cantidad de píxeles
    driver.execute_script(f"window.scrollBy(0, 70);")
    time.sleep(1)
    # Dar clic al boton de responsabilidad civil
    boton_responsabilidad_civil = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[6]/div[1]/h4/a')))
    boton_responsabilidad_civil.click()
    time.sleep(2)    
    # obtener la informacion del contenedor de responsabilidad civil
    informacion_responsabilidad_civil = driver.find_elements(By.XPATH, '//*[@id="pnlPolizaResponsabilidadCivil"]/div/div/div/table/tbody/tr[1]')
    # verificar si la lista del contenedor esta vacia y llenar la informacion en cada titulo correspondiente
    if len(informacion_responsabilidad_civil) == 0:
        data_dict_civil = {titulos_columnas_responsabilidad_civil[i]: 'NA' for i in range(len(titulos_columnas_responsabilidad_civil))}
    else:
        # VERIFICAR QUE LOS DATOS EXISTAN
        verificar_informacion_civil = driver.find_element(By.XPATH, '//*[@id="pnlPolizaResponsabilidadCivil"]/div/div/div/table/tbody/tr[1]/td[1]')
        if verificar_informacion_civil.text == '':
            boton_responsabilidad_civil.click()
            time.sleep(2)      
            # obtener la informacion del contenedor de responsabilidad civil
            informacion_responsabilidad_civil = driver.find_elements(By.XPATH, '//*[@id="pnlPolizaResponsabilidadCivil"]/div/div/div/table/tbody/tr[1]')
        for civil in informacion_responsabilidad_civil:
            civil_data = civil.find_elements(By.TAG_NAME, "td")
            data_dict_civil = {titulos_columnas_responsabilidad_civil[i]: civil_data[i].text for i in range(len(titulos_columnas_responsabilidad_civil))}
    return data_dict_civil


##################################################### OBTENER RTM ############################################################################################################
def rtm(driver, titulos_columnas_rtm):
    # Realiza el scroll hacia abajo según la cantidad de píxeles
    driver.execute_script(f"window.scrollBy(0, 150);")
    time.sleep(1)
    # Dar clic al boton de rtm
    boton_rtm = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[7]/div[1]/h4/a')))
    boton_rtm.click()
    time.sleep(2)      
    # obtener la informacion del contenedor de rtm y llenar la informacion en cada titulo correspondiente
    informacion_rtm = driver.find_elements(By.XPATH, '//*[@id="pnlRevisionTecnicoMecanicaNacional"]/div/div/div/table/tbody/tr[1]')
    # verificar si la lista del contenedor esta vacia
    if len(informacion_rtm) == 0:
        data_dict_rtm = {titulos_columnas_rtm[i]: 'NA' for i in range(len(titulos_columnas_rtm))}
    else:
        # VERIFICAR QUE LOS DATOS EXISTAN
        verificar_informacion_rtm = driver.find_element(By.XPATH, '//*[@id="pnlRevisionTecnicoMecanicaNacional"]/div/div/div/table/tbody/tr[1]/td[1]')
        if verificar_informacion_rtm.text == '':
            boton_rtm.click()
            time.sleep(2)
            # obtener la informacion del contenedor de rtm y llenar la informacion en cada titulo correspondiente
            informacion_rtm = driver.find_elements(By.XPATH, '//*[@id="pnlRevisionTecnicoMecanicaNacional"]/div/div/div/table/tbody/tr[1]')
        for rtm in informacion_rtm:            
            rtm_data = rtm.find_elements(By.TAG_NAME, "td")
            data_dict_rtm = {titulos_columnas_rtm[i]: rtm_data[i].text for i in range(len(titulos_columnas_rtm))}
    return data_dict_rtm

##################################################### OBTENER TARJETA DE OPERACION PARTE 1 ########################################################################################
def operacion_1(driver, titulos_columnas_tarjeta_operacion_1):
    # Realiza el scroll hacia abajo según la cantidad de píxeles
    driver.execute_script(f"window.scrollBy(0,1100);")
    time.sleep(1)
    # Dar clic al boton de rtm
    boton_operacion = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[15]/div[1]/h4/a')))
    boton_operacion.click()
    time.sleep(2)            
    # obtener la informacion del contenedor 1 de operacion y llenar la informacion en cada titulo correspondiente
    informacion_operacion_1 = driver.find_elements(By.XPATH, '//*[@id="pnlTarjetOperacion"]/div/div/div/div/div[2]')
    # crear lista vacia para posteriormente llenarla con los datos del elemento
    lista_elementos_1 = []
    # VERIFICAR QUE LOS DATOS EXISTAN
    verificar_informacion_operacion_1 = driver.find_element(By.XPATH, '//*[@id="pnlTarjetOperacion"]/div/div/div/div[1]/div[2]')
    if verificar_informacion_operacion_1.text == '':
        boton_operacion.click()
        time.sleep(2)
        # obtener la informacion del contenedor 1 de operacion y llenar la informacion en cada titulo correspondiente
        informacion_operacion_1 = driver.find_elements(By.XPATH, '//*[@id="pnlTarjetOperacion"]/div/div/div/div/div[2]')
    # recorrer la lista de cada tag
    for elemento_op_1 in informacion_operacion_1:
        if elemento_op_1.text == '':
            lista_elementos_1.append('NA')
        else:            
            lista_elementos_1.append(elemento_op_1.text)
    data_dict_operacion_1 = dict(zip(titulos_columnas_tarjeta_operacion_1,lista_elementos_1))
    return data_dict_operacion_1


##################################################### OBTENER TARJETA DE OPERACION PARTE 2 ########################################################################################
def operacion_2(driver, titulos_columnas_tarjeta_operacion_2):
    # obtener la informacion del contenedor 1 de operacion y llenar la informacion en cada titulo correspondiente
    informacion_operacion_2 = driver.find_elements(By.XPATH, '//*[@id="pnlTarjetOperacion"]/div/div/div/div/div[4]')
    # crear lista vacia para posteriormente llenarla con los datos del elemento
    lista_elementos_2 = []
    # recorrer la lista de cada tag
    for elemento_op_2 in informacion_operacion_2:
        if elemento_op_2.text == '':
            lista_elementos_2.append('NA')
        else:
            lista_elementos_2.append(elemento_op_2.text)
    data_dict_operacion_2 = dict(zip(titulos_columnas_tarjeta_operacion_2,lista_elementos_2)) 
    return data_dict_operacion_2

##################################################### ELIMINAR ARCHIVOS ##############################################################################################
def elimnar_archivos(ruta_carpeta):
    extension = '.xlsx'
    # Recorre el directorio en busca de archivos con la extensión especificada
    for archivo in os.listdir(ruta_carpeta):
        if 'Completo' not in archivo and archivo.endswith(extension) and 'A1' not in archivo and archivo.endswith(extension) and 'Control' not in archivo and archivo.endswith(extension):
            archivo_a_eliminar = os.path.join(ruta_carpeta, archivo)            
            # Verificamos si el archivo existe antes de intentar eliminarlo
            if os.path.exists(archivo_a_eliminar):
                try:
                    # Eliminamos el archivo
                    os.remove(archivo_a_eliminar)
                except OSError as error:
                    print(f"Error al eliminar el archivo {archivo_a_eliminar}: {error}")
                    continue
            else:
                print(f"El archivo {archivo_a_eliminar} no existe.")

##################################################### AGREGAR DATOS A DF ############################################################################################
def agregar_a_df(d_combinado, ruta_informe):
    # Convertir el diccionario en DataFrame
    df = pd.DataFrame([d_combinado])
    # Verificar si el archivo ya existe
    if not os.path.exists(ruta_informe):
        # Si el archivo no existe, crearlo y escribir la cabecera
        df.to_csv(ruta_informe, index=False, mode='w', header=True, encoding='utf-8-sig')
    else:
        # Si el archivo existe, añadir los datos sin la cabecera
        df.to_csv(ruta_informe, index=False, mode='a', header=False, encoding='utf-8-sig')

##################################################### CAPTURA DE TIEMPO ###############################################################################################
# Capturar fecha actual
fecha_actual = datetime.datetime.now()

##################################################### DECLARACION DE LAS RUTAS PARA GENERACION DE INFORMES ############################################################
ruta_carpeta = "C:\\Users\\jesus.ovalles\\Proyectos\\WebScraping RUNT" 
ruta_informe = ruta_carpeta + f"\\Informe_Completo_RUNT.csv"
ruta_control = ruta_carpeta + f"\\Control_Informe_runt.xlsx"

##################################################### DECLARACION DE LAS RUTAS PARA GENERACION DE INFORMES ############################################################
# Leer archivo en donde se encuentran las placas y personas a leer y convertirlas en listas para luego iterar
vehiculos = pd.read_excel(ruta_carpeta + "\\A1_Placas_RUNT.xlsx")
placas = vehiculos['PLACA'].tolist()
documentos = vehiculos['CEDULA'].tolist()
# Crear lista de titulos para cada DataFrame
titulos_columnas_soat = ['SOAT NUMERO DE POLIZA','SOAT FECHA EXPEDICION','SOAT FECHA INICIO DE VIGENCIA','SOAT FECHA FIN DE VIGENCIA','SOAT CODIGO TARIFA','SOAT ENTIDAD EXPIDE SOAT','SOAT ESTADO']
titulos_columnas_responsabilidad_civil = ['CIVIL NUMERO DE POLIZA','CIVIL FECHA EXPEDICION','CIVIL FECHA INICIO DE VIGENCIA','CIVIL FECHA FIN DE VIGENCIA','CIVIL ENTIDAD QUE EXPIDE','CIVIL TIPO DE POLIZA','CIVIL ESTADO', 'CIVIL DETALLE']
titulos_columnas_rtm = ['RTM TIPO REVISION','RTM FECHA EXPEDICION','RTM FECHA VIGENCIA','RTM CDA EXPIDE RTM','RTM VIGENTE','RTM NRO. CERTIFICADO', 'RTM INFORMACION CONSISTENTE']
titulos_columnas_tarjeta_operacion_1 = ['OPERACION EMPRESA AFILIADORA', 'OPERACION RADIO DE ACCIÓN', 'OPERACION MODALIDAD DE SERVICIO', 'OPERACION FECHA DE EXPEDICIÓN (DD/MM/AAAA)', 'OPERACION FECHA FIN DE VIGENCIA (DD/MM/AAAA)']
titulos_columnas_tarjeta_operacion_2 = ['OPERACION MODALIDAD DE TRANSPORTE', 'OPERACION NRO. TARJETA DE OPERACIÓN', 'OPERACION FECHA INICIO DE VIGENCIA (DD/MM/AAAA)', 'OPERACION ESTADO']
titulos_columnas_control = ['PLACA','TIEMPO_EJECUCION','COMENTARIO']
# crear DataFrames vacios
df_control = pd.DataFrame(columns=titulos_columnas_control)
# crear diccionario de vacios
titulos = titulos_columnas_soat + titulos_columnas_responsabilidad_civil + titulos_columnas_rtm + titulos_columnas_tarjeta_operacion_1 + titulos_columnas_tarjeta_operacion_2
diccionario_sin_registros = {titulo: '-' for titulo in titulos}
##################################################### CONFIGURACION DE PARAMETROS DEL WEB SCRAPING #####################################################################
# Pagina del runt
url = "https://www.runt.gov.co/consultaCiudadana/#/consultaVehiculo"
# url = "https://www.runt.gov.co/consultaCiudadana/un"
# Ruta del driver de chrome
path = "C:\\Automatic\\chromedriver-win64\\chromedriver.exe"
# Configurar el nivel de registro para Selenium
# logging.basicConfig(level=logging.ERROR)
# Agregar múltiples opciones para Selenium
options = Options()
options.add_argument(path) # Driver de Google para el ingreso al navegador
options.add_argument("--lang=es") # Seleccionar el idioma
# options.add_argument("--headless") # Ejecutar sin interfaz grafica visible para ejecutar en segundo plano
options.add_argument("--incognito") # Activar modo incognito
driver = webdriver.Chrome(options=options)
# driver = webdriver.Edge()
driver.get(url)
# driver.set_window_size(3500, 3500)
# Maximizar ventana
driver.maximize_window()
# Esperar a que la pagina cargue
time.sleep(5)

##################################################### COMIENZO DEL LOOP PARA TODAS LAS PLACAS ##########################################################################
# Configurar OCR
ocr = easyocr.Reader(["es"], gpu=False)
contador_celda = 0

for placa, documento in zip(placas, documentos):
    # Ajustar el zoom al 75%
    driver.execute_script("document.body.style.zoom='88%'")
    
    print(placa)
    # Establecer el tipo de documento inicial
    tipo_documento = 'NIT'
    # Establecer validacion inicial
    validacion = 'EXITOSO'
    try:
        # Registrar el tiempo de inicio
        inicio = time.time()
        # Respuesta del servidor. Exitoso 200
        respuesta = requests.get(url)
        # Asegúrate de que la respuesta fue exitosa (200 OK), levantar un error (HTTPError 404). 
        respuesta.raise_for_status()
        # SCROLL HACIA ABAJO
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # #ESCRIBIR PLACA Y CEDULA
        ingresar_placa = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noPlaca"]')))
        ingresar_placa.send_keys(placa)
        time.sleep(1)
        ingresar_documento = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noDocumento"]')))
        ingresar_documento.send_keys(documento)
        # DAR CLIC AL SELECTOR DE TIPO DE DOCUMENTO
        selector_tipo_documento = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#tipoDocumento')))
        # CREAR SELECTOR
        selector = Select(selector_tipo_documento)
        # ELEGIR "NIT"
        selector.select_by_visible_text('NIT')
        # RESOLVER CAPTCHA
        captch_ocr = resolver_captcha(driver, ocr)
        ingresar_captch = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="captchatxt"]')))
        ingresar_captch.send_keys(captch_ocr)
        time.sleep(0.5)
        clic_consultar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[9]/button')))
        clic_consultar.click()
        time.sleep(3)
        elemento_en_popup = driver.find_element(By.XPATH, '//*[@id="msgConsulta"]')
        time.sleep(1)
        if 'la imagen no coincide' in elemento_en_popup.text.lower() or 'resaltados en rojo' in elemento_en_popup.text.lower() or 'expirado' in elemento_en_popup.text.lower():        
            while 'la imagen no coincide' in elemento_en_popup.text.lower() or 'resaltados en rojo' in elemento_en_popup.text.lower():
                intento_captcha(driver, placa, documento)
                elemento_en_popup = driver.find_element(By.XPATH, '//*[@id="msgConsulta"]')
                time.sleep(1)
            elemento_en_popup = driver.find_element(By.XPATH, '//*[@id="msgConsulta"]')
            #Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT.
            if 'no hay información registrada' in elemento_en_popup.text.lower() or 'resaltados en rojo' in elemento_en_popup.text.lower() or 'expirado' in elemento_en_popup.text.lower():        
                # DAR CLIC AL BOTON ACEPTAR
                boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
                boton_aceptar.click()
                validacion = "SIN REGISTRO"
                tipo_documento = "DESCONOCIDO"
                dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
                # Combinar diccionarios
                d_combinado = {**dic_validacion,**diccionario_sin_registros}
                # llamar funcion para agregar datos a df
                agregar_a_df(d_combinado, ruta_informe)
                fin = time.time()
                tiempo_fin = fin - inicio
                df_control.at[contador_celda,"PLACA"] = f'{placa}'
                df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
                df_control.to_excel(ruta_control, index=False)
                contador_celda += 1
                driver.refresh()       
                continue  

        if 'los datos registrados no corresponden' in elemento_en_popup.text.lower():
            time.sleep(1)
            # DAR CLIC AL BOTON ACEPTAR
            boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
            boton_aceptar.click()
            # DAR CLIC AL SELECTOR DE TIPO DE DOCUMENTO
            selector_tipo_documento = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#tipoDocumento')))
            # CREAR SELECTOR
            selector = Select(selector_tipo_documento)
            # ELEGIR "NIT"
            selector.select_by_visible_text('NIT')
            # RESOLVER CAPTCHA
            captch_ocr = resolver_captcha(driver, ocr)
            ingresar_captch = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="captchatxt"]')))
            ingresar_captch.send_keys(captch_ocr)
            time.sleep(0.5)
            clic_consultar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[9]/button')))
            clic_consultar.click()
            time.sleep(3)
            elemento_en_popup = driver.find_element(By.XPATH, '//*[@id="msgConsulta"]')
            time.sleep(1)
            if 'la imagen no coincide' in elemento_en_popup.text.lower() or 'resaltados en rojo' in elemento_en_popup.text.lower():            
                while 'la imagen no coincide' in elemento_en_popup.text.lower() or 'resaltados en rojo' in elemento_en_popup.text.lower():
                    intento_con_cedula_ciudadania(driver, placa, documento)
                    elemento_en_popup = driver.find_element(By.XPATH, '//*[@id="msgConsulta"]')
                    time.sleep(1)
                #Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT.
                if 'no hay información registrada' in elemento_en_popup.text.lower():        
                    # DAR CLIC AL BOTON ACEPTAR
                    boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
                    boton_aceptar.click()
                    validacion = "SIN REGISTRO"
                    tipo_documento = "DESCONOCIDO"
                    dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
                    # Combinar diccionarios
                    d_combinado = {**dic_validacion,**diccionario_sin_registros}
                    # llamar funcion para agregar datos a df
                    agregar_a_df(d_combinado, ruta_informe)
                    fin = time.time()
                    tiempo_fin = fin - inicio
                    df_control.at[contador_celda,"PLACA"] = f'{placa}'
                    df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
                    df_control.to_excel(ruta_control, index=False)
                    contador_celda += 1
                    driver.refresh()
                    continue  
            elemento_en_popup = driver.find_element(By.XPATH, '//*[@id="msgConsulta"]')
            time.sleep(1)
            if 'los datos registrados no corresponden' in elemento_en_popup.text.lower() or 'resaltados en rojo' in elemento_en_popup.text.lower():
                time.sleep(1)
                # DAR CLIC AL BOTON ACEPTAR
                boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
                boton_aceptar.click()
                ingresar_placa = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noPlaca"]')))
                ingresar_placa.clear()
                time.sleep(0.5)
                ingresar_documento = WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="noDocumento"]')))
                ingresar_documento.clear()
                # DAR CLIC AL SELECTOR DE TIPO DE DOCUMENTO
                selector_tipo_documento = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#tipoDocumento')))
                # CREAR SELECTOR
                selector = Select(selector_tipo_documento)
                # ELEGIR "NIT"
                selector.select_by_visible_text('NIT')
                contador_celda += 1
                tipo_documento = 'DESCONOCIDO'
                validacion = 'LOS DATOS NO CORRESPONDEN'
                dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
                # Combinar diccionarios
                d_combinado = {**dic_validacion,**diccionario_sin_registros}
                # llamar funcion para agregar datos a df
                agregar_a_df(d_combinado, ruta_informe)
                fin = time.time()
                tiempo_fin = fin - inicio
                df_control.at[contador_celda,"PLACA"] = f'{placa}'
                df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
                df_control.to_excel(ruta_control, index=False)
                contador_celda += 1
                driver.refresh()          
                continue
            tipo_documento = "CEDULA"
        #Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT.
        if 'no hay información registrada' in elemento_en_popup.text.lower():
            # DAR CLIC AL BOTON ACEPTAR
            boton_aceptar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
            boton_aceptar.click()
            validacion = "SIN REGISTRO"
            tipo_documento = "DESCONOCIDO"
            dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
            # Combinar diccionarios
            d_combinado = {**dic_validacion,**diccionario_sin_registros}
            # llamar funcion para agregar datos a df
            agregar_a_df(d_combinado, ruta_informe)     
            fin = time.time()
            tiempo_fin = fin - inicio
            df_control.at[contador_celda,"PLACA"] = f'{placa}'
            df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
            df_control.to_excel(ruta_control, index=False)
            contador_celda += 1
            driver.refresh()
            continue 
            
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # OBTENER INFORMACIÓN DE PÓLIZAS SOAT
        dict_soat = soat(driver, titulos_columnas_soat)
        # OBTENER INFORMACIÓN DE PÓLIZAS RESPONSABILIDAD CIVIL
        dict_civil = civil(driver, titulos_columnas_responsabilidad_civil)
        # OBTENER INFORMACIÓN DE REVISION TECNOMECANICA
        dict_rtm = rtm(driver, titulos_columnas_rtm)
        # OPERACION PARTE 1
        dict_operacion_1 = operacion_1(driver, titulos_columnas_tarjeta_operacion_1)
        # OPERACION PARTE 2
        dict_operacion_2 = operacion_2(driver, titulos_columnas_tarjeta_operacion_2)

        # Combinar diccionarios
        d_combinado = {**dic_validacion,**dict_soat, **dict_civil, **dict_rtm, **dict_operacion_1, **dict_operacion_2}

        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)

        # DAR CLIC AL BOTON DE OTRA CONSULTA
        clic_otra_consultar = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/button')))
        clic_otra_consultar.click()
        time.sleep(2)

        # Aumentar contador de celdas
        contador_celda += 1
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.to_excel(ruta_control, index=False)
        driver.refresh()            

    except IndexError:
        comentario = f'Se presentó un error al resolver el captch, no se encontró la imagen: IndexError'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        contador_celda += 1
        driver.refresh()
        time.sleep(3)    
        continue
    except NoSuchElementException:        
        comentario = f'No encontró el elemento especificado en la página web: NoSuchElementException'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        contador_celda += 1
        driver.refresh()
        time.sleep(3)    
        continue       
    except ElementNotInteractableException:        
        comentario = f'Se intentó interactuar con un elemento de la página que no es interactuable : ElementNotInteractableException'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        contador_celda += 1
        driver.refresh()
        time.sleep(3)    
        continue 
    except StaleElementReferenceException:        
        comentario = f'Un elemento se ha vuelto obsoleto debido a cambios en la página (POPUP): StaleElementReferenceException'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        contador_celda += 1
        driver.refresh()
        time.sleep(3)    
        continue
    except TimeoutException:        
        comentario = f'Se excedió el tiempo de espera especificado para una operación (Error página): TimeoutException'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        contador_celda += 1
        driver.refresh()
        time.sleep(3)
        print()
        print('''
            ELEMENTO NO ENCONTRADO
            ''')
        print()
        # Volver a la pagina inicial
        driver.get(url)
        driver.refresh()
        # Respuesta del servidor. Exitoso 200
        respuesta = requests.get(url)
        print('Respuesta_1 = ', respuesta)
        continue
    except WebDriverException:        
        comentario = f'Desconexión del navegador: WebDriverException'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        # contador_celda += 1
        # driver.refresh()
        # time.sleep(3)
        print()
        print('''
            ERROR CONEXIÓN INTERNET
            ''')
        print()
        break
    except HTTPError:      
        comentario = f'El servidor no ha encontrado la página solicitada: HTTPError 404'
        validacion = "ERROR"
        tipo_documento = "-"
        dic_validacion = {'VALIDACION':validacion, 'PLACA':placa, 'DOCUMENTO':documento, 'TIPO_DOCUMENTO':tipo_documento}
        # Combinar diccionarios
        d_combinado = {**dic_validacion,**diccionario_sin_registros}
        # llamar funcion para agregar datos a df
        agregar_a_df(d_combinado, ruta_informe)
        fin = time.time()
        tiempo_fin = fin - inicio
        df_control.at[contador_celda,"PLACA"] = f'{placa}'
        df_control.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        df_control.at[contador_celda,"COMENTARIO"] = comentario
        df_control.to_excel(ruta_control, index=False)
        contador_celda += 1
        # Volver a la pagina inicial
        driver.get(url)
        driver.refresh()
        # Respuesta del servidor. Exitoso 200
        respuesta = requests.get(url)
        print('Respuesta_1 = ', respuesta)
        time.sleep(5)
        continue

driver.quit()
# time.sleep(1)
# elimnar_archivos(ruta_carpeta)

print()
print('''
      EL PROGRAMA HA FINALIZADO
      ''')
print()
