import os
import pickle
import pandas as pd
from cryptography.fernet import Fernet
from typing import Optional, Dict

# Clase para proteger credenciales
class ProtectedString:
    def __init__(self, value: str):
        self._value = value

    def __str__(self) -> str:
        return "********"

    def __repr__(self) -> str:
        return "********"
    
    def secure(self, caller_name: str) -> str:
        # Registrar el intento de acceso (puedes descomentar la línea de registro si lo deseas)
        # self._log_access_attempt(caller_name)
        return self._value

    # def _log_access_attempt(self, caller_name: str) -> None:
    #     # Implementa el logging aquí si es necesario
    #     # print(f"Acceso a credencial por parte de: {caller_name}")
    #     pass

# Clase para manipulación y carga de credenciales
class SecureCredentials:
    def __init__(self, base_path: Optional[str] = None, usuario: Optional[str] = None):
        self._credentials = None
        self._fernet = None
        self.usuario = usuario  # Almacena el usuario
        self.rutas = self._obtener_rutas(base_path)
        self._cargar_credenciales()

    # Función para obtener las rutas de los archivos
    def _obtener_rutas(self, base_path: Optional[str]) -> dict:
        if base_path is None:
            base_path = os.path.expanduser("~")  # Usa el directorio home por defecto
        return {
            "ruta": base_path,
            "ruta_excel": os.path.join(base_path, "Proyectos", "Credenciales", "Credenciales.xlsx"),
            "ruta_pickle": os.path.join(base_path, "Proyectos", "Credenciales", f"Credenciales_{self.usuario}.pkl"),
            "ruta_clave": os.path.join(base_path, "Proyectos", "Credenciales", f"key_{self.usuario}.key")
        }
        
    # Función para crear o leer la clave de cifrado
    def _manejar_clave(self) -> Optional[bytes]:
        try:
            if not os.path.isfile(self.rutas["ruta_clave"]):
                clave = Fernet.generate_key()
                with open(self.rutas["ruta_clave"], 'wb') as archivo_clave:
                    archivo_clave.write(clave)
                # print(f"Clave generada y guardada para el usuario '{self.usuario}'.")
            else:
                with open(self.rutas["ruta_clave"], 'rb') as archivo_clave:
                    clave = archivo_clave.read()
                # print(f"Clave cargada desde el archivo para el usuario '{self.usuario}'.")
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

            if not os.path.isfile(self.rutas["ruta_pickle"]):
                # Si no existe el archivo pickle, crea las credenciales
                # print(f"Archivo pickle no encontrado para el usuario '{self.usuario}'. Creando credenciales desde Excel.")
                self._crear_credenciales()
            else:
                # Si existe el archivo pickle, lee las credenciales
                # print(f"Archivo pickle encontrado para el usuario '{self.usuario}'. Leyendo credenciales.")
                self._leer_credenciales()

        except Exception as e:
            print(f"Error al cargar credenciales: {e}")

    # Función para encriptar credenciales si no existen
    def _crear_credenciales(self) -> None:
        try:
            df = pd.read_excel(self.rutas["ruta_excel"])
            # Filtra la fila correspondiente al usuario especificado
            user_row = df[df['Usuario'] == self.usuario]
            if user_row.empty:
                raise ValueError(f"Usuario '{self.usuario}' no encontrado en el archivo Excel.")

            # Obtiene las credenciales del usuario
            credenciales = {
                'Usuario': ProtectedString(user_row['Usuario'].iloc[0]),
                'Contraseña': ProtectedString(user_row['Contraseña'].iloc[0])
            }

            # Encripta las credenciales
            datos_encriptados = self._fernet.encrypt(pickle.dumps(credenciales))
            with open(self.rutas["ruta_pickle"], 'wb') as f:
                f.write(datos_encriptados)
            
            self._credentials = credenciales
            # print(f"Credenciales para el usuario '{self.usuario}' creadas y encriptadas correctamente.")
        except Exception as e:
            print(f"Error al crear credenciales: {e}")

    # Función para desencriptar credenciales
    def _leer_credenciales(self) -> None:
        try:
            if not os.path.isfile(self.rutas["ruta_pickle"]):
                # Si no existe el archivo pickle, crea las credenciales
                self._crear_credenciales()
                return

            with open(self.rutas["ruta_pickle"], 'rb') as archivo:
                datos_encriptados = archivo.read()
            self._credentials = pickle.loads(self._fernet.decrypt(datos_encriptados))

            # Verifica que las credenciales correspondan al usuario solicitado
            if self._credentials['Usuario'].secure("internal") != self.usuario:
                raise ValueError("Las credenciales almacenadas no corresponden al usuario solicitado.")
            
            # print(f"Credenciales para el usuario '{self.usuario}' desencriptadas correctamente.")
        except Exception as e:
            print(f"Error al leer credenciales: {e}")

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
