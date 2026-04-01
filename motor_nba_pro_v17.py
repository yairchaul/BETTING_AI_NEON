# -*- coding: utf-8 -*-
"""
MOTOR NBA PRO V17 - Con Player Props (Líder en 3PM y puntos)
"""

import numpy as np
import logging
from database_manager import db

logger = logging.getLogger(__name__)

def analizar_nba_pro_v17(partido_data):
    """
    Analiza partido NBA y devuelve recomendación con jugadores destacados
    """
    local = partido_data.get('home', partido_data.get('local', ''))
    visitante = partido_data.get('away', partido_data.get('visitante', ''))
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 225.0)

    # Stats de equipos desde BD
    stats_l = db.get_team_stats(local, 'nba', limit=5) or {}
    stats_v = db.get_team_stats(visitante, 'nba', limit=5) or {}

    # Valores por defecto si no hay datos
    expected_local = stats_l.get('promedio_favor', 112) if stats_l.get('promedio_favor') else 112
    expected_visit = stats_v.get('promedio_favor', 110) if stats_v.get('promedio_favor') else 110
    total_proyectado = expected_local + expected_visit

    # PLAYER PROPS: Líder en 3PM y puntos
    top_3pm_local = db.get_top_player_stat(local, 'three_pm', limit=1, deporte='nba')
    top_3pm_visit = db.get_top_player_stat(visitante, 'three_pm', limit=1, deporte='nba')
    top_points_local = db.get_top_player_stat(local, 'points', limit=1, deporte='nba')
    top_points_visit = db.get_top_player_stat(visitante, 'points', limit=1, deporte='nba')

    # Cálculo de probabilidad (placeholder mejorable)
    diff = expected_local - expected_visit
    prob_local = 0.5 + (diff / 50)  # Simplificado
    prob_local = max(0.3, min(0.7, prob_local))
    
    # Over/Under basado en total proyectado vs línea
    if total_proyectado > linea_ou:
        prob_over = 0.55 + (total_proyectado - linea_ou) / 50
        prob_over = min(0.75, prob_over)
        recomendacion = f"OVER {linea_ou}"
        confianza = int(prob_over * 100) - 10
    else:
        prob_over = 0.45 - (linea_ou - total_proyectado) / 50
        prob_over = max(0.25, prob_over)
        recomendacion = f"UNDER {linea_ou}"
        confianza = int((1 - prob_over) * 100) - 10

    confianza = max(50, min(85, confianza))

    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(prob_over * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'top_3pm_local': top_3pm_local,
        'top_3pm_visit': top_3pm_visit,
        'top_points_local': top_points_local,
        'top_points_visit': top_points_visit,
        'etiqueta_verde': confianza >= 65,
        'edge': round((prob_over - 0.5) * 100, 1)
    }
