import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {
    'x-apisports-key': API_KEY  # ← HEADER CORRECTO según documentación
}

print(' PROBANDO CON HEADER CORRECTO')
print('=' * 60)

# 1. Verificar estado de la cuenta
url = "https://v3.football.api-sports.io/status"
try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f' Status Code: {response.status_code}')
    print(f' Respuesta completa: {response.json()}')
    
    # Verificar si hay error en la respuesta
    data = response.json()
    if 'errors' in data and data['errors']:
        print(f' Error en API: {data["errors"]}')
    else:
        print(' API conectada correctamente')
        print(f'   Cuenta: {data["response"]["account"]["email"]}')
        print(f'   Plan: {data["response"]["subscription"]["plan"]}')
        print(f'   Requests: {data["response"]["requests"]["current"]}/{data["response"]["requests"]["limit_day"]}')
        
except Exception as e:
    print(f' Error de conexión: {e}')  #  CORREGIDO: comilla cerrada

# 2. Buscar ligas de México
print('\n BUSCANDO LIGAS EN MÉXICO:')
url = "https://v3.football.api-sports.io/leagues"
params = {"country": "Mexico"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        ligas = data.get('response', [])
        print(f' Encontradas {len(ligas)} ligas:')
        for liga in ligas:
            print(f'    {liga["league"]["name"]} (ID: {liga["league"]["id"]})')
    else:
        print(f' Error HTTP: {response.status_code}')
        print(f'   Detalle: {response.json()}')
except Exception as e:
    print(f' Error: {e}')  #  CORREGIDO: comilla cerrada
