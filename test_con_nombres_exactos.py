# test_con_nombres_exactos.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

# Nombres EXACTOS que devolvió la API
nombres_exactos = {
    'puebla': 'Puebla',
    'tigres': 'Tigres UANL',
    'america': 'Club America',
    'chivas': 'Guadalajara Chivas',
    'cruz azul': 'Cruz Azul',
    'pumas': 'U.N.A.M. - Pumas',
    'monterrey': 'Monterrey',
    'atlas': 'Atlas',
    'santos': 'Santos Laguna',
    'san luis': 'Atletico San Luis'
}

print(' PROBANDO CON NOMBRES EXACTOS DE LA API')
print('=' * 60)

for clave, nombre_exacto in nombres_exactos.items():
    print(f'\n Buscando: "{nombre_exacto}"')
    
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": nombre_exacto}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                team = data['response'][0]['team']
                print(f'    ENCONTRADO: {team["name"]} (ID: {team["id"]})')
            else:
                print(f'    No encontrado')
        else:
            print(f'    Error HTTP: {response.status_code}')
    except Exception as e:
        print(f'    Error: {e}')  #  CORREGIDO: comilla cerrada
