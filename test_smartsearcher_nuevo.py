# test_smartsearcher_nuevo.py
from modules.smart_searcher import SmartSearcher
import json

print(' PROBANDO SMARTSEARCHER ACTUALIZADO')
print('=' * 60)

searcher = SmartSearcher()

print(f'\n Modelo Groq: {searcher.modelo_groq}')
print(f'   Groq disponible: {"" if searcher.groq_client else ""}')

# Probar búsqueda en Football-API
print('\n Buscando Puebla en Football-API...')
puebla_info = searcher.search_team_football_api('Puebla')
if puebla_info:
    print(f'    Encontrado: {puebla_info.get("name")} (ID: {puebla_info.get("id")})')
else:
    print('    No encontrado')

# Probar estadísticas
print('\n Estadísticas de Puebla:')
puebla_stats = searcher.get_team_stats('Puebla')
print(f'   Goles promedio: {puebla_stats["avg_goals_scored"]:.2f}')
print(f'   Goles concedidos: {puebla_stats["avg_goals_conceded"]:.2f}')
print(f'   Confianza: {puebla_stats["confidence"]:.0%}')

# Probar H2H
print('\n Historial Puebla vs Tigres:')
h2h = searcher.get_head_to_head('Puebla', 'Tigres UANL')
print(f'   Partidos: {h2h["total_matches"]}')
print(f'   Victorias local: {h2h["home_wins"]}')
print(f'   Empates: {h2h["draws"]}')
print(f'   Victorias visitante: {h2h["away_wins"]}')
print(f'   Promedio goles: {h2h["avg_goals"]:.2f}')
print(f'   BTTS: {h2h["btts_rate"]:.0%}')
print(f'   Confianza: {h2h["confidence"]:.0%}')

# Probar Groq
if searcher.groq_client:
    print('\n Análisis con Groq:')
    news = searcher.get_recent_news('Puebla', 'Tigres UANL')
    if news:
        print(f'   {news[0]["summary"][:200]}...')
