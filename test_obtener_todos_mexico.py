# test_obtener_todos_mexico.py
import requests
import streamlit as st
import json

print(' OBTENIENDO TODOS LOS EQUIPOS DE MÉXICO (FORMA CORRECTA)')
print('=' * 70)

API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# 1. PRIMERO: Obtener todas las ligas de México
print('\n 1. LIGAS DISPONIBLES EN MÉXICO:')
url = "https://v3.football.api-sports.io/leagues"
params = {"country": "Mexico"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        ligas = data.get('response', [])
        print(f'    Encontradas {len(ligas)} ligas:')
        
        ligas_mx = []
        for liga in ligas:
            liga_info = liga['league']
            print(f'       {liga_info["name"]} (ID: {liga_info["id"]})')
            ligas_mx.append({
                'id': liga_info['id'],
                'name': liga_info['name']
            })
    else:
        print(f'    Error {response.status_code}')
except Exception as e:
    print(f'    Error: {e}')

# 2. SEGUNDO: Obtener TODOS los equipos de México por país
print('\n\n 2. TODOS LOS EQUIPOS DE MÉXICO (POR PAÍS):')
url = "https://v3.football.api-sports.io/teams"
params = {"country": "Mexico"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('response', [])
        print(f'    Encontrados {len(equipos)} equipos en total:')
        
        # Crear diccionario de mapeo
        mapeo_equipos = {}
        for eq in equipos:
            team = eq['team']
            print(f'       {team["name"]} (ID: {team["id"]})')
            # Guardar para mapeo
            nombre_normalizado = team['name'].lower()
            mapeo_equipos[nombre_normalizado] = team['name']
            
            # También guardar variantes sin acentos
            sin_acentos = nombre_normalizado.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            mapeo_equipos[sin_acentos] = team['name']
        
        print('\n\n MAPEO GENERADO (para copiar a smart_searcher.py):')
        print('=' * 50)
        print('self.team_name_mappings = {')
        for nombre_api in set(mapeo_equipos.values()):
            nombre_lower = nombre_api.lower()
            print(f"    '{nombre_lower}': ['{nombre_api}'],")
        print('}')
        
    else:
        print(f'    Error {response.status_code}')
except Exception as e:
    print(f'    Error: {e}')  #  CORREGIDO

# 3. TERCERO: Verificar equipos por liga específica (Liga MX)
if ligas_mx:
    liga_mx_id = next((l['id'] for l in ligas_mx if 'Liga MX' in l['name'] or 'Liga BBVA' in l['name']), None)
    
    if liga_mx_id:
        print(f'\n\n 3. EQUIPOS DE LIGA MX (ID: {liga_mx_id}):')
        url = "https://v3.football.api-sports.io/teams"
        params = {"league": liga_mx_id, "season": 2024}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                equipos = data.get('response', [])
                print(f'    Encontrados {len(equipos)} equipos en Liga MX:')
                for eq in equipos:
                    team = eq['team']
                    print(f'       {team["name"]}')
        except Exception as e:
            print(f'    Error: {e}')  #  CORREGIDO

print('\n' + '=' * 70)
