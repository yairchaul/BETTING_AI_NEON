# -*- coding: utf-8 -*-
"""
MOTOR MLB PRO - Con Player Props (Probabilidad de Home Run y bateadores destacados)
"""

import numpy as np
import logging
from database_manager import db

logger = logging.getLogger(__name__)

def analizar_mlb_pro_v20(partido_data):
    """
    Analiza partido MLB y devuelve recomendación con bateadores destacados
    """
    local = partido_data.get('home', partido_data.get('local', ''))
    visitante = partido_data.get('away', partido_data.get('visitante', ''))
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 8.5)

    # Stats de equipos desde BD
    stats_l = db.get_team_stats(local, 'mlb', limit=5) or {}
    stats_v = db.get_team_stats(visitante, 'mlb', limit=5) or {}

    # Valores por defecto
    expected_local = stats_l.get('promedio_favor', 4.5) if stats_l.get('promedio_favor') else 4.5
    expected_visit = stats_v.get('promedio_favor', 4.2) if stats_v.get('promedio_favor') else 4.2
    total_proyectado = expected_local + expected_visit

    # PLAYER PROPS: Top candidatos a HR
    top_hr_local = db.get_top_player_stat(local, 'hr', limit=2, deporte='mlb')
    top_hr_visit = db.get_top_player_stat(visitante, 'hr', limit=2, deporte='mlb')
    top_avg_local = db.get_top_player_stat(local, 'avg', limit=1, deporte='mlb')
    top_avg_visit = db.get_top_player_stat(visitante, 'avg', limit=1, deporte='mlb')

    # Cálculo de probabilidad Over/Under
    if total_proyectado > linea_ou:
        prob_over = 0.52 + (total_proyectado - linea_ou) / 20
        prob_over = min(0.70, prob_over)
        recomendacion = f"OVER {linea_ou}"
        confianza = int(prob_over * 100) - 5
    else:
        prob_over = 0.48 - (linea_ou - total_proyectado) / 20
        prob_over = max(0.30, prob_over)
        recomendacion = f"UNDER {linea_ou}"
        confianza = int((1 - prob_over) * 100) - 5

    confianza = max(50, min(80, confianza))

    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(prob_over * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'top_hr_local': top_hr_local,
        'top_hr_visit': top_hr_visit,
        'top_avg_local': top_avg_local,
        'top_avg_visit': top_avg_visit,
        'etiqueta_verde': confianza >= 60,
        'edge': round((prob_over - 0.5) * 100, 1)
    }
