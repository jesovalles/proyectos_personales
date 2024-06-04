# librerias
import random
from time import sleep
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# opciones de navegación
options = webdriver.ChromeOptions()
# options.add_argument('--start-maximized')  # maximizar ventana
options.add_argument('--disable-extensions')  # deshabilitar extensiones
options.add_argument('--incognito')  # activar modo incógnito
# options.add_argument("--headless")  # ejecutar sin interfaz gráfica visible para ejecutar en segundo plano
options.add_argument("--disable-images")  # desactivar imágenes
options.add_argument("--disable-notifications")  # desactivar notificaciones

# URL de la página a scrapear
url = 'https://www.olx.in/cars_c84'

# iniciar driver
driver = webdriver.Chrome(options=options)
driver.get(url)
# maximizar ventana
driver.maximize_window()
# esperar a que la pagina cargue
time.sleep(5)

# esperar a que los elementos se carguen en la página
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//li[@data-aut-id="itemBox"]')))
except Exception as e:
    print(f"No se pudo cargar la página correctamente: {e}")
    driver.quit()
    exit()

# busco el boton para cargar mas informacion
boton = driver.find_element(By.XPATH, '//button[@data-aut-id="btnLoadMore"]')
for i in range(3): # voy a darle click en cargar mas 3 veces
    try:
        # le doy click
        boton.click()
        # espero que cargue la informacion dinamica
        time.sleep(20)
        # busco el boton nuevamente para darle click en la siguiente iteracion
        boton = driver.find_element(By.XPATH, '//button[@data-aut-id="btnLoadMore"]')
        # esperar a que la pagina cargue
        time.sleep(20)
    except:
        # si hay algun error, rompo el lazo.
        break
        
# encuentro cual es el XPATH (li) de cada elemento donde esta la informacion que quiero extraer
autos = driver.find_elements(By.XPATH, '//li[@data-aut-id="itemBox"]')

# listas para almacenar los datos a scrapear
precios = []
descripciones = []

# recorro cada uno de los anuncios que he encontrado
for auto in autos:
    # por cada anuncio hallo el precio
    precio = auto.find_element(By.XPATH, './/span[@data-aut-id="itemPrice"]').text
    precios.append(precio)
    # por cada anuncio hallo la descripcion
    descripcion = auto.find_element(By.XPATH, './/div[@data-aut-id="itemTitle"]').text
    descripciones.append(descripcion)
    
# cierra el navegador
driver.quit()

# crea un DataFrame con los datos
df = pd.DataFrame({'Precio': precios, 'Descripcion': descripciones})

# guarda el DataFrame en un archivo CSV con codificación UTF-8
df.to_csv('autos.csv', index=False, encoding='utf-8')

print("Datos guardados en autos.csv")