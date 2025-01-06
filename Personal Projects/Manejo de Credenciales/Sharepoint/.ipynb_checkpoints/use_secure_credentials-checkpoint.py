from modificado_secure_credentials import SecureCredentials

# crea una instancia de SecureCredentials pasando el usuario
inst = SecureCredentials(base_path=None, usuario="user_5")
# obteniendo las credenciales
check = inst.creds(caller_name="main")['password']
    
print(f"Impresión convencional: {check}")  
print(f'Impresión con class: {check.secure("main")}')