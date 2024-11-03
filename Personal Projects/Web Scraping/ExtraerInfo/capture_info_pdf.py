import os
import pdfplumber
import pandas as pd
import re
from datetime import datetime

# Función para extraer datos
def extraer_datos(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"
        
        # Extraer número de factura
        match_factura = re.search(r'Factura:\s*(\d+)', texto_completo, re.IGNORECASE) # busca: Factura: 12345
        numero_factura = match_factura.group(1) if match_factura else None

        # Extraer fecha
        match_fecha = re.search(r'Fecha:\s*([\d/]+)', texto_completo, re.IGNORECASE) # busca: Fecha: 04/10/2023
        fecha = match_fecha.group(1) if match_fecha else None

        # Extraer total
        match_total = re.search(r'Total:\s*\$?([\d,]+\.\d{2})', texto_completo, re.IGNORECASE) # busca: Total: 1234.56
        total = float(match_total.group(1).replace(',', '')) if match_total else None

        # Extraer nombre del cliente
        match_cliente = re.search(r'Cliente:\s*([A-Za-z\s]+)', texto_completo, re.IGNORECASE) # busca: Cliente: Juan Pérez
        cliente = match_cliente.group(1).strip() if match_cliente else None

        return {
            'Número de Factura': str(numero_factura),  # Convierte a string
            'Fecha': fecha,
            'Total': total,
            'Cliente': cliente
        }

# Ruta de los archivos
ruta = 'C:\\Users\\jesus.ovalles\\Proyectos\\ExtraerInfo\\Facturación'

# Archivo de registro de PDFs procesados
archivo_registro = 'pdfs_procesados.txt'

# Cargar lista de archivos procesados
if os.path.exists(archivo_registro):
    with open(archivo_registro, 'r') as f:
        pdfs_procesados = set(f.read().splitlines())
else:
    pdfs_procesados = set()

# Lista para almacenar los datos extraídos
datos_facturas = []

# Iterando sobre los archivos para extraer los datos
for archivo in os.listdir(ruta):
    if archivo.lower().endswith('.pdf') and archivo not in pdfs_procesados:
        ruta_pdf = os.path.join(ruta, archivo)
        datos = extraer_datos(ruta_pdf)
        datos_facturas.append(datos)

        # Agregar archivo al registro de procesados
        pdfs_procesados.add(archivo)
        with open(archivo_registro, 'a') as f:
            f.write(archivo + '\n')

# Crear DataFrame con la data consolidada
df_nuevos_datos = pd.DataFrame(datos_facturas)

# Convertir las fechas de los nuevos datos al formato 'dd/mm/yyyy'
if not df_nuevos_datos.empty:
    df_nuevos_datos['Fecha'] = pd.to_datetime(df_nuevos_datos['Fecha'], format='%d/%m/%Y', errors='coerce').dt.strftime('%d/%m/%Y')

# Guardando datos en Excel
if not df_nuevos_datos.empty:  # Solo guardar si hay datos nuevos
    # Intentar leer el archivo existente si existe
    if os.path.exists('facturas_extraidas.xlsx'):
        df_existente = pd.read_excel('facturas_extraidas.xlsx', dtype={'Número de Factura': str, 'Total': float, 'Cliente': str})
        
        # Asegurarse de que las fechas existan como texto en formato 'dd/mm/yyyy'
        df_existente['Fecha'] = pd.to_datetime(df_existente['Fecha'], format='%d/%m/%Y', errors='coerce').dt.strftime('%d/%m/%Y')
        
        # Concatenar los nuevos datos con los existentes
        df_consolidado = pd.concat([df_existente, df_nuevos_datos], ignore_index=True)
    else:
        df_consolidado = df_nuevos_datos

    # Guardar el DataFrame consolidado en el archivo Excel
    df_consolidado.to_excel('facturas_extraidas.xlsx', index=False)