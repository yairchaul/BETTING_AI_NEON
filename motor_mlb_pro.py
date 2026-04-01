# -*- coding: utf-8 -*-
"""
MOTOR MLB PRO - Análisis con Poisson + Monte Carlo
"""

import numpy as np
from scipy.stats import poisson
import logging
from database_manager import db

logger = logging.getLogger(__name__)

def analizar_mlb_pro_v20(partido_data):
    """
    Analiza partido MLB con Poisson + Monte Carlo
    
    Args:
        partido_data: dict con local, visitante, odds
    
    Returns:
        dict con recomendacion, confianza, etc.
    """
    local = partido_data.get('home', '')
    visitante = partido_data.get('away', '')
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 8.5)
    
    # Obtener últimos 5 partidos
    stats_l = db.get_team_stats(local, deporte='mlb', limit=5)
    stats_v = db.get_team_stats(visitante, deporte='mlb', limit=5)
    
    if not stats_l or not stats_v:
        logger.warning(f"Datos insuficientes para {local} vs {visitante}")
        return {
            'recomendacion': 'DATOS INSUFICIENTES',
            'confianza': 40,
            'total_proyectado': 8.5,
            'etiqueta_verde': False
        }
    
    # Proyección
    ataque_l = stats_l.get('promedio_favor', 4.5)
    defensa_v = stats_v.get('promedio_contra', 4.5)
    ataque_v = stats_v.get('promedio_favor', 4.5)
    defensa_l = stats_l.get('promedio_contra', 4.5)
    
    expected_local = (ataque_l * 0.55 + defensa_v * 0.45) * 1.02
    expected_visit = (ataque_v * 0.55 + defensa_l * 0.45) * 1.02
    total_proyectado = expected_local + expected_visit
    
    # Simulación Monte Carlo
    np.random.seed(42)
    sim_local = poisson.rvs(expected_local, size=10000)
    sim_visit = poisson.rvs(expected_visit, size=10000)
    sim_total = sim_local + sim_visit
    
    prob_over = np.mean(sim_total > linea_ou)
    prob_under = 1 - prob_over
    
    if prob_over > 0.55:
        recomendacion = f"OVER {linea_ou}"
        confianza = int(prob_over * 100)
    elif prob_under > 0.55:
        recomendacion = f"UNDER {linea_ou}"
        confianza = int(prob_under * 100)
    else:
        recomendacion = "SIN VALOR CLARO"
        confianza = 50
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(max(prob_over, prob_under) * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'proyeccion_local': round(expected_local, 1),
        'proyeccion_visitante': round(expected_visit, 1),
        'etiqueta_verde': confianza >= 70,
        'stats_local': stats_l,
        'stats_visitante': stats_v
    }
