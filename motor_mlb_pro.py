# -*- coding: utf-8 -*-
"""
MOTOR MLB PRO - Con fuerza base por equipo
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

# Fuerza base de equipos MLB (0-100)
EQUIPOS_FUERZA_MLB = {
    "Dodgers": 92, "Yankees": 88, "Braves": 86, "Astros": 85, "Phillies": 84,
    "Padres": 82, "Rangers": 81, "Orioles": 80, "Blue Jays": 78, "Mariners": 77,
    "Mets": 76, "Cardinals": 75, "Diamondbacks": 74, "Reds": 72, "Giants": 71,
    "Cubs": 70, "Red Sox": 69, "Twins": 68, "Guardians": 67, "Tigers": 65,
    "Royals": 64, "Pirates": 62, "Athletics": 60, "Rockies": 58, "Marlins": 57,
    "Nationals": 56, "White Sox": 55, "Angels": 54
}

def obtener_fuerza_equipo(equipo):
    """Obtiene fuerza base del equipo MLB"""
    for nombre, fuerza in EQUIPOS_FUERZA_MLB.items():
        if nombre.lower() in equipo.lower() or equipo.lower() in nombre.lower():
            return fuerza
    return 70


def analizar_mlb_pro_v20(partido_data):
    """Analiza partido MLB con fuerza de equipos"""
    local = partido_data.get('home', partido_data.get('local', 'Local'))
    visitante = partido_data.get('away', partido_data.get('visitante', 'Visitante'))
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 8.5)
    
    fuerza_local = obtener_fuerza_equipo(local)
    fuerza_visit = obtener_fuerza_equipo(visitante)
    
    # Carreras esperadas
    base_carreras = 4.8
    expected_local = base_carreras + (fuerza_local - 70) * 0.04
    expected_visit = base_carreras + (fuerza_visit - 70) * 0.04
    total_proyectado = expected_local + expected_visit
    
    # Probabilidad de OVER
    diff = total_proyectado - linea_ou
    prob_over = 1 / (1 + np.exp(-diff / 1.8))
    prob_over = min(0.85, max(0.15, prob_over))
    
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
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(prob_over * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'proyeccion_local': round(expected_local, 1),
        'proyeccion_visitante': round(expected_visit, 1),
        'etiqueta_verde': confianza >= 70,
        'edge': round((prob_over - 0.5) * 100, 1)
    }
