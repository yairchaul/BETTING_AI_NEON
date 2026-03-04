import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

print(' OBTENIENDO EQUIPOS DE LIGA MX')
print('=' * 60)

# Obtener equipos de Liga MX (ID: 262)
url = "https://v3.football.api-sports.io/teams"
params = {"league": 262, "season": 2024}

try:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('response', [])
        print(f' Encontrados {len(equipos)} equipos:')
        
        print('\n LISTA PARA SMARTSEARCHER:')
        print('self.team_name_mappings = {')
        for eq in equipos:
            team = eq['team']
            nombre = team['name']
            nombre_lower = nombre.lower()
            print(f"    '{nombre_lower}': ['{nombre}'],")
        print('}')
        
        print('\n EQUIPOS POR NOMBRE:')
        for eq in equipos:
            team = eq['team']
            print(f"    {team['name']} (ID: {team['id']})")
    else:
        print(f' Error: {response.status_code}')
except Exception as e:
    print(f' Error: {e}')
