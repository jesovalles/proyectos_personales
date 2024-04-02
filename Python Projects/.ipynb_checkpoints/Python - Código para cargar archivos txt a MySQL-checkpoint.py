import os
import mysql.connector
import datetime as dt

# Conexión a la base de datos MySQL
conexion = mysql.connector.connect(host="localhost", user="root", password="password", database="database")

# Ruta del directorio a buscar
ruta = "ruta_local"

# Obtener la lista de archivos en el directorio
archivos = os.listdir(ruta)

# Crear una lista de nombres de archivos cargados en la columna FileName
cursor = conexion.cursor()
cursor.execute("SELECT FileName FROM fileloadstatus")
archivos_cargados = [fila[0] for fila in cursor.fetchall()]

# Recorrer los archivos en el directorio
for archivo in archivos:
    if archivo.startswith("Llamadas por analista y skill") and archivo not in archivos_cargados:
        
        # Leer el archivo de texto
        with open(os.path.join(ruta, archivo), 'r') as file:
            lines = file.readlines()[5:] # Omitir las cinco primeras filas
            
        # iterar por cada línea del archivo y agregarla a la tabla en MySQL
        for line in lines:
            line = line.strip()
            
            #Valida si la fila no está vaciq
            if line:
                # Separar los valores por tabulaciones (u otro delimitador si es necesario)
                values = line.split('\t')

                # Aquí debes ajustar el código para asignar los valores a las variables correspondientes
                fecha_str = values[0]
                Fecha = dt.datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%Y/%m/%d").replace("/", "-") #Cambio el formato 01-01-2023 por el formato 2023-01-01 que es el formato que recibe MySQL
                SplitSkill = values[1]
                Nombre_del_agente = values[3]
                Identif_de_conexión = values[4]
                Llamadas_ACD = values[5]
                Tiempo_prom_de_ACD = values[6]
                Tiempo_prom_de_ACW = values[7]
                Llamadas_de_entrada_a_la_extn = values[8]
                Tiempo_prom_de_entrada_a_la_extn = values[9]
                Llamadas_de_salida_de_la_extn = values[10]
                Tiempo_prom_de_salida_de_la_extn = values[11]
                Tiempo_ACD = values[12]
                Tiempo_ACW = values[13]
                Tiempo_de_llamado_del_agente = values[14]
                Otra_hora = values[15]
                Tiempo_AUX = values[16]
                Tiempo_dispon = values[17]
                Tiempo_con_personal = values[18]
                Trans_de_salida = values[19]
                Llamadas_retenidas = values[20]
                Tiempo_de_reten = values[21]
                HOLDABNCALLS = values[22]

                query = f"INSERT INTO llamadas_por_analista (`Fecha`, `Split/Skill`, `Nombre del agente`, `Identif. de conexión`, `Llamadas ACD`, `Tiempo prom. de ACD`, `Tiempo prom. de ACW`, `Llamadas de entrada a la extn`, `Tiempo prom. de entrada a la extn`, `Llamadas de salida de la extn`, `Tiempo prom. de salida de la extn`, `Tiempo ACD`, `Tiempo ACW`, `Tiempo de llamado del agente`, `Otra hora`, `Tiempo AUX`, `Tiempo dispon.`, `Tiempo con personal`, `Trans. de salida`, `Llamadas retenidas`, `Tiempo de reten.`, `HOLDABNCALLS`) VALUES ('{Fecha}', '{SplitSkill}', '{Nombre_del_agente}', '{Identif_de_conexión}', '{Llamadas_ACD}', '{Tiempo_prom_de_ACD}', '{Tiempo_prom_de_ACW}', '{Llamadas_de_entrada_a_la_extn}', '{Tiempo_prom_de_entrada_a_la_extn}', '{Llamadas_de_salida_de_la_extn}', '{Tiempo_prom_de_salida_de_la_extn}', '{Tiempo_ACD}', '{Tiempo_ACW}', '{Tiempo_de_llamado_del_agente}', '{Otra_hora}', '{Tiempo_AUX}', '{Tiempo_dispon}', '{Tiempo_con_personal}', '{Trans_de_salida}', '{Llamadas_retenidas}', '{Tiempo_de_reten}', '{HOLDABNCALLS}')"
                cursor.execute(query)

        # Registrar el nombre del archivo en la columna FileName
        cursor.execute("INSERT INTO fileloadstatus (FileName) VALUES (%s)", (archivo,))
        print(f"Se cargó el archivo: {archivo}")

# Cerrar la conexión a la base de datos
conexion.commit()
cursor.close()
conexion.close()