# test_api_con_pais.py
import requests
import streamlit as st

print(' PROBANDO API-FOOTBALL CON DIFERENTES PARÁMETROS')
print('=' * 70)

API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# 1. Verificar qué ligas hay disponibles
print('\n 1. BUSCANDO LIGAS DE MÉXICO:')
url = "https://v3.football.api-sports.io/leagues"
params = {"country": "Mexico"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        ligas = data.get('response', [])
        print(f'    Encontradas {len(ligas)} ligas en México:')
        for liga in ligas:
            print(f'       {liga["league"]["name"]} (ID: {liga["league"]["id"]})')
    else:
        print(f'    Error {response.status_code}')
except Exception as e:
    print(f'    Error: {e}')

# 2. Probar búsqueda por ID de liga
print('\n 2. BUSCANDO EQUIPOS DE LIGA MX (ID 262):')
url = "https://v3.football.api-sports.io/teams"
params = {"league": 262, "season": 2024}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('response', [])
        print(f'    Encontrados {len(equipos)} equipos en Liga MX 2024:')
        for eq in equipos[:5]:  # Mostrar primeros 5
            team = eq['team']
            print(f'       {team["name"]} (ID: {team["id"]})')
    else:
        print(f'    Error {response.status_code}')
except Exception as e:
    print(f'    Error: {e}')

# 3. Probar búsqueda por nombre con acentos
print('\n 3. PROBANDO CON ACENTOS:')
nombres_con_acentos = [
    'América',
    'Tigres UANL',
    'Guadalajara',
    'Cruz Azul'
]

for nombre in nombres_con_acentos:
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": nombre}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                team = data['response'][0]['team']
                print(f'    {nombre}: {team["name"]} (ID: {team["id"]})')
            else:
                print(f'    {nombre}: No encontrado')
    except Exception as e:
        print(f'    Error con {nombre}: {e}')  #  CORREGIDO

print('\n' + '=' * 70)
