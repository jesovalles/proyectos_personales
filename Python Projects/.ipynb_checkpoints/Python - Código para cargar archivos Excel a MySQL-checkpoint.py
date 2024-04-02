import os
import mysql.connector
import pandas as pd

# Conexión a la base de datos MySQL
conexion = mysql.connector.connect(host="localhost",user="root",password="password",database="database")

# Ruta del directorio a buscar
ruta = "ruta_local"

# Obtener la lista de archivos en el directorio
archivos = os.listdir(ruta)

# Crear una lista de nombres de archivos cargados en la columna FileName
cursor = conexion.cursor()
cursor.execute("SELECT FileName FROM fileloadstatus")

# Crear una variable que contendrá los nombres de los archivos de la columna FileName resultante de la consulta hecha
archivos_cargados = [fila[0] for fila in cursor.fetchall()]

# Recorrer los archivos en el directorio
for archivo in archivos:
    if archivo.startswith("OPC_Detalles_de_Tareas_Fecha_Creacion_Dia") and archivo not in archivos_cargados:
        
        # Leer el archivo con Pandas y quita las primeras 4 filas
        df = pd.read_excel(os.path.join(ruta, archivo), skiprows=4)

        # Renombrar la columna "Name" a "Nombre" si existe
        if "Name" in df.columns:
            df = df.rename(columns={"Name": "Nombre"})

        # Renombrar la columna "Age" a "Edad" si existe
        if "Age" in df.columns:
            df = df.rename(columns={"Age": "Edad"})

        # iterar por cada fila del DataFrame y agregarla a la tabla en MySQL
        for i, row in df.iterrows():
            Fecha_Creacion_Tareas = row['Fecha Creacion Tareas']
            Fecha_Cierra_Tarea = row['Fecha Cierra Tarea']
            IncidenteSolicitudCambios = row['IncidenteSolicitudCambios']
            ID_Tarea = row['ID Tarea']
            Estado = row['Estado']
            Empresa_Cliente = row['Empresa Cliente']
            Segmentacion_B2B = row['Segmentacion B2B']
            Prioridad = row['Prioridad']
            Tipo_de_Tarea = row['Tipo de Tarea']
            Remitente = row['Remitente']
            Nombre_Tarea = row['Nombre Tarea']
            Resumen = row['Resumen']
            Grupo_Asignado_Tarea = row['Grupo Asignado Tarea']
            Analista_Asignado = row['Analista Asignado']
    
            query = f"INSERT INTO tareas_creacion (`Fecha Creacion Tareas`, `Fecha Cierra Tarea`, `IncidenteSolicitudCambios`, `ID Tarea`, `Estado`, `Empresa Cliente`, `Segmentacion B2B`, `Prioridad`, `Tipo de Tarea`, `Remitente`, `Nombre Tarea`, `Resumen`, `Grupo Asignado Tarea`, `Analista Asignado`) VALUES ('{Fecha_Creacion_Tareas}', '{Fecha_Cierra_Tarea}', '{IncidenteSolicitudCambios}', '{ID_Tarea}', '{Estado}', '{Empresa_Cliente}', '{Segmentacion_B2B}', '{Prioridad}', '{Tipo_de_Tarea}', '{Remitente}', '{Nombre_Tarea}', '{Resumen}', '{Grupo_Asignado_Tarea}', '{Analista_Asignado}')"    
            cursor.execute(query)

            # Registrar el nombre del archivo en la columna FileName
        cursor.execute("INSERT INTO fileloadstatus (FileName) VALUES (%s)", (archivo,))
        print(f"Se cargó el archivo: {archivo}")

# Cerrar la conexión a la base de datos
conexion.commit()
cursor.close()
conexion.close()