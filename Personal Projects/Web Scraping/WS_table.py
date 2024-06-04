# librerias
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# opciones de navegación
options = webdriver.ChromeOptions()
# options.add_argument('--start-maximized') # maximizar ventana
options.add_argument('--disable-extensions') # deshabilitar extensiones
options.add_argument('--incognito') # activar modo incognito
# options.add_argument("--headless") # ejecutar sin interfaz grafica visible para ejecutar en segundo plano
options.add_argument("--disable-images") # desactivar imagenes
options.add_argument("--disable-notifications") # desactivar notificaciones

# url de la pagina a scrapear
url = 'https://eltiempo.es'

# iniciar driver
driver = webdriver.Chrome(options=options)
# iniciar el navegador
driver.get(url)
# maximizar ventana
driver.maximize_window()
# Esperar a que la pagina cargue
time.sleep(5)
# clickear en el boton de aceptar cookies
WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="redesignCmpWrapper"]/div[2]/div[1]/a'))).click()
time.sleep(5)
# ingresar texto en el buscador
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="term"]'))).send_keys('Madrid')
time.sleep(5)
# clickear en el buscador
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="search"]/div/div/div/ul/li[1]/a'))).click()
time.sleep(5)
# clickear en por horas
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="cityPoisTable"]/section/ul[1]/li[2]/h2/a'))).click()
time.sleep(5)
# tabla de horas (full xpath)
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[7]/div[1]/div[4]/div/main/section[3]/article/ul')))
time.sleep(5)
# scrapear tabla que contiene la informacion (full xpath)
texto_columnas = driver.find_element(By.XPATH, '/html/body/div[7]/div[1]/div[4]/div/main/section[3]/article/ul')
texto_columnas = texto_columnas.text
# seleccionar solo el dia de hoy
tiempo_hoy = texto_columnas.split('Mañana')[0].split('\n')[1:-1]

# almacenamiento de datos
horas = list()
temp = list()
v_viento = list()

# iterando atraves de la lista para guardar los datos
for i in range(0, len(tiempo_hoy), 5):
    horas.append(tiempo_hoy[i])
    temp.append(tiempo_hoy[i + 1])
    v_viento.append(tiempo_hoy[i + 4])

# creando dataframe
df = pd.DataFrame({'Horas': horas, 'Temperatura': temp, 'V_viento(km_h)': v_viento})
print(df)
df.to_csv('tiempo_hoy.csv', index=False)