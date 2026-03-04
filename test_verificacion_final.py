# test_verificacion_final.py
from modules.smart_searcher import SmartSearcher

searcher = SmartSearcher()
equipos = ['Puebla', 'Tigres', 'América', 'Chivas', 'Cruz Azul', 'Pumas', 'Monterrey', 'Atlas']

print(' VERIFICACIÓN FINAL:')
print('=' * 50)

for equipo in equipos:
    print(f'\n Buscando: {equipo}')
    team_info = searcher.search_team_football_api(equipo)
    if team_info:
        print(f'    {team_info["name"]} (ID: {team_info["id"]})')
    else:
        print(f'    No encontrado')
