import pandas as pd
import requests

# Hacer la solicitud a la API en formato json
response = requests.get("https://www.datos.gov.co/resource/7cci-nqqb.json").json()

# Creación de Dataframe a partir del formato json
df = pd.DataFrame(response)
df.head()