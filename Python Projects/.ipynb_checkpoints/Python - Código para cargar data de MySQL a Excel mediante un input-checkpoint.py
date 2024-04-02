import pandas as pd
import mysql.connector

# Ingrese Segmentacion B2B y Prioridad
segmentacion = input("Ingrese la segmentación: ")

prioridad = input("Ingrese la prioridad: ")

parametros = (segmentacion, prioridad)

# Conexión a la base de datos MySQL
conexion = mysql.connector.connect(host="localhost", user="root", password="password", database="database")

# Ejecución de la consulta SQL
df_sql = pd.read_sql("""SELECT * FROM tareas_cierre
                        WHERE `Segmentacion B2B` = '"""+segmentacion+"' AND Prioridad = '"""+prioridad+"' """, conexion)

# Cerrar la conexión a la base de datos MySQL
conexion.close()

# Guardar la consulta en un DataFrame
df = pd.DataFrame(df_sql)

df.to_excel("ruta_local\\Data_de_prueba.xlsx", engine='openpyxl', index=False)

print("Dataframe guardado en Excel correctamente.")