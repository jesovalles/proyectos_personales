import paramiko
import os
import datetime as dt

# Configuración de conexión SFTP
hostname = 'xx.xxx.xx.xx'
username = 'user'
password = 'password'
port = 2222

# Configuración de ruta remota y local
remote_path = 'ruta_ftp'
local_path = 'ruta_local'

# Obtiene la fecha actual en el formato requerido
date_str = dt.datetime.now().strftime('%m-%d-%Y')

# Conexión SFTP
transport = paramiko.Transport((hostname, port))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

# Descarga archivos de Excel con la fecha actual
for filename in sftp.listdir(remote_path):
    if filename.endswith('.xlsx') and date_str in filename:
        remote_file = os.path.join(remote_path, filename)
        local_file = os.path.join(local_path, filename)
        sftp.get(remote_file, local_file)
        print(f'Descargado: {filename}')

# Cierre de conexión SFTP
sftp.close()
transport.close()