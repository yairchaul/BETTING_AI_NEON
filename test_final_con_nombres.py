# test_final_con_nombres.py
from modules.smart_searcher import SmartSearcher

print(' PROBANDO BÚSQUEDA CON NOMBRES CORREGIDOS')
print('=' * 60)

searcher = SmartSearcher()

equipos_a_probar = [
    'Puebla',
    'Tigres',
    'América',
    'Chivas',
    'Cruz Azul',
    'Pumas',
    'Monterrey',
    'Atlas',
    'Santos',
    'San Luis'
]

print('\n Resultados de búsqueda:')
print('-' * 40)

for equipo in equipos_a_probar:
    print(f'\n Buscando: "{equipo}"')
    team_info = searcher.search_team_football_api(equipo)
    if team_info:
        print(f'    ENCONTRADO: {team_info["name"]} (ID: {team_info["id"]})')
    else:
        print(f'    No encontrado en API')
