from secure_credentials import SecureCredentials

# crea una instancia de SecureCredentials pasando el usuario
inst = SecureCredentials(base_path=None, usuario="Jesus Ovalles")
# obteniendo las credenciales
check = inst.creds(caller_name="main")['password']
    
print(check)  
print(check.secure("main"))