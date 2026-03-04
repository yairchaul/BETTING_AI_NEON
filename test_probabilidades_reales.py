# test_probabilidades_reales.py
from modules.elo_system import ELOSystem
import numpy as np

print(' PROBABILIDADES REALES CON ELO')
print('=' * 60)

elo = ELOSystem()
elo.load_ratings()

# Partidos de la captura
partidos = [
    ('Puebla', 'Tigres UANL'),
    ('Monterrey', 'Querétaro FC'),
    ('Atlas', 'Tijuana Xolos de Caliente'),
    ('América', 'FC Juárez')
]

for local, visitante in partidos:
    print(f'\n {local} vs {visitante}')
    print('-' * 40)
    
    probs = elo.get_win_probability(local, visitante)
    
    print(f'   Local ({local}): {probs["home"]:.1%}')
    print(f'   Empate: {probs["draw"]:.1%}')
    print(f'   Visitante ({visitante}): {probs["away"]:.1%}')
    
    # Calcular odds justas (inversa de probabilidad)
    odds_justas = {
        'local': 1/probs["home"] if probs["home"] > 0 else 0,
        'draw': 1/probs["draw"] if probs["draw"] > 0 else 0,
        'away': 1/probs["away"] if probs["away"] > 0 else 0
    }
    
    print(f'\n   Odds justas (ELO):')
    print(f'      Local: {odds_justas["local"]:.2f}')
    print(f'      Empate: {odds_justas["draw"]:.2f}')
    print(f'      Visitante: {odds_justas["away"]:.2f}')
