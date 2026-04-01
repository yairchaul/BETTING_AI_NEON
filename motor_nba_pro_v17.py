# -*- coding: utf-8 -*-
"""
MOTOR NBA PRO V17 - Con fuerza base por equipo (más realista que lista simple)
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

# Fuerza base de equipos NBA (0-100)
EQUIPOS_FUERZA = {
    "Lakers": 88, "Celtics": 89, "Bucks": 87, "Nuggets": 86, "Suns": 84, "Warriors": 83,
    "Cavaliers": 85, "Thunder": 84, "Timberwolves": 82, "Knicks": 81, "Mavericks": 80,
    "Heat": 78, "76ers": 79, "Pelicans": 77, "Kings": 76, "Clippers": 75, "Grizzlies": 74,
    "Hawks": 72, "Rockets": 71, "Bulls": 70, "Raptors": 69, "Pacers": 68, "Magic": 67,
    "Hornets": 65, "Spurs": 64, "Jazz": 63, "Trail Blazers": 62, "Wizards": 60, "Pistons": 58
}

def obtener_fuerza_equipo(equipo):
    """Obtiene fuerza base del equipo (0-100)"""
    for nombre, fuerza in EQUIPOS_FUERZA.items():
        if nombre.lower() in equipo.lower() or equipo.lower() in nombre.lower():
            return fuerza
    return 70  # valor medio por defecto


def analizar_nba_pro_v17(partido_data):
    """Analiza partido NBA con datos de prueba basados en fuerza de equipos"""
    local = partido_data.get('home', partido_data.get('local', 'Local'))
    visitante = partido_data.get('away', partido_data.get('visitante', 'Visitante'))
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 225.0)
    
    # Obtener fuerza de equipos
    fuerza_local = obtener_fuerza_equipo(local)
    fuerza_visit = obtener_fuerza_equipo(visitante)
    
    # Convertir fuerza a puntos esperados (base 110 + ajuste)
    base_pts = 110
    expected_local = base_pts + (fuerza_local - 70) * 0.35
    expected_visit = base_pts + (fuerza_visit - 70) * 0.35
    total_proyectado = expected_local + expected_visit
    
    # Probabilidad de OVER
    diff = total_proyectado - linea_ou
    prob_over = 1 / (1 + np.exp(-diff / 12))
    prob_over = min(0.85, max(0.15, prob_over))
    
    # Decisión
    if prob_over > 0.55:
        recomendacion = f"OVER {linea_ou}"
        confianza = int(60 + (prob_over - 0.55) * 100)
    elif prob_over < 0.45:
        recomendacion = f"UNDER {linea_ou}"
        confianza = int(60 + (0.45 - prob_over) * 100)
    else:
        recomendacion = "SIN VALOR CLARO"
        confianza = 50
    
    confianza = min(85, max(40, confianza))
    
    # Probabilidad de moneyline (quién gana)
    prob_local_win = 0.5 + (fuerza_local - fuerza_visit) / 200
    prob_local_win = min(0.85, max(0.15, prob_local_win))
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(prob_over * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'proyeccion_local': round(expected_local, 1),
        'proyeccion_visitante': round(expected_visit, 1),
        'prob_local_win': round(prob_local_win * 100, 1),
        'etiqueta_verde': confianza >= 70,
        'edge': round((prob_over - 0.5) * 100, 1),
        'stats_local': {'fuerza': fuerza_local},
        'stats_visitante': {'fuerza': fuerza_visit}
    }
