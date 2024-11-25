import pickle

##### leer pickel sin encriptacion ##########
with open('C:\\Users\\jesus.ovalles\\Proyectos\\Credenciales\\Credenciales_user_5.pkl', 'rb') as archivo:
    datos = pickle.load(archivo)

# Extrae el valor del nombre de usuario
username = datos.get('user')

# Muestra el nombre de usuario
print(f"El nombre de usuario es: {username}")