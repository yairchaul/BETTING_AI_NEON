# test_todas_variantes.py
import requests
import streamlit as st

print(' PROBANDO TODAS LAS VARIANTES DE NOMBRES')
print('=' * 70)

API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Diccionario de equipos con todas sus posibles variantes
equipos = {
    'Puebla': [
        'Puebla', 'Club Puebla', 'Puebla FC', 'FC Puebla', 
        'Puebla F.C.', 'C. Puebla', 'Club Puebla FC'
    ],
    'Tigres': [
        'Tigres', 'Tigres UANL', 'UANL', 'Tigres de la UANL',
        'Club Tigres', 'Tigres FC', 'Tigres U.A.N.L.'
    ],
    'Monterrey': [
        'Monterrey', 'CF Monterrey', 'Monterrey FC', 'FC Monterrey',
        'C.F. Monterrey', 'Rayados', 'Club de Futbol Monterrey'
    ],
    'América': [
        'América', 'Club América', 'America', 'Club America',
        'C.F. América', 'CF America', 'Club de Fútbol América'
    ],
    'Chivas': [
        'Chivas', 'Guadalajara', 'CD Guadalajara', 'C.D. Guadalajara',
        'Chivas Rayadas', 'Club Deportivo Guadalajara'
    ],
    'Cruz Azul': [
        'Cruz Azul', 'CD Cruz Azul', 'C.D. Cruz Azul',
        'Cruz Azul FC', 'Club Deportivo Cruz Azul'
    ],
    'Atlas': [
        'Atlas', 'Atlas FC', 'FC Atlas', 'Club Atlas',
        'Atlas F.C.', 'F.C. Atlas'
    ],
    'Tijuana': [
        'Tijuana', 'Xolos', 'Club Tijuana', 'Xolos de Tijuana',
        'C. Tijuana', 'Tijuana Xolos'
    ],
    'Juárez': [
        'Juárez', 'FC Juárez', 'Juarez', 'FC Juarez',
        'Club Juárez', 'Bravos de Juárez'
    ],
    'Querétaro': [
        'Querétaro', 'Queretaro', 'Querétaro FC', 'Queretaro FC',
        'Club Querétaro', 'Gallos Blancos'
    ]
}

print('\n Probando TODAS las variantes:')
print('=' * 60)

for equipo, variantes in equipos.items():
    print(f'\n {equipo}:')
    print('-' * 40)
    
    encontrado = False
    for variante in variantes:
        try:
            url = "https://v3.football.api-sports.io/teams"
            params = {"search": variante}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('response') and len(data['response']) > 0:
                    team = data['response'][0]['team']
                    print(f'    "{variante}"  {team["name"]} (ID: {team["id"]})')
                    encontrado = True
                    break
                else:
                    print(f'    "{variante}"  No encontrado')
            else:
                print(f'    "{variante}"  Error {response.status_code}')
                
        except Exception as e:
            print(f'    "{variante}"  Error: {e}')
    
    if not encontrado:
        print(f'     No se encontró NINGUNA variante para {equipo}')

# 4. Probar búsqueda por estadio o ciudad
print('\n\n  PROBANDO BÚSQUEDA POR CIUDAD/ESTADIO:')
ciudades = ['Puebla', 'Monterrey', 'Guadalajara', 'Ciudad de México']

for ciudad in ciudades:
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": ciudad, "country": "Mexico"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                print(f'\n Equipos en {ciudad}:')
                for team in data['response'][:3]:
                    print(f'    {team["team"]["name"]}')
            else:
                print(f'\n No hay equipos en {ciudad}')
    except Exception as e:
        print(f' Error: {e}')

# 5. Verificar endpoint de status
print('\n\n VERIFICANDO ESTADO DE LA API:')
url = "https://v3.football.api-sports.io/status"
try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f' API activa: {data}')
    else:
        print(f' Error {response.status_code}')
except Exception as e:
    print(f' Error: {e}')

print('\n' + '=' * 70)
