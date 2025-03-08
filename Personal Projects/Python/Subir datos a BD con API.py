import requests
import pandas as pd
import json

# Crear un DataFrame de ejemplo
data = {
    "id": [1, 2, 3],
    "nombre": ["Juan", "Ana", "Pedro"],
    "edad": [30, 25, 40],
    "ciudad": ["Bogotá", "Medellín", "Cali"]
}
df = pd.DataFrame(data)

# 1Seleccionar las columnas que se quieren enviar
columnas_necesarias = ["id", "nombre", "edad"]  # Ajusta las columnas según necesites
df_filtrado = df[columnas_necesarias]

# Convertir a JSON para enviarlo a la API
datos_json = df_filtrado.to_json(orient="records")

# Configuración de la API
API_URL = "https://api.ejemplo.com/subir"
TOKEN = "tu_token_aqui"  # Reemplázalo con tu token real
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Enviar los datos a la API (Corrección aplicada)
response = requests.post(API_URL, headers=headers, json=json.loads(datos_json))

# Verificar la respuesta de la API
if response.status_code == 200:
    print("Datos subidos correctamente")
else:
    print(f"Error {response.status_code}: {response.text}")

# CODIGO PARA API QUE RECIBA MULTIPLES REGISTROS POR PETICION