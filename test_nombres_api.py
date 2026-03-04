# test_nombres_api.py
from modules.smart_searcher import SmartSearcher
import requests

print(' DESCUBRIENDO NOMBRES EXACTOS EN FOOTBALL-API')
print('=' * 70)

searcher = SmartSearcher()

# Lista de equipos a probar con diferentes variantes
equipos_a_probar = [
    'Puebla',
    'Club Puebla',
    'Puebla FC',
    'Tigres',
    'Tigres UANL',
    'UANL',
    'Monterrey',
    'CF Monterrey',
    'Rayados',
    'América',
    'Club América',
    'Chivas',
    'Guadalajara',
    'Cruz Azul',
    'Atlas',
    'Tijuana',
    'Xolos',
    'Juárez',
    'FC Juárez',
    'Querétaro',
    'Querétaro FC'
]

print('\n Probando búsquedas en Football-API:')
print('-' * 50)

for equipo in equipos_a_probar:
    print(f'\n Buscando: "{equipo}"')
    
    try:
        url = "https://v3.football.api-sports.io/teams"
        params = {"search": equipo}
        headers = {
            'x-rapidapi-key': searcher.football_api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                team = data['response'][0]['team']
                print(f'    ENCONTRADO: {team["name"]} (ID: {team["id"]})')
            else:
                print('    No encontrado')
        else:
            print(f'    Error {response.status_code}')
            
    except Exception as e:
        print(f'    Error: {e}')  #  CORREGIDO: comilla cerrada correctamente

print('\n' + '=' * 70)
