# test_pumas_final.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

print(' BUSCANDO NOMBRE EXACTO DE PUMAS')
print('=' * 60)

variantes = [
    'Pumas',
    'UNAM',
    'U.N.A.M.',
    'Pumas UNAM',
    'Club Universidad Nacional',
    'Universidad Nacional',
    'Pumas de la UNAM',
    'Pumas U.N.A.M.'
]

for variante in variantes:
    print(f'\n Probando: "{variante}"')
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": variante}
    
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
        print(f'    Error: {e}')  #  AHORA SÍ ESTÁ BIEN CERRADO

print('\n' + '=' * 60)
