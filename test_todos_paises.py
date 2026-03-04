# test_todos_paises.py
import requests
import streamlit as st
import time

print(' DIAGNÓSTICO COMPLETO DE API-FOOTBALL')
print('=' * 70)

API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# 1. VERIFICAR ESTADO DE LA CUENTA
print('\n 1. VERIFICANDO ESTADO DE LA API:')
url = "https://v3.football.api-sports.io/status"
try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f'   Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Respuesta: {data}')
        if data.get('response', {}).get('account'):
            print(f'    Cuenta activa: {data["response"]["account"]["email"]}')
        else:
            print('     Cuenta no activa o suspendida')
    else:
        print(f'    Error: {response.status_code}')
except Exception as e:
    print(f'    Error: {e}')

# 2. VERIFICAR PAÍSES DISPONIBLES
print('\n 2. VERIFICANDO PAÍSES DISPONIBLES:')
url = "https://v3.football.api-sports.io/countries"
try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        paises = data.get('response', [])
        print(f'    Total países: {len(paises)}')
        
        # Buscar México
        mexico = next((p for p in paises if p['name'].lower() == 'mexico'), None)
        if mexico:
            print(f'    México encontrado: {mexico}')
        else:
            print('    México NO está en la lista de países')
            
        # Mostrar primeros 10 países como muestra
        print('\n   Primeros 10 países:')
        for p in paises[:10]:
            print(f'       {p["name"]} (código: {p.get("code", "N/A")})')
    else:
        print(f'    Error: {response.status_code}')
except Exception as e:
    print(f'    Error: {e}')

# 3. VERIFICAR LIGAS POR PAÍS (MÉXICO)
print('\n 3. BUSCANDO LIGAS EN MÉXICO:')
url = "https://v3.football.api-sports.io/leagues"

for country_name in ['Mexico', 'México']:
    params = {"country": country_name}
    try:
        print(f'\n   Probando con país: "{country_name}"')
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            ligas = data.get('response', [])
            print(f'      Ligas encontradas: {len(ligas)}')
            for liga in ligas[:3]:  # Mostrar primeras 3
                print(f'          {liga["league"]["name"]} (ID: {liga["league"]["id"]})')
        else:
            print(f'      Error: {response.status_code}')
    except Exception as e:
        print(f'      Error: {e}')
    time.sleep(1)  # Pequeña pausa entre requests

# 4. VERIFICAR EQUIPOS POR PAÍS
print('\n 4. BUSCANDO EQUIPOS EN MÉXICO:')
url = "https://v3.football.api-sports.io/teams"
params = {"country": "Mexico"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('response', [])
        print(f'   Equipos encontrados: {len(equipos)}')
        
        if len(equipos) > 0:
            print('\n   Equipos:')
            for eq in equipos[:10]:
                team = eq['team']
                print(f'       {team["name"]} (ID: {team["id"]})')
        else:
            print('     No se encontraron equipos')
    else:
        print(f'   Error: {response.status_code}')
except Exception as e:
    print(f'   Error: {e}')

# 5. SOLUCIÓN: PROBAR CON LIGAS ESPECÍFICAS
print('\n 5. BUSCANDO IDs DE LIGAS CONOCIDAS:')
ligas_conocidas = [
    'Liga MX', 'Liga BBVA MX', 'Primera División de México',
    'Ascenso MX', 'Liga de Expansión MX'
]

for liga in ligas_conocidas:
    url = "https://v3.football.api-sports.io/leagues"
    params = {"name": liga, "country": "Mexico"}
    try:
        print(f'\n   Buscando: "{liga}"')
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                for l in data['response']:
                    print(f'       {l["league"]["name"]} (ID: {l["league"]["id"]})')
            else:
                print('       No encontrado')
    except Exception as e:
        print(f'      Error: {e}')  #  CORREGIDO: comilla cerrada

print('\n' + '=' * 70)
print(' DIAGNÓSTICO COMPLETADO')
