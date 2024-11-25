import pickle

##### leer pickel sin encriptacion ##########
with open('C:\\Users\\jesus.ovalles\\Proyectos\\Credenciales\\Credenciales_pickle.pkl', 'rb') as archivo:
    datos = pickle.load(archivo)

# Extrae el valor del nombre de usuario
username = datos.get('username')

# Muestra el nombre de usuario
print(f"El nombre de usuario es: {username}")