# librerias
import time
from time import sleep
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
url = 'https://www.amazon.in'

# iniciar driver
driver = webdriver.Chrome(options=options)
driver.get(url)
# maximizar ventana
driver.maximize_window()
# esperar a que la pagina cargue
time.sleep(5)

# esperar a que los elementos se carguen en la página
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="twotabsearchtextbox"]')))
except Exception as e:
    print(f"No se pudo cargar la página correctamente: {e}")
    driver.quit()
    exit()

# ingresar texto en el buscador
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="twotabsearchtextbox"]'))).send_keys('Smartphones under 10000')
time.sleep(3)
# clickear en el buscador
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="nav-search-submit-button"]'))).click()
time.sleep(3)

# almacenamiento de productos
products = []

# recorriendo y scrapeando pagina por pagina
for i in range(10): # iterando por las primeras 10 paginas
    print('Scraping page', i+1)
    product = driver.find_elements(By.XPATH, '//span[@class="a-size-medium a-color-base a-text-normal"]')
    for p in product:
        products.append(p.text)
    next_button = driver.find_element(By.XPATH, '//a[text()="Next"]')
    next_button.click()
    time.sleep(5)

# cierra el navegador
driver.quit()

# crea un DataFrame con los datos
df = pd.DataFrame({'Productos': products})

# guarda el DataFrame en un archivo CSV con codificación UTF-8
df.to_csv('Amazon products.csv', index=False, encoding='utf-8')

print("Datos guardados en Amazon products.csv")