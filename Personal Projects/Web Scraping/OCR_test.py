# librerías
import random
from time import sleep
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytesseract
from PIL import Image
import mss

# configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# opciones de navegación
options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')  # Deshabilitar extensiones
options.add_argument('--incognito')  # Activar modo incógnito
options.add_argument("--disable-images")  # Desactivar imágenes
options.add_argument("--disable-notifications")  # Desactivar notificaciones

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

# capturar region específica de la pantalla
with mss.mss() as sct:
    # definiendo las coordenadas de la region
    region = {'top': 750, 'left': 155, 'width': 400, 'height': 50}
    screenshot = sct.grab(region)
    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

    # guardar la imagen (para verificación)
    # img.save("screenshot.png")

    # extraer texto de la region
    texto_capturado = pytesseract.image_to_string(img)

print(f"Texto encontrado: {texto_capturado}")
# cerrar el driver
driver.quit()


# import pyautogui
# # obtiene la posición actual del mouse
# time.sleep(3)
# x, y = pyautogui.position()
# print(f"Posición actual del mouse: x={x}, y={y}")