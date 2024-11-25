import requests
import pandas as pd
import json

# funcion para visualizar json
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# URL conexion
response = requests.get("http://api.open-notify.org/astros")

# visualizando json
jprint(response.json())

# verificacion y conexion
if response.status_code == 200:
    # obteniendo el contenido del JSON
    data = response.json()  
    # convirtiendo a df
    df = pd.DataFrame(data)
    # expandiendo la columna 'people' usando json_normalize
    df = pd.json_normalize(df['people'])
    # combinando el df expandido con las columnas restantes
    df_final = pd.concat([df, df.drop(columns=['people'])], axis=1)
    print(df_final)
else:
    print("Error en la solicitud:", response.status_code)