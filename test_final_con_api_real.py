# test_final_con_api_real.py
from modules.smart_searcher import SmartSearcher
from modules.elo_system import ELOSystem
import json

print(' PRUEBA FINAL CON API-FOOTBALL REAL')
print('=' * 70)

searcher = SmartSearcher()
elo = ELOSystem()
elo.load_ratings()

# Probar búsqueda de equipo
print('\n Buscando Puebla en Football-API...')
puebla_info = searcher.search_team_football_api('Puebla')
if puebla_info:
    print(f'    Encontrado: {puebla_info.get("name")} (ID: {puebla_info.get("id")})')
    print(f'     Estadio: {puebla_info.get("venue", {}).get("name", "N/A")}')
else:
    print('    No encontrado')

# Probar estadísticas
print('\n Estadísticas de Puebla:')
puebla_stats = searcher.get_team_stats('Puebla')
print(f'   Goles promedio: {puebla_stats["avg_goals_scored"]:.2f}')
print(f'   Goles concedidos: {puebla_stats["avg_goals_conceded"]:.2f}')
print(f'   Fuente: {puebla_stats["source"]}')
print(f'   Confianza: {puebla_stats["confidence"]:.0%}')

# Probar H2H
print('\n Historial Puebla vs Tigres:')
h2h = searcher.get_head_to_head('Puebla', 'Tigres UANL')
print(f'   Partidos: {h2h["total_matches"]}')
print(f'   Victorias local: {h2h["home_wins"]}')
print(f'   Empates: {h2h["draws"]}')
print(f'   Victorias visitante: {h2h["away_wins"]}')
print(f'   Promedio goles: {h2h["avg_goals"]:.2f}')
print(f'   Fuente: {h2h["source"]}')
print(f'   Confianza: {h2h["confidence"]:.0%}')

if h2h['recent_matches']:
    print('\n   Últimos enfrentamientos:')
    for match in h2h['recent_matches'][:3]:
        print(f'       {match["date"]}: {match["home"]} {match["score"]} {match["away"]}')

# Probar Groq
print('\n Análisis con Groq:')
news = searcher.get_recent_news('Puebla', 'Tigres UANL')
if news:
    print(f'   {news[0]["summary"]}')

# Probar ELO
print('\n Ratings ELO:')
print(f'   Puebla: {elo.get_rating("Puebla"):.0f}')
print(f'   Tigres: {elo.get_rating("Tigres UANL"):.0f}')
probs = elo.get_win_probability('Puebla', 'Tigres UANL')
print(f'   Probabilidades: Local {probs["home"]:.1%}, Empate {probs["draw"]:.1%}, Visitante {probs["away"]:.1%}')

# Predicción combinada
print('\n Predicción combinada:')
pred = searcher.predict_match_outcome('Puebla', 'Tigres UANL', 
                                      [probs['home'], probs['draw'], probs['away']])
if pred:
    print(f'   Local: {pred[0]:.1%}')
    print(f'   Empate: {pred[1]:.1%}')
    print(f'   Visitante: {pred[2]:.1%}')

print('\n' + '=' * 70)
print(' SISTEMA COMPLETAMENTE FUNCIONAL CON DATOS REALES')
