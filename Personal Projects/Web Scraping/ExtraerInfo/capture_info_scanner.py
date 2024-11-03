import os
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re

# Inicializando EasyOCR en español
lector = easyocr.Reader(['es'], gpu=False)

# Función para extraer texto usando EasyOCR con PyMuPDF
def extraer_texto_easyocr(pdf_path):
    try:
        # Abrir el documento pdf
        documento = fitz.open(pdf_path)
        texto_completo = ""
        
        # Itera sobre cada página
        for pagina_num, pagina in enumerate(documento, start=1):
            # Renderiza la página como una imagen de alta resolución
            pix = pagina.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # Convierte la imagen a un formato compatible con EasyOCR (array de numpy)
            img_np = np.array(img)
            # Realiza OCR en la imagen usando EasyOCR
            resultado = lector.readtext(img_np, detail=0)  # detail=0 solo devuelve el texto
            # Une el texto extraído
            texto_completo += "\n".join(resultado) + "\n"
        
        documento.close()
        return texto_completo
    except Exception as e:
        return ""

# Función para extraer datos del texto
def extraer_datos(texto_completo):
    match_factura = re.search(r'Factura:\s*(\d+)', texto_completo, re.IGNORECASE)
    numero_factura = match_factura.group(1) if match_factura else None

    match_fecha = re.search(r'Fecha:\s*([\d/]+)', texto_completo, re.IGNORECASE)
    fecha = match_fecha.group(1) if match_fecha else None

    match_total = re.search(r'Total:\s*\$?([\d,]+\.\d{2})', texto_completo, re.IGNORECASE)
    total = float(match_total.group(1).replace(',', '')) if match_total else None

    match_cliente = re.search(r'Cliente:\s*([A-Za-z\s]+)', texto_completo, re.IGNORECASE)
    cliente = match_cliente.group(1).strip() if match_cliente else None

    return {
        'Número de Factura': str(numero_factura) if numero_factura else None,
        'Fecha': fecha,
        'Total': total,
        'Cliente': cliente
    }

# Ruta de los archivos
ruta = 'C:\\Users\\jesus.ovalles\\Proyectos\\ExtraerInfo\\Facturación'

# Log archivos cargados
archivo_registro = 'pdfs_procesados.txt'

# Carga lista de archivos procesados
if os.path.exists(archivo_registro):
    with open(archivo_registro, 'r') as f:
        pdfs_procesados = set(f.read().splitlines())
else:
    pdfs_procesados = set()

# Lista para almacenar los datos extraídos
datos_facturas = []

# Iterando sobre los archivos para extraer los datos
nuevos_archivos = [archivo for archivo in os.listdir(ruta) 
                   if archivo.lower().endswith('.pdf') and archivo not in pdfs_procesados]

if not nuevos_archivos:
    exit()  # No hay nuevos archivos, salir sin hacer nada

for archivo in nuevos_archivos:
    ruta_pdf = os.path.join(ruta, archivo)
    
    # Extraer texto usando EasyOCR
    texto = extraer_texto_easyocr(ruta_pdf)
    
    if texto:
        datos = extraer_datos(texto)
        datos_facturas.append(datos)

        # Agregar archivo al registro de procesados
        pdfs_procesados.add(archivo)
        with open(archivo_registro, 'a') as f:
            f.write(archivo + '\n')
    
    print(f"Se cargo el archivo: {archivo}")

# Crear DataFrame con la data extraída
df_nuevos_datos = pd.DataFrame(datos_facturas)

# Convertir las fechas de los nuevos datos al formato 'dd/mm/yyyy'
if not df_nuevos_datos.empty:
    df_nuevos_datos['Fecha'] = pd.to_datetime(df_nuevos_datos['Fecha'], format='%d/%m/%Y', errors='coerce').dt.strftime('%d/%m/%Y')

# Guardando datos en Excel
if not df_nuevos_datos.empty:  # Solo guardar si hay datos nuevos
    # Intentar leer el archivo existente si existe
    if os.path.exists('facturas_extraidas.xlsx'):
        df_existente = pd.read_excel('facturas_extraidas.xlsx', dtype={'Número de Factura': str, 'Total': float, 'Cliente': str})
        df_existente['Fecha'] = pd.to_datetime(df_existente['Fecha'], format='%d/%m/%Y', errors='coerce').dt.strftime('%d/%m/%Y')
        df_consolidado = pd.concat([df_existente, df_nuevos_datos], ignore_index=True)
    else:
        df_consolidado = df_nuevos_datos

    # Guardar el DataFrame consolidado en el archivo Excel
    df_consolidado.to_excel('facturas_extraidas.xlsx', index=False)
