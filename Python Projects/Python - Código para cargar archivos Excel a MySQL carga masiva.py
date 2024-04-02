import os
import mysql.connector
import pandas as pd
import numpy as np

# Conexión a la base de datos MySQL
conexion = mysql.connector.connect(host="localhost", user="root", password="password", database="database")

# Crea una lista de los nombres de los archivos que ya están cargados y están en la columna FileName
cursor = conexion.cursor()
cursor.execute("SELECT FileName FROM fileloadstatus")
archivos_cargados = [fila[0] for fila in cursor.fetchall()]

# Ruta de los archivos a cargar
ruta = "ruta_local"

# Recorre todos los archivos en la ruta principal y en las subcarpetas
for raiz, subcarpeta, archivos in os.walk(ruta):
    for archivo in archivos:
        # Verifica si el archivo cumple las condiciones y no está en la lista de archivos cargados
        if archivo.startswith(("OPC_Detalles_de_Tareas_Cerrado_Dia", "OPC_Detalles_de_Tareas_Fecha_Cierre_Dia")) and archivo not in archivos_cargados:
            # Obtiene la ruta completa del archivo
            archivo_ruta = os.path.join(raiz, archivo)
            
            # Lee el archivo con Pandas y quita las primeras 4 filas
            df = pd.read_excel(archivo_ruta, skiprows=4)
            
            # Reemplazar los valores NaN por None en el DataFrame
            df = df.replace({np.nan: None})
    
            # Renombrar la columna "Incidente/Solicitud/Cambios" a "IncidenteSolicitudCambios" si existe
            if "IncidenteSolicitudCambios" in df.columns:
                df = df.rename(columns={"IncidenteSolicitudCambios": "Incidente/Solicitud/Cambios"})
                
            # Reemplazar "\" por "\\" en la columna "Notas"
            df["Notas"] = df["Notas"].str.replace("\\", "\\\\", regex=False)
            df["Notas"] = df["Notas"].str.replace("'", "")
            
            # Convierte el DataFrame (df) en una lista de Python (df_lista) para luego usarlo en el executemany
            df_lista = df.values.tolist()
            
            # Inserta los datos en la tabla tareas_cierre
            cursor.executemany(
                "INSERT INTO tareas_cierre VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", df_lista)
    
            # Registrar el nombre del archivo en la columna FileName
            cursor.execute("INSERT INTO fileloadstatus (FileName) VALUES (%s)", (archivo,))
            print(f"Se cargó el archivo: {archivo_ruta}")

# Cerrar la conexión a la base de datos
conexion.commit()
cursor.close()
conexion.close()