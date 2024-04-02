import os
import pandas as pd

# Ruta donde se buscaran los archivos
ruta = "ruta"

# Lista que contiene los archivos de la ruta
lista_archivos = os.listdir(ruta)

# Ruta donde se guardara el archivo excel
ruta_destino = "ruta_destino\\consolidado de tareas cierre.xlsx"

# Crea el df que consolidara la data
df_consolidado = []

# Recorrer los archivos en el directorio
for archivo in lista_archivos:
    if archivo.startswith("OPC_Detalles_de_Tareas_Cerrado_Dia"):
        
        # Leer el archivo con Pandas y quitar las primeras 4 filas
        df = pd.read_excel(os.path.join(ruta, archivo), skiprows=4)

        # Renombrar la columna "Incidente/Solicitud/Cambios" a "IncidenteSolicitudCambios" si existe
        if "Incidente/Solicitud/Cambios" in df.columns:
            df = df.rename(columns={"Incidente/Solicitud/Cambios": "IncidenteSolicitudCambios"})
            
        # Se anexa la data al df_consolidado
        df_consolidado.append(df)
        
        print(f"Se cargó el archivo: {archivo}")
        
# Consolidar los dataframes en uno solo
df_final = pd.concat(df_consolidado, ignore_index=True)

# Guardar el dataframe consolidado en un archivo Excel
df_final.to_excel(ruta_destino, index=False)