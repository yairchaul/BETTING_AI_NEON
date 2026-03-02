# modules/montecarlo.py
import numpy as np

def run_simulation(home_attack=1.3, home_defense=1.1, away_attack=1.2, away_defense=1.2, simulations=20000):
    """Simulación Monte Carlo con análisis detallado de todos los mercados"""
    
    # Valores por defecto basados en estadísticas reales de ligas
    league_avg = 1.35
    
    # Calcular goles esperados
    lambda_home = max(0.3, league_avg * (home_attack / 1.2) * (1.2 / away_defense) * 1.1)
    lambda_away = max(0.2, league_avg * (away_attack / 1.2) * (1.2 / home_defense))
    
    # Generar goles con ruido
    noise_home = np.random.normal(1, 0.12, simulations)
    noise_away = np.random.normal(1, 0.12, simulations)
    
    goals_home = np.random.poisson(lambda_home * np.abs(noise_home))
    goals_away = np.random.poisson(lambda_away * np.abs(noise_away))
    total_goals = goals_home + goals_away
    
    # Simular goles en primer tiempo (asumiendo 42% de los goles en 1T)
    first_half_factor = 0.42
    first_half_goals = np.random.binomial(total_goals.astype(int), first_half_factor)
    second_half_goals = total_goals - first_half_goals
    
    # Métricas especiales
    prob_over_5_5 = np.mean(total_goals > 5.5)
    prob_over_4_5 = np.mean(total_goals > 4.5)
    
    # Probabilidad de que un equipo sea goleador
    local_high_scorer = np.mean(goals_home >= 3)
    away_high_scorer = np.mean(goals_away >= 3)
    
    # Ambos anotan en primer tiempo
    btts_first_half = np.mean((first_half_goals > 0) & 
                               (goals_home > 0) & (goals_away > 0))
    
    # Over en primer tiempo
    over_1_5_first_half = np.mean(first_half_goals > 1.5)
    over_0_5_first_half = np.mean(first_half_goals > 0.5)
    
    # Goleadas
    home_win_by_2 = np.mean((goals_home - goals_away) >= 2)
    away_win_by_2 = np.mean((goals_away - goals_home) >= 2)
    home_win_by_3 = np.mean((goals_home - goals_away) >= 3)
    away_win_by_3 = np.mean((goals_away - goals_home) >= 3)
    
    return {
        # Resultados
        'local_gana': float(np.mean(goals_home > goals_away)),
        'empate': float(np.mean(goals_home == goals_away)),
        'visitante_gana': float(np.mean(goals_away > goals_home)),
        
        # Totales progresivos
        'over_0.5': float(np.mean(total_goals > 0.5)),
        'over_1.5': float(np.mean(total_goals > 1.5)),
        'over_2.5': float(np.mean(total_goals > 2.5)),
        'over_3.5': float(np.mean(total_goals > 3.5)),
        'over_4.5': float(prob_over_4_5),
        'over_5.5': float(prob_over_5_5),
        
        # Primer tiempo
        'over_0.5_1t': float(over_0_5_first_half),
        'over_1.5_1t': float(over_1_5_first_half),
        'btts_1t': float(btts_first_half),
        
        # BTTS
        'btts': float(np.mean((goals_home > 0) & (goals_away > 0))),
        
        # Handicaps
        'local_gana_por_2+': float(home_win_by_2),
        'visitante_gana_por_2+': float(away_win_by_2),
        'local_gana_por_3+': float(home_win_by_3),
        'visitante_gana_por_3+': float(away_win_by_3),
        
        # Goleadores
        'local_marca_3+': float(local_high_scorer),
        'visitante_marca_3+': float(away_high_scorer),
        
        # Estadísticas
        'goles_promedio': float(np.mean(total_goals)),
        'goles_local_promedio': float(np.mean(goals_home)),
        'goles_visit_promedio': float(np.mean(goals_away))
    }
