import requests
import pandas as pd

# Configuración de la API
API_URL = "https://api.ejemplo.com/data"
TOKEN_URL = "https://api.ejemplo.com/auth"
CLIENT_ID = "tu_cliente_id"
CLIENT_SECRET = "tu_cliente_secreto"

# Obtener token de autenticación
response = requests.post(TOKEN_URL, data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
token = response.json().get("access_token")

# Verificar si se obtuvo el token
if not token:
    raise Exception("Error al obtener el token de autenticación")

# Configurar encabezados con el token
headers = {"Authorization": f"Bearer {token}"}

# Hacer la solicitud a la API
response = requests.get(API_URL, headers=headers)
data = response.json()

# Convertir los datos a un DataFrame
df = pd.DataFrame(data)

# Mostrar las primeras filas del DataFrame
print(df.head())






