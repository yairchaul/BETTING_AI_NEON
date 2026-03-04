# test_searcher_real.py
from modules.smart_searcher import SmartSearcher
import json

print('🔍 PRUEBA REAL DE SMARTSEARCHER')
print('=' * 60)

searcher = SmartSearcher()

# Probar con equipos reales de la captura
equipos = ['Puebla', 'Tigres UANL', 'Monterrey', 'América']

for equipo in equipos:
    print(f'\n BUSCANDO: {equipo}')
    print('-' * 40)
    
    # Buscar estadísticas del equipo
    stats = searcher.get_team_stats(equipo)
    print(f' Estadísticas: {json.dumps(stats, indent=2, ensure_ascii=False)[:200]}...')
    
    # Buscar enfrentamientos
    if equipo == 'Puebla':
        h2h = searcher.get_head_to_head('Puebla', 'Tigres UANL')
        print(f' Historial vs Tigres: {json.dumps(h2h, indent=2, ensure_ascii=False)[:200]}...')
