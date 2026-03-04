# test_api_football_directo.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
URL = 'https://v3.football.api-sports.io/status'

headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

print(' VERIFICANDO ESTADO DE API-FOOTBALL')
print('=' * 60)

try:
    response = requests.get(URL, headers=headers, timeout=5)
    print(f' Status Code: {response.status_code}')
    print(f' Respuesta: {response.text[:500]}')
    
    if response.status_code == 200:
        print(' API funcionando correctamente')
    elif response.status_code == 403:
        print(' Acceso denegado - Cuenta suspendida')
        print('\n POSIBLES SOLUCIONES:')
        print('   1. Ve a https://dashboard.api-football.com')
        print('   2. Inicia sesión con tu cuenta')
        print('   3. Verifica el estado de tu suscripción')
        print('   4. Si está suspendida, contacta soporte o crea una cuenta nueva')
    else:
        print(f' Error {response.status_code}')
        
except Exception as e:
    print(f' Error de conexión: {e}')
