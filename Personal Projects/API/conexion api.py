import requests
 
# Definir el endpoint, token y parámetros
url = "https://apiconta.contanet.com.pe/desarrollo/v1/Trazabilidad/SolicitudRequerimiento"  # Cambia esta URL por tu endpoint
bearer_token = "KtAv5YAR0D3ggGgnSte5sVeH2lwO9Q3XVw4PGM/ias1J+fkRfnqku44bAfGcKmiajIpWQgFeR4UunEjNIxGlUQ=="  # Cambia por tu Bearer Token
params = {
    "FechaDesde": "2024-01-01",  # Cambia los parámetros según sea necesario
    "FechaHasta": "2024-10-10"
}
 
# Configurar los encabezados con el token de autenticación
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}
 
# Realizar la solicitud GET o POST
response = requests.get(url, headers=headers, params=params)  # Usar 'post' si es necesario
 
# Verificar el resultado de la solicitud
if response.status_code == 200:
    print("Solicitud exitosa!")
    print(response.json())  # Mostrar la respuesta en formato JSON
else:
    print(f"Error en la solicitud: {response.status_code}")
    print(response.text)