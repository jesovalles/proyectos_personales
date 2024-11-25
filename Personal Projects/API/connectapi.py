import requests
import pandas as pd

# URL conexion
url = 'https://data.gov.ie/api/3/action/package_search?q=homelessness&rows=100'
data = requests.get(url).json()['result']

# obteniendo informacion
df = pd.json_normalize(data['results'], 'resources', 'title')

# filtrando informacion
df_filter = df['title'].str.startswith('Homelessness Report') & df['format'].eq('CSV')
df = df.loc[df_filter, ['title', 'url']]

# descargando data
data = {}
for idx, row in df.iterrows():
    dt = pd.to_datetime(row.title.strip('Homelessness Report '))
    data[dt] = pd.read_csv(row.url)

# anexando los datos
df_final = (pd.concat(data, axis=0).droplevel(1).rename_axis('Date').sort_index().reset_index())
df_final.to_excel('Homelessness Report.xlsx', index=False)