import requests
import pandas as pd

# Crear un DataFrame de ejemplo
data = {
    "id": [1, 2, 3],
    "nombre": ["Juan", "Ana", "Pedro"],
    "edad": [30, 25, 40],
    "ciudad": ["Bogotá", "Medellín", "Cali"]
}
df = pd.DataFrame(data)

# Seleccionar las columnas que se quieren enviar
columnas_necesarias = ["id", "nombre", "edad"]  
df_filtrado = df[columnas_necesarias]

# Configuración de la API
API_URL = "https://api.ejemplo.com/subir"
TOKEN = "tu_token_aqui"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Enviar cada registro por separado
for _, fila in df_filtrado.iterrows():
    datos_json = fila.to_json()  # Convertir fila individual a JSON
    response = requests.post(API_URL, headers=headers, data=datos_json)  # Enviar petición

    # Verificar la respuesta de la API
    if response.status_code == 200:
        print(f"Registro {fila['id']} subido correctamente")
    else:
        print(f"Error al subir {fila['id']}: {response.status_code} - {response.text}")

# CODIGO PARA API QUE RECIBA UN REGISTRO POR PETICION