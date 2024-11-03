############################################################ AGREGAR CARPETA DE PAQUETES AL PATH ##############################################################
import sys
import os
# obtén la ruta al directorio principal de tu proyecto
ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# añade la ruta al directorio principal de tu proyecto a sys.path
sys.path.append(ruta_proyecto)

######################################################### IMPORTANDO LIBRERIAS ##################################################################################
import os
import re
import time
import logging
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import tkinter as tk
from tkinter import messagebox

##################################################### CAPTURA DE TIEMPO #########################################################################################
# registra hora inicio del script
inicio_total = time.time()
# Capturar fecha actual
fecha_actual = datetime.datetime.now()

##################################################### DECLARACION DE LAS RUTAS y ID PARA GENERACION DE INFORMES #################################################
ruta_carpeta = f"C:\\Users\\jesus.ovalles\\Proyectos\\WebScraping SIMIT"
# leer archivo en donde se encuentran los ids y personas a leer
fuente = pd.read_excel(f"{ruta_carpeta}\\fuente_TEST.xlsx")
# lista que contiene las placas y documentos
fuente['ID1'] = fuente['ID1'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
fuente['ID2'] = fuente['ID2'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
fuente['ID3'] = fuente['ID3'].apply(lambda x: f"{float(x):.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
# concatenacion de los documentos y placas
ids = pd.concat([fuente['ID1'].astype(str), fuente['ID2'].astype(str), fuente['ID3'].astype(str)]).tolist()
ids = [id_ for id_ in ids if id_ != 'nan']  # Filtra los valores 'nan'
# rutas para guardar los informes de multas y comparendos del SIMIT
ruta_informe = f"{ruta_carpeta}\\Informe_SIMIT_Mensual_1.csv"
# ruta informe final
ruta_informe_final = f"{ruta_carpeta}\\Informe_Semanal_Completo_SIMIT_{fecha_actual.date()}.xlsx"
# crear DataFrame y ruta para guardar informe de control
control_errores_tiempos = pd.DataFrame(columns=['id','TIEMPO_EJECUCION','COMENTARIO'])
ruta_control = f"{ruta_carpeta}\\Control_Informe_SIMIT_{fecha_actual.date()}_1.xlsx"
titulos_inicio = ['Tipo_inicial','Notificación_inicial','Placa_inicial','Secretaría_inicial','Infracción_inicial','Estado_inicial','Valor_inicial','Valor_a_pagar_inicial']
titulos_internos = ['No. comparendo','Fecha','Hora','Dirección', 'Fecha revocatoria','Comparendo electrónico','Fecha notificación', 'Fuente comparendo','Secretaría','Agente','Código','Descripción','Valor','S.M.D.V:','Tipo documento','Número documento','Nombres','Apellidos','Tipo de infractor','Placa','No. Licencia del vehículo','Tipo','Servicio','No. Licencia','Fecha vencimiento','Categoría','Secretaría','Municipio comparendo','Localidad comuna','Radio acción','U.V.T:','Modalidad transporte','Pasajeros']
mapeo_titulos = {
    'Tipo_inicial': ['No. comparendo_inicial', 'Tipo_comparendo_multa_inicial', 'Fecha_comparendo_inicial'],
    'Infracción_inicial': ['Codigo_infraccion', 'Modo_deteccion', 'Tiene_proyeccion_pago'],
    'Estado_inicial': ['Estado_actual', 'Tiene_curso'],
    'Valor_a_pagar_inicial': ['Monto_a_pagar', 'Detalle_pago']
}

#################################################### CONFIGURACION DE PARAMETROS DEL WEB SCRAPING ###############################################################
# pagina del SIMIT
url = "https://fcm.org.co/simit/#/home-public"
# ruta del driver de chrome
path = "C:/Automatic/chromedriver-win64/chromedriver.exe"
# configurar el nivel de registro para Selenium
logging.basicConfig(level=logging.ERROR)  
# agregar múltiples opciones para Selenium
options = Options()
options.add_argument(path) # driver de Edge para el ingreso al navegador
#options.add_argument("--lang=es") # seleccionar el idioma
options.add_argument("--incognito") # activar modo incognito
# options.add_argument("--headless") # ejecutar sin interfaz grafica visible para ejecutar en segundo plano
options.add_argument("--disable-images") # desactivar imagenes
options.add_argument("--disable-notifications") # desactivar notificaciones
options.add_argument("--log-level=3")  # Silencia advertencias y errores innecesarios
options.add_argument("--disable-logging") # desactiva parte de los registros internos de Chromium
options.add_argument("--disable-gpu")  # A veces reduce errores gráficos
options.add_argument("--no-sandbox") # Reducen algunos errores de ejecucion al manejar recursod del navegador 
options.add_argument("--disable-dev-shm-usage") # Reducen algunos errores de ejecucion al manejar recursod del navegador 
options.add_argument("--force-device-scale-factor=0.5") # Establecer el zoom al 50% 
# driver = webdriver.Chrome(options=options)
driver = webdriver.Edge(options=options)
driver.get(url)
# maximizar ventana
driver.maximize_window()
# esperar a que la pagina cargue
time.sleep(5)

#################################################### FUNCIONES DE PROCESAMIENTO #################################################################################
def tratamiento(ruta_informe_csv,ruta_informe_final):
    df_inicio = pd.read_csv(ruta_informe_csv, dtype=str, sep=',')    
    #################################### TRATAMIENTO DE DATOS DF_INICIO ####################################
    # DIVIDIMOS LA COLUMNA "Tipo_inicial" en tres nuevas columnas utilizando str.split y expand=True
    columnas_resolucion_tipo_fecha = df_inicio['Tipo_inicial'].str.split(' ', expand=True)    
    # Asignamos los valores de las nuevas columnas al dataframe
    df_inicio['Resolucion_Multa_Comparendo'] = columnas_resolucion_tipo_fecha[0]
    df_inicio['Tipo infraccion'] = columnas_resolucion_tipo_fecha[1]
    # df_inicio['Fecha_Fecha'] = columnas_resolucion_tipo_fecha[2]
    df_inicio['Tipo cobro'] = columnas_resolucion_tipo_fecha[3].str.replace(":","")
    df_inicio['Fecha resolucion'] = columnas_resolucion_tipo_fecha[4]
    # antes de dividir la columna "Infracción_inicial", hacemos algunos reemplazos
    patron = re.compile(r'…|\.\.\.')
    df_inicio['Infracción_inicial'] = df_inicio['Infracción_inicial'].replace(patron, '', regex=True)
    df_inicio['Infracción_inicial'] = df_inicio['Infracción_inicial'].replace('  ', ' ', regex=True)
    # DIVIDIMOS LA COLUMNA "Infraciión" en tres nuevas columnas utilizando str.split y expand=True
    columnas_infraccion = df_inicio['Infracción_inicial'].str.split(' ', n=1, expand=True)
    # Asignamos los valores de las nuevas columnas al dataframe
    df_inicio['Infracción'] = columnas_infraccion[0]
    # antes de dividir la columna "Valor_inicial", hacemos algunos reemplazos
    df_inicio['Valor_inicial'] = df_inicio['Valor_inicial'].str.replace('$', ' ')
    df_inicio['Valor_inicial'] = df_inicio['Valor_inicial'].str.replace('Interés', ' ')
    # DIVIDIMOS LA COLUMNA "Valor_inicial" en tres nuevas columnas utilizando str.split y expand=True
    columnas_valor_interes = df_inicio['Valor_inicial'].str.split('     ', expand=True)
    # Asignamos los valores de las nuevas columnas al dataframe
    df_inicio['Valor Comparendo'] = columnas_valor_interes[0].str.replace(' ', '')
    df_inicio['Interes'] = columnas_valor_interes[1]
    # Hacemos algunos reemplazos en la columna "Valor_a_pagar_inicial"
    df_inicio['Valor_a_pagar_inicial'] = df_inicio['Valor_a_pagar_inicial'].str.replace('$', ' ')
    df_inicio['Valor_a_pagar_inicial'] = df_inicio['Valor_a_pagar_inicial'].str.replace('Detalle Pago', '')
    df_inicio['Valor_a_pagar_inicial'] = df_inicio['Valor_a_pagar_inicial'].str.replace(' ', '')
    columnas_a_eliminar = ['Tipo_inicial','Placa_inicial','Secretaría_inicial','Infracción_inicial','Valor_inicial','Valor']
    df_inicio['LLAVE'] =  df_inicio['Resolucion_Multa_Comparendo'].astype(str) + '_' + df_inicio['Placa'].astype(str) + '_' +  df_inicio['Código'].astype(str)
    # # #################################### UNION DE AMBOS DF CON SU RESPECTIVO TRATAMIENTO DE DATOS ####################################
    renombrar_columnas = {'Notificación_inicial':'Notificación', 'Estado_inicial':'Estado', 'Valor_a_pagar_inicial': 'Valor a pagar'}
    resultado = df_inicio.rename(columns=renombrar_columnas)
    # Reemplazar celdas vacias por -
    resultado.replace('', '-', inplace=True)
    resultado.fillna('-', inplace=True)
    # Dar orden especifico a las columnas
    orden_especifico = ['ID','Placa','Resolucion_Multa_Comparendo','Tipo infraccion','Tipo cobro','Fecha resolucion','Notificación','Infracción','Estado',
                        'Valor Comparendo','Interes','Valor a pagar','No. comparendo','Fecha','Hora','Dirección','Comparendo electrónico','Fecha notificación',
                        'Fuente comparendo','Secretaría','Agente','Código','Descripción','S.M.D.V:','Tipo documento','Número documento','Nombres','Apellidos',
                        'Tipo de infractor','No. Licencia del vehículo','Tipo','Servicio','No. Licencia','Fecha vencimiento','Categoría','Municipio comparendo',
                        'Localidad comuna','Radio acción','U.V.T:','Modalidad transporte','Pasajeros','Detalle','Resolucion_Multa_inicial','LLAVE']
    # Reordenar las columnas según el orden específico
    resultado = resultado[orden_especifico]
    # Guardar el DataFrame en un archivo Excel
    resultado.to_excel(ruta_informe_final, index=False)

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

# Asegurarte de que ambas listas tienen la misma longitud
def longitud_diccionarios(informacion_inicial_inicio,informacion_inicial_interna,ruta_informe):
    if len(informacion_inicial_inicio) == len(informacion_inicial_interna):
        for dic1, dic2 in zip(informacion_inicial_inicio, informacion_inicial_interna):
            dic1 = {clave: valor.replace('\n', ' ') if isinstance(valor, str) else valor for clave, valor in dic1.items()}
            d_combinado = {**dic1, **dic2}
            agregar_a_df(d_combinado, ruta_informe)
    else:
        longitud_maxima = max(len(informacion_inicial_inicio), len(informacion_inicial_interna))
        informacion_inicial_inicio.extend([{}] * (longitud_maxima - len(informacion_inicial_inicio)))
        informacion_inicial_interna.extend([{}] * (longitud_maxima - len(informacion_inicial_interna)))
        for dic1, dic2 in zip(informacion_inicial_inicio, informacion_inicial_interna):
            d_combinado = {**dic1, **dic2}
            agregar_a_df(d_combinado, ruta_informe)

# navega por las páginas utilizando los botones de paginación
def navegar_paginas(driver, contenedor, cant_pag):
    boton_activo = WebDriverWait(contenedor, 10).until(EC.presence_of_element_located((By.XPATH, './/button[@class="number-pagination active"]')))
    pagina_actual = int(boton_activo.get_attribute('value'))
    
    while cant_pag != pagina_actual:
        # Espera hasta que el contenedor esté presente
        contenedor = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb-4')))
        # Encuentra y hace clic en el botón de siguiente página
        boton_siguiente = driver.find_element(By.XPATH, '//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/a[2]')
        boton_siguiente.click()
        # Espera a que el nuevo botón activo se cargue
        boton_activo = WebDriverWait(contenedor, 10).until(EC.presence_of_element_located((By.XPATH, './/button[@class="number-pagination active"]')))
        pagina_actual = int(boton_activo.get_attribute('value'))
        # Espera breve para evitar sobrecargar la página
        time.sleep(1)
    return pagina_actual

# selecciona el maximo posible de multas por pagina para reducir el numer de paginas a recorrer
def seleccionar_maximo_dropdown(contenedor, xpath_dropdown='//*[@id="pageLengthSelect"]/option'):
    try:
        # Verificar si el dropdown existe
        if contenedor.find_element(By.XPATH, xpath_dropdown):
            opciones = contenedor.find_elements(By.XPATH, xpath_dropdown)
            # Convertir las opciones a una lista de enteros
            opciones_numericas = [int(opcion.text) for opcion in opciones]
            # Encontrar el valor máximo
            valor_maximo = max(opciones_numericas)
            # Seleccionar la opción correspondiente al valor máximo
            for opcion in opciones:
                if int(opcion.text) == valor_maximo:
                    opcion.click()  # Seleccionar la opción con el valor máximo
                    time.sleep(1)
                    break
    except (NoSuchElementException, TimeoutException):
        # Si no se encuentra el dropdown o surge un timeout, continúa sin detener el programa
        pass

# genera los lotes de placas o cedulas a procesar 
def cargar_lotes(documentos, tamano_lote):
    # Recorre en lotes según el tamaño definido
    for i in range(0, len(documentos), tamano_lote):
        lote = documentos[i:i + tamano_lote]
        # Itera sobre cada elemento dentro del lote
        for id in lote:
            yield id  # Retorna cada ID de forma individual

##################################################### COMIENZO DEL LOOP PARA TODAS LAS idS #######################################################################
# inicializar contador de celdas
contador_celda = 0
print(ids)
tamano_lote = 3

# Inicializar contador de IDs procesados
ids_procesados = 0  

for id in cargar_lotes(ids, tamano_lote):
# for id in ids:
    ids_procesados += 1
    print(id)
    # DEBIDO A QUE LA PAGINA DEL SIMIT SACA UN POOPUP CUANDO SE ABRE, SE DEBE DAR X AL AVISO
    try:
        # Haga clic en la x del mensaje
        dar_x_mantenimiento = WebDriverWait(driver,1).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="modalInformation"]/div/div/div[1]/button/span')))
        dar_x_mantenimiento.click()
        time.sleep(1)
    except:
        pass # si no existe el poopup, continua
     
    informacion_inicial_inicio = []
    informacion_inicial_interna = []
    try:
        inicio = time.time()
        # localizar cual es el boton de buscar
        body_html = driver.find_elements(By.XPATH, '/html/body')
        for texto in body_html:
            if 'Puntos de pago' in  texto.text: # usa el texto puntos de pago para validar en que pagina se esta
                ubicacion_boton_consultar = "//*[@id='consultar']" # boton busqueda en primera pagina
            else:
                ubicacion_boton_consultar = '//*[@id="btnNumDocPlaca"]' # boton busqueda en segunda pagina

        # espera que el campo de entrada sea visible y luego ingrese la cédula (es el mismo boton en ambas paginas)
        ingresar_id = WebDriverWait(driver,60).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtBusqueda']")))
        ingresar_id.send_keys(id)
        time.sleep(2)
        # haga clic en el botón de búsqueda
        boton_consultar = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH, f'{ubicacion_boton_consultar}')))
        boton_consultar.click()
        time.sleep(5)
        
        ##################################### NAVEGANDO A TRAVES DE LAS PAGINAS #################################################################################
        contenedor = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb-4')))
        
        # VERIFICA SI EL DOCUMENTO TIENE MULTAS ASOCIADAS
        if "No tienes comparendos ni multas registradas en Simit" not in contenedor.text:
            # EL DOCUMENTO TIENE MULTAS
            contenedor = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb-4')))
            
            # SI SALE EL POOPUP DE ESTADO DE CUENTA
            estado_cuenta = driver.find_elements(By.XPATH, '//*[@class="modal-content"]')
            for clave in estado_cuenta:
                if 'Estado de cuenta' in clave.text and 'Nit'in clave.text:
                    try:
                        boton_cedula = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-multiples-personas"]/div/div/div[2]/div[1]/label')))
                        boton_cedula.click()                    
                    except:
                        boton_cedula = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-multiples-personas"]/div/div/div[2]/div[2]/label')))
                        boton_cedula.click()
                    boton_continuar = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-multiples-personas"]/div/div/div[2]/div[3]/button')))
                    boton_continuar.click()
                    time.sleep(1)                
                    contenedor = driver.find_element(By.CLASS_NAME, 'pb-4') 
                elif 'Estado de cuenta' in clave.text and 'Cédula'in clave.text:
                    boton_cedula = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-multiples-personas"]/div/div/div[2]/div[1]/label')))
                    boton_cedula.click()
                    boton_continuar = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-multiples-personas"]/div/div/div[2]/div[3]/button')))
                    boton_continuar.click()
                    time.sleep(1)                
                    contenedor = driver.find_element(By.CLASS_NAME, 'pb-4')
                    
            # VERIFICA SI HAY PAGINACION
            contenido_anterior = None
            ultima_pagina = False
            seleccionar_maximo_dropdown(contenedor) 
            paginacion = contenedor.find_elements(By.XPATH, '//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/div/button')
            if len(paginacion) > 0:
                # SI TIENE PAGINACION
                # PRIMERA LISTA A COMPARAR
                lista_paginas_1 = []                
                for pagina in paginacion:
                    lista_paginas_1.append(pagina.text)                
                # SEGUNDA LISTA A COMPARAR
                lista_paginas_2 = []
                while lista_paginas_2 != lista_paginas_1:                
                    # OBTENER ULTIMA PAGINA
                    #ultima = lista_paginas_1[-1]
                    ultima = len(lista_paginas_1)
                    # DAR CLICK AL BOTON DE LA ULTIMA PAGINA
                    boton_ultima_pagina = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/div/button[{ultima}]')))
                    boton_ultima_pagina.click()
                    time.sleep(1)
                    # OBTENER SEGUNDA LISTA PARA COMPARAR
                    paginas_2 = contenedor.find_elements(By.XPATH, '//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/div/button')                    
                    for pagina_2 in paginas_2:
                        lista_paginas_2.append(pagina_2.text)
      
                    ultima = lista_paginas_2[-1] 
                    boton_ultima_pagina = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/a[2]')))
                    boton_ultima_pagina.click()
                    time.sleep(1)

                    paginas = contenedor.find_elements(By.XPATH, '//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/div/button')
                    lista_paginas_1 = []                
                    for pagina in paginas:
                        lista_paginas_1.append(pagina.text)

                pagina0 = 0
                pagina1=1
                while pagina0 != pagina1:
                    boton_uno = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/div/button[1]')))
                    pagina0 = boton_uno.get_attribute('value')
                    pagina0 = int(pagina0)
                    boton_uno.click()
                time.sleep(1)
                
                cantidad_paginas = int(lista_paginas_2[-1])
                print(f"Cantidad paginas: {cantidad_paginas}")
                
                cant_pag = 1
                while not ultima_pagina:
                    pagina_actual = navegar_paginas(driver, contenedor, cant_pag)
                    seleccionar_maximo_dropdown(contenedor) 
                    # obtiene cada elemento que contiene las multas y comparendos
                    comparendos_multas = contenedor.find_elements(By.XPATH, '//*[@id="multaTable"]/tbody/tr')
                    for multa in comparendos_multas:
                        if multa.text != '':                   
                            multa_data = multa.find_elements(By.TAG_NAME, "td")
                            data_dict_inicio = {titulos_inicio[i]: multa_data[i].text for i in range(len(titulos_inicio))}
                            informacion_inicial_inicio.append(data_dict_inicio)

                    # Obtener todos los comparendos y multas del listado
                    detalles = contenedor.find_elements(By.XPATH, '//*[contains(@id, "verDetalle")]')
                    lista_numeros_resolucion = []
                    for resolucion in detalles:
                        lista_numeros_resolucion.append(resolucion.text)
                    # limpia el listado e ingresa a cada multa   
                    cantidad_multas_inicials=1
                    for det in lista_numeros_resolucion:
                        if det != '':
                            pagina_actual = navegar_paginas(driver, contenedor, cant_pag)
                            if cant_pag == pagina_actual:
                                # intenta dar click en cada multa para ver detalle
                                try:    
                                    boton_link_detalle = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, f'/html/body/div[10]/div/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/table/tbody/tr[{cantidad_multas_inicials}]/td[1]/a/u')))
                                    boton_link_detalle.click()
                                except:
                                    boton_link_detalle = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.LINK_TEXT, f'{det}')))
                                    boton_link_detalle.click()
                                # obteniendo informacion de detalle
                                time.sleep(2)
                                contenedor_2 = driver.find_element(By.CLASS_NAME, 'h-100')
                                info_detalles = contenedor_2.find_elements(By.XPATH, '//*[@id="mainView"]/div/div/div[2]/div/div/div/div')
                                resolucion_multa_inicial = contenedor_2.find_element(By.XPATH, '//*[@id="detalleMultaDos"]/h6/span').text
                                cantidad_multas_inicials += 1
                                data_dict_interno = {titulo: None for titulo in titulos_internos}
                                
                                for item in info_detalles:
                                    titulo = item.find_element(By.TAG_NAME, 'label').text
                                    contenido = item.find_element(By.TAG_NAME, 'p').text
                                    if titulo in data_dict_interno:
                                        data_dict_interno[titulo] = contenido

                                detalle_interno = driver.find_element(By.ID, 'detalleMultaDos').text
                                detalle_interno = str(detalle_interno).split('\n')[0]
                                detalle_interno = str(detalle_interno).split(': ')[-1]                   
                                data_dict_interno['Detalle'] = f'{detalle_interno}'

                                data_dict_interno['ID'] = f'{id}'
                                data_dict_interno['Resolucion_Multa_inicial'] = f'{resolucion_multa_inicial}'                     
                                informacion_inicial_interna.append(data_dict_interno)
                                
                                boton_devolver = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mainView"]/div/div/div[1]/div/div[2]/button')))
                                boton_devolver.click()
                                time.sleep(2)
                                # subir al inicio de pagina
                                contenedor = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb-4')))  
                                seleccionar_maximo_dropdown(contenedor)                
                         
                    # contador de paginas       
                    cant_pag += 1                      
                    # contenido pagina actual
                    contenido_actual = driver.page_source  
                    # da click en boton siguiente
                    boton_siguiente = driver.find_element(By.XPATH, '//*[@id="mainView"]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[4]/a[2]')
                    boton_siguiente.click()
                    time.sleep(2)
                    contenedor = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'pb-4')))  

                    if pagina_actual == cantidad_paginas:
                        ultima_pagina = True
                    else:
                        contenido_anterior = contenido_actual

            # SI NO HAY PAGINACION
            else:
                comparendos_multas = contenedor.find_elements(By.XPATH, '//*[@id="multaTable"]/tbody/tr')
                for multa in comparendos_multas:
                    if multa.text != '':                   
                        multa_data = multa.find_elements(By.TAG_NAME, "td")
                        data_dict_inicio = {titulos_inicio[i]: multa_data[i].text for i in range(len(titulos_inicio))}
                        informacion_inicial_inicio.append(data_dict_inicio)
             
                # Obtener todos los comparendos y multas del listado
                detalles = contenedor.find_elements(By.XPATH, '//*[contains(@id, "verDetalle")]')
                lista_numeros_resolucion = []
                for resolucion in detalles:
                    lista_numeros_resolucion.append(resolucion.text)

                # limpia el listado e ingresa a cada multa
                cantidad_multas_inicials=1
                for det in lista_numeros_resolucion:
                    if det != '':
                        # intenta dar click en cada multa para ver detalle
                        try:    
                            boton_link_detalle = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, f'/html/body/div[10]/div/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/table/tbody/tr[{cantidad_multas_inicials}]/td[1]/a/u')))
                            boton_link_detalle.click()
                        except:
                            boton_link_detalle = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.LINK_TEXT, f'{det}')))
                            boton_link_detalle.click()

                        # obteniendo informacion de detalle
                        time.sleep(2)
                        contenedor_2 = driver.find_element(By.CLASS_NAME, 'h-100')
                        info_detalles = contenedor_2.find_elements(By.XPATH, '//*[@id="mainView"]/div/div/div[2]/div/div/div/div')
                        resolucion_multa_inicial = contenedor_2.find_element(By.XPATH, '//*[@id="detalleMultaDos"]/h6/span').text
                        cantidad_multas_inicials += 1
                        data_dict_interno = {titulo: None for titulo in titulos_internos}

                        for item in info_detalles:
                            titulo = item.find_element(By.TAG_NAME, 'label').text
                            contenido = item.find_element(By.TAG_NAME, 'p').text
                            if titulo in data_dict_interno:
                                data_dict_interno[titulo] = contenido

                        detalle_interno = driver.find_element(By.ID, 'detalleMultaDos').text
                        detalle_interno = str(detalle_interno).split('\n')[0]
                        detalle_interno = str(detalle_interno).split(': ')[-1]                   
                        data_dict_interno['Detalle'] = f'{detalle_interno}'

                        data_dict_interno['ID'] = f'{id}'
                        data_dict_interno['Resolucion_Multa_inicial'] = f'{resolucion_multa_inicial}'                     
                        informacion_inicial_interna.append(data_dict_interno)
                        
                        # volver a la pagina principal
                        boton_devolver = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mainView"]/div/div/div[1]/div/div[2]/button')))
                        boton_devolver.click()
                        time.sleep(2)

            # REESTRUCTURA DE DATOS        
            longitud_diccionarios(informacion_inicial_inicio,informacion_inicial_interna,ruta_informe)
        
        # SI EL DOCUMENTO NO TIENE MULTAS
        else:
            time.sleep(1)
        
        # borrar id antes de escribir el siguiente id
        ingresar_id = WebDriverWait(driver,1).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtBusqueda']")))
        ingresar_id.clear()
        
    except TimeoutException:
        driver.refresh()
        ingresar_id = WebDriverWait(driver,1).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtBusqueda']")))
        ingresar_id.clear()
        control_errores_tiempos.at[contador_celda,"id"] = f'{id}'    
        control_errores_tiempos.at[contador_celda,"COMENTARIO"] = f'Se presentó un error al ejecutar esta id: TimeoutException'
        time.sleep(5)
        ubicacion_boton_consultar = '//*[@id="btnNumDocPlaca"]'
    except NoSuchElementException:
        driver.refresh()
        ingresar_id = WebDriverWait(driver,1).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtBusqueda']")))
        ingresar_id.clear()
        control_errores_tiempos.at[contador_celda,"id"] = f'{id}'    
        control_errores_tiempos.at[contador_celda,"COMENTARIO"] = f'Se presentó un error al ejecutar esta id: NoSuchElementException'        
        time.sleep(5)
        ubicacion_boton_consultar = '//*[@id="btnNumDocPlaca"]'
    except ElementNotInteractableException:
        driver.refresh()
        ingresar_id = WebDriverWait(driver,1).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtBusqueda']")))
        ingresar_id.clear()
        control_errores_tiempos.at[contador_celda,"id"] = f'{id}'    
        control_errores_tiempos.at[contador_celda,"COMENTARIO"] = f'Se presentó un error al ejecutar esta id: ElementNotInteractableException'
        time.sleep(5)
        ubicacion_boton_consultar = '//*[@id="btnNumDocPlaca"]'
    except:
        driver.refresh()
        ingresar_id = WebDriverWait(driver,1).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtBusqueda']")))
        ingresar_id.clear()
        control_errores_tiempos.at[contador_celda,"id"] = f'{id}'    
        control_errores_tiempos.at[contador_celda,"COMENTARIO"] = f'Se presentó un error al ejecutar esta id: ErrorInesperado'
        time.sleep(5)
        ubicacion_boton_consultar = '//*[@id="btnNumDocPlaca"]'
    finally:
        # aumentar contador de celdas
        contador_celda += 1
        # control de tiempos
        fin = time.time()
        tiempo_fin = fin - inicio
        control_errores_tiempos.at[contador_celda,"id"] = f'{id}'
        control_errores_tiempos.at[contador_celda,'TIEMPO_EJECUCION'] = f'{tiempo_fin}'
        control_errores_tiempos.to_excel(ruta_control, index=False)

        # Verificar si se ha procesado un lote completo
        if len(ids) != ids_procesados:
            if ids_procesados % tamano_lote == 0:
                while True:
                    try:
                        user_input = messagebox.askquestion("Continuar", f"Se han procesado {tamano_lote} IDs. ¿Desea continuar con el siguiente lote?")
                    except KeyboardInterrupt:
                        print("\nProceso detenido por el usuario.")
                        driver.quit()
                        exit()
                    if user_input in ['yes', 'no']:
                        break
                if user_input == 'no':
                    print("Proceso detenido por el usuario.")
                    break
                else:
                    print("Continuando con el siguiente lote...")
                    time.sleep(1)

# luego de recorrer todas las ids, esto cierra la pagina web
driver.quit()

# LLAMAR FUNCION PARA EL TRATAMIENTO DE LOS DATOS
tratamiento(ruta_informe,ruta_informe_final)

# registra hora finalizacion del script
fin_final = time.time()
# calcular la duración
duracion = fin_final - inicio_total
print(f'''
      FINAL DE EJECUCIÓN
      Tiempo de ejecución:
      {duracion} Segundos
      {duracion/60} Minutos
      ''')