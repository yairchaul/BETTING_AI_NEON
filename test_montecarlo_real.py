# test_montecarlo_real.py
from modules.montecarlo_pro import MonteCarloPro
from modules.smart_searcher import SmartSearcher
import numpy as np

print('🔍 PRUEBA REAL DE MONTECARLO')
print('=' * 60)

searcher = SmartSearcher()
montecarlo = MonteCarloPro(simulations=10000)

# Obtener datos reales de Puebla vs Tigres
puebla_stats = searcher.get_team_stats('Puebla')
tigres_stats = searcher.get_team_stats('Tigres UANL')

print(f'\n Puebla: {puebla_stats}')
print(f' Tigres: {tigres_stats}')

# Calcular fuerzas basado en datos REALES
home_attack = puebla_stats.get('avg_goals_scored', 1.2) if puebla_stats else 1.2
home_defense = puebla_stats.get('avg_goals_conceded', 1.2) if puebla_stats else 1.2
away_attack = tigres_stats.get('avg_goals_scored', 1.2) if tigres_stats else 1.2
away_defense = tigres_stats.get('avg_goals_conceded', 1.2) if tigres_stats else 1.2

print(f'\n Fuerzas calculadas:')
print(f'   Ataque Local: {home_attack:.2f}')
print(f'   Defensa Local: {home_defense:.2f}')
print(f'   Ataque Visitante: {away_attack:.2f}')
print(f'   Defensa Visitante: {away_defense:.2f}')

# Calcular lambdas para Poisson
lambda_home = home_attack * away_defense
lambda_away = away_attack * home_defense

print(f'\n Lambdas Poisson: Local={lambda_home:.2f}, Visitante={lambda_away:.2f}')

# Simular con Monte Carlo
try:
    resultados = montecarlo.simulate_match(lambda_home, lambda_away)
    print(f'\n RESULTADOS MONTECARLO:')
    print(f'   Goles promedio local: {resultados.get("avg_home_goals", 0):.2f}')
    print(f'   Goles promedio visitante: {resultados.get("avg_away_goals", 0):.2f}')
    print(f'   BTTS: {resultados.get("btts", 0):.1%}')
    print(f'   Over 1.5: {resultados.get("over_1_5", 0):.1%}')
    print(f'   Over 2.5: {resultados.get("over_2_5", 0):.1%}')
except Exception as e:
    print(f' Error en simulate_match: {e}')
    
    # Alternativa: calcular manualmente
    print('\n Calculando manualmente...')
    home_goals = np.random.poisson(lambda_home, 10000)
    away_goals = np.random.poisson(lambda_away, 10000)
    total_goals = home_goals + away_goals
    btts = np.mean((home_goals > 0) & (away_goals > 0))
    
    print(f'   Goles promedio local: {np.mean(home_goals):.2f}')
    print(f'   Goles promedio visitante: {np.mean(away_goals):.2f}')
    print(f'   BTTS: {btts:.1%}')
    print(f'   Over 1.5: {np.mean(total_goals > 1.5):.1%}')
    print(f'   Over 2.5: {np.mean(total_goals > 2.5):.1%}')
