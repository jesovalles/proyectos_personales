import os
import pickle
import requests
import pandas as pd
from io import BytesIO
from shareplum import Office365
from typing import Optional, Dict
from cryptography.fernet import Fernet

user = "bi.admin@inmel.co"
password = "tFC+Bqig.b47M"

# Clase para proteger credenciales
class ProtectedString:
    def __init__(self, value: str):
        self._value = value

    def __str__(self) -> str:
        return "********"

    def __repr__(self) -> str:
        return "********"
    
    def secure(self, caller_name: str) -> str:
        return self._value

# Clase para manipulación y carga de credenciales
class SecureCredentials:
    def __init__(self, base_path: Optional[str] = None, usuario: Optional[str] = None):
        self._credentials = None
        self._fernet = None
        self.usuario = usuario  # Almacena el usuario
        self.user = user
        self.password = password  # Stores the password
        self.rutas = self._obtener_rutas(base_path)
        self._cargar_credenciales()
   
    # Leer archivo en SharePoint
    def leer_archivo_sharepoint(self,user,password):
        """ Leer el archivo que contiene las credenciales"""
        config = {
            'sp_usuario': user,
            'sp_password': password,
            'sp_ruta_base': 'https://inmelingenieria.sharepoint.com',
            'sp_nombre_sitio': 'Analytics-0018-TICPrincipal',
            'sp_documentos_compartidos': 'Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred'
            }
        usuario = config['sp_usuario']
        password = config['sp_password']
        nombre_sitio = config['sp_nombre_sitio']
        ruta_base = config['sp_ruta_base']
        ruta_documentos = config['sp_documentos_compartidos']
        # Obtener cookie de autenticación
        authcookie = Office365(ruta_base, username=usuario, password=password).GetCookies()
        session = requests.Session()
        session.cookies = authcookie
        session.headers.update({'user-agent': 'python_bite/v1'})
        session.headers.update({'accept': 'application/json;odata=verbose'})
        # Obtener lista de archivos en la carpeta
        try:
            response = session.get(url=ruta_base + "/sites/" + nombre_sitio + "/_api/web/GetFolderByServerRelativeUrl('" + ruta_documentos + "')/Files")
            response.raise_for_status()
            archivos = response.json()
            enlace_completo = "Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred/"
            lista_ruta_archivos = [enlace_completo + info_archivos['Name'] for info_archivos in archivos['d']['results']]
            
            # Leer y mostrar cada imagen
            for archivo in lista_ruta_archivos:
                if 'Pswd' in archivo and archivo.lower().endswith('.xlsx'):
                    # Crear la ruta completa para leer archivo de Excel con pandas
                    archivo_url = f"{ruta_base}/sites/{nombre_sitio}/{archivo}"
                    archivo_response = session.get(archivo_url)
                    archivo_response.raise_for_status()
                    # Leer el contenido del archivo con pandas directamente desde la memoria
                    contenido_archivo = BytesIO(archivo_response.content)
                    df = pd.read_excel(contenido_archivo)
                    return df, enlace_completo         
        except Exception as e:
            print(f"Error al obtener la lista de archivos: {e}")
            return []
        
    # enviar archivo a sharepoint
    def subir_archivos(self, clave, nombre_archivo, user, password):
        """ Envia a SharePoint pickel y llave de cifrado"""
        config = dict()
        config['sp_user'] = user
        config['sp_password'] = password
        config['sp_base_path'] = 'https://inmelingenieria.sharepoint.com'
        config['sp_site_name'] = 'Analytics-0018-TICPrincipal'
        config['sp_doc_library'] = 'Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred/keys'
        # Obtener datos de configuracion
        username = config['sp_user']
        password = config['sp_password']
        site_name = config['sp_site_name']
        base_path = config['sp_base_path']
        doc_library = config['sp_doc_library']
        file_name = f'{nombre_archivo}'
        # Convertir DataFrame a bytes
        file_in_memory = BytesIO()
        # clave.to_pickle(file_in_memory, index=False)
        file_in_memory.seek(0)
        # Obtener cookie de autenticación
        authcookie = Office365(base_path, username=username, password=password).GetCookies()
        session = requests.Session()
        session.cookies = authcookie
        session.headers.update({'user-agent': 'python_bite/v1'})
        session.headers.update({'accept': 'application/json;odata=verbose'})
        # Recibo el X-RequestDigest de la primera llamada fallida
        session.headers.update({'X-RequestDigest': 'FormDigestValue'})
        response = session.post(url=base_path + "/sites/" + site_name + "/_api/web/GetFolderByServerRelativeUrl('" + doc_library + "')/Files/add(url='a.txt',overwrite=true)",data="")
        session.headers.update({'X-RequestDigest': response.headers['X-RequestDigest']})
        # Realizar la carga real
        try:
            response = session.post(
                url=base_path + "/sites/" + site_name + "/_api/web/GetFolderByServerRelativeUrl('" + doc_library + "')/Files/add(url='" 
                + file_name + "',overwrite=true)",
                data=clave)
            if response.status_code == 200:
                # print("CARGA EXITOSA EN SHAREPOINT")
                return
            else:
                print(f"No se pudo cargar el archivo. Código de estado: {response.status_code}")
                return
        except Exception as err:
            print("Se produjo algún error an cargar archivo: " + str(err))
            return 
        
    # Función para obtener las rutas de los archivos
    def _obtener_rutas(self, base_path: Optional[str]) -> dict:
        if base_path is None:
            base_path = os.path.expanduser("~")  # Usa el directorio home por defecto
        
        return {
            "ruta": base_path,
            "ruta_pickle": os.path.join(base_path, "Proyectos", "Credenciales", f"Credenciales_{self.usuario}.pkl"),
            "ruta_clave": os.path.join(base_path, "Proyectos", "Credenciales", f"key_{self.usuario}.key")
        }
    
    # Función para crear o leer la clave de cifrado
    def _manejar_clave(self) -> Optional[bytes]:
        try:
            if not self._verificar_llavecifrado(self.user, self.password):
                clave = Fernet.generate_key()
                with open(self.rutas["ruta_clave"], 'wb') as archivo_clave:
                    archivo_clave.write(clave)
                # Sube el archivo a SharePoint
                with open(self.rutas["ruta_clave"], 'rb') as archivo:
                    self.subir_archivos(archivo.read(), f"Credenciales_{self.usuario}.key", user, password)
                # Elimina el archivo después de subirlo
                os.remove(self.rutas["ruta_clave"])           
            else:
                # Leer llave en sharepoint
                config = {
                    'sp_usuario': self.user,
                    'sp_password': self.password,
                    'sp_ruta_base': 'https://inmelingenieria.sharepoint.com',
                    'sp_nombre_sitio': 'Analytics-0018-TICPrincipal',
                    'sp_documentos_compartidos': 'Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred/keys'
                }
                ruta_base = config['sp_ruta_base']
                nombre_sitio = config['sp_nombre_sitio']
                ruta_documentos = config['sp_documentos_compartidos']

                # Autenticación y creación de sesión
                authcookie = Office365(
                    ruta_base,
                    username=config['sp_usuario'],
                    password=config['sp_password']
                ).GetCookies()

                session = requests.Session()
                session.cookies = authcookie
                session.headers.update({'user-agent': 'python_bite/v1'})
                session.headers.update({'accept': 'application/json;odata=verbose'})

                archivo_nombre = f"Credenciales_{self.usuario}.key"
                archivo_url = f"{ruta_base}/sites/{nombre_sitio}/{ruta_documentos}/{archivo_nombre}"

                response = session.get(archivo_url)
                response.raise_for_status()
                # Retorna la clave directamente desde el contenido del archivo
                clave = response.content
                # print("Llave cargada desde SharePoint")
            return clave
        except Exception as e:
            print(f"Error al manejar la clave: {e}")
            return None
        
    # Función para cargar pickle
    def _cargar_credenciales(self) -> None:
        try:
            clave = self._manejar_clave()
            if clave is None:
                return

            self._fernet = Fernet(clave)

            if not self._verificar_pickel(self.user, self.password):
                # Si no existe el archivo pickle, crea las credenciales
                self._crear_credenciales()
            else:
                # Si existe el archivo pickle, lee las credenciales
                self._leer_credenciales()

        except Exception as e:
            print(f"Error al cargar credenciales: {e}")

    # Función para encriptar credenciales si no existen
    def _crear_credenciales(self) -> None:
        try:
            df = self.leer_archivo_sharepoint(user,password)[0]           
            # Filtra la fila correspondiente al usuario especificado
            user_row = df[df['User'] == self.usuario]
            if user_row.empty:
                raise ValueError(f"User '{self.usuario}' no encontrado en el archivo Excel.")
            # Obtiene las credenciales del usuario
            credenciales = {
                'Usuario': ProtectedString(user_row['User'].iloc[0]),
                'Contraseña': ProtectedString(user_row['Pswd'].iloc[0])
            }
            # Encripta las credenciales
            datos_encriptados = self._fernet.encrypt(pickle.dumps(credenciales))
            with open(self.rutas["ruta_pickle"], 'wb') as f:
                f.write(datos_encriptados)
            # Sube el archivo a SharePoint
            with open(self.rutas["ruta_pickle"], 'rb') as archivo:
                self.subir_archivos(archivo.read(), f"Credenciales_{self.usuario}.pkl", user, password)
            # Elimina el archivo después de subirlo
            os.remove(self.rutas["ruta_pickle"])

            self._credentials = credenciales
        except Exception as e:
            print(f"Error al crear credenciales: {e}")

    def _verificar_pickel(self, user, password):
        """Verifica si existe el archivo pickle en la carpeta 'keys' de SharePoint"""
        config = {
            'sp_usuario': user,
            'sp_password': password,
            'sp_ruta_base': 'https://inmelingenieria.sharepoint.com',
            'sp_nombre_sitio': 'Analytics-0018-TICPrincipal',
            'sp_documentos_compartidos': 'Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred/keys'
        }
        usuario = config['sp_usuario']
        password = config['sp_password']
        nombre_sitio = config['sp_nombre_sitio']
        ruta_base = config['sp_ruta_base']
        ruta_documentos = config['sp_documentos_compartidos']

        # Obtener cookie de autenticación
        authcookie = Office365(ruta_base, username=usuario, password=password).GetCookies()
        session = requests.Session()
        session.cookies = authcookie
        session.headers.update({'user-agent': 'python_bite/v1'})
        session.headers.update({'accept': 'application/json;odata=verbose'})

        # Obtener lista de archivos en la carpeta
        try:
            response = session.get(
                url=ruta_base + "/sites/" + nombre_sitio + "/_api/web/GetFolderByServerRelativeUrl('" + ruta_documentos + "')/Files"
            )
            response.raise_for_status()
            archivos = response.json()
            # obteniendo usuario para buscar su archivo
            df = self.leer_archivo_sharepoint(user,password)[0]
            # Filtra la fila correspondiente al usuario especificado
            user_row = df[df['User'] == self.usuario]
            archivo_nombre = f"Credenciales_{self.usuario}.pkl"
            # Verificar si existe un archivo pickle en la lista
            for archivo_info in archivos['d']['results']:
                if archivo_info['Name'].endswith('.pkl') and archivo_info['Name'] == archivo_nombre:
                    # print("El archivo pickle existe en SharePoint")
                    return True
            print("El archivo pickle no se encontró en SharePoint, se procede a crearlo y subirlo a sharepoint")
            return False
        except Exception as e:
            print(f"Error al obtener la lista de archivos: {e}")
            return False
    
    def _verificar_llavecifrado(self, user, password):
        """Verifica si existe el archivo pickle en la carpeta 'keys' de SharePoint"""
        config = {
            'sp_usuario': user,
            'sp_password': password,
            'sp_ruta_base': 'https://inmelingenieria.sharepoint.com',
            'sp_nombre_sitio': 'Analytics-0018-TICPrincipal',
            'sp_documentos_compartidos': 'Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred/keys'
        }
        usuario = config['sp_usuario']
        password = config['sp_password']
        nombre_sitio = config['sp_nombre_sitio']
        ruta_base = config['sp_ruta_base']
        ruta_documentos = config['sp_documentos_compartidos']

        # Obtener cookie de autenticación
        authcookie = Office365(ruta_base, username=usuario, password=password).GetCookies()
        session = requests.Session()
        session.cookies = authcookie
        session.headers.update({'user-agent': 'python_bite/v1'})
        session.headers.update({'accept': 'application/json;odata=verbose'})

        # Obtener lista de archivos en la carpeta
        try:
            response = session.get(
                url=ruta_base + "/sites/" + nombre_sitio + "/_api/web/GetFolderByServerRelativeUrl('" + ruta_documentos + "')/Files"
            )
            response.raise_for_status()
            archivos = response.json()
            # obteniendo usuario para buscar su archivo
            df = self.leer_archivo_sharepoint(user,password)[0]
            # Filtra la fila correspondiente al usuario especificado
            user_row = df[df['User'] == self.usuario]
            archivo_nombre = f"Credenciales_{self.usuario}.key"
            # Verificar si existe un archivo pickle en la lista
            for archivo_info in archivos['d']['results']:
                if archivo_info['Name'].endswith('.key') and archivo_info['Name'] == archivo_nombre:
                    # print("La llave de cifrado existe en SharePoint")
                    return True
            print("La llave de cifrado no se encontró en SharePoint, se procede a crearla y subirla a sharepoint")
            return False
        except Exception as e:
            print(f"Error al obtener la lista de archivos: {e}")
            return False
    
    # Función para desencriptar credenciales
    def _leer_credenciales(self) -> None:
        try:
            config = {
                'sp_usuario': self.user,
                'sp_password': self.password,
                'sp_ruta_base': 'https://inmelingenieria.sharepoint.com',
                'sp_nombre_sitio': 'Analytics-0018-TICPrincipal',
                'sp_documentos_compartidos': 'Documentos%20compartidos%2F0018%20%2D%20TIC%20Principal%2FCred/keys'
            }
            usuario = config['sp_usuario']
            password = config['sp_password']
            nombre_sitio = config['sp_nombre_sitio']
            ruta_base = config['sp_ruta_base']
            ruta_documentos = config['sp_documentos_compartidos']
            archivo_nombre = f"Credenciales_{self.usuario}.pkl"

            # Obtener cookie de autenticación
            authcookie = Office365(ruta_base, username=usuario, password=password).GetCookies()
            session = requests.Session()
            session.cookies = authcookie
            session.headers.update({'user-agent': 'python_bite/v1'})
            session.headers.update({'accept': 'application/json;odata=verbose'})

            # Obtener URL del archivo pickle
            archivo_url = f"{ruta_base}/sites/{nombre_sitio}/{ruta_documentos}/{archivo_nombre}"
            response = session.get(archivo_url)
            if response.status_code == 200:
                datos_encriptados = response.content  # Leer contenido en memoria

                # Desencriptar el contenido
                datos_desencriptados = self._fernet.decrypt(datos_encriptados)

                # Cargar el contenido desencriptado como un objeto Python
                self._credentials = pickle.loads(datos_desencriptados)
                # print("Credenciales cargadas exitosamente")
            else:
                print(f"No se pudo obtener el archivo. Código de estado: {response.status_code}")
                self._crear_credenciales()
        except Exception as e:
            print(f"Error al leer credenciales desde SharePoint: {e}")

    # Función para obtener credenciales
    def creds(self, caller_name: str) -> Optional[Dict[str, ProtectedString]]:
        if self._credentials is None:
            self._cargar_credenciales()

        if self._credentials:
            return {
                'usuario': self._credentials['Usuario'],
                'password': self._credentials['Contraseña']
            }
        return None