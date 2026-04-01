# -*- coding: utf-8 -*-
"""
MOTOR FÚTBOL PRO - Con fuerza base por equipo
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

# Fuerza base de equipos de fútbol (0-100)
EQUIPOS_FUERZA_FUTBOL = {
    "Real Madrid": 95, "Barcelona": 93, "Manchester City": 94, "Liverpool": 92,
    "Bayern": 91, "PSG": 90, "Arsenal": 88, "Chelsea": 86, "Inter": 85,
    "AC Milan": 84, "Juventus": 83, "Atletico": 82, "Dortmund": 81, "Napoli": 80,
    "Roma": 78, "Lazio": 77, "Sevilla": 76, "Villarreal": 75, "Real Sociedad": 74,
    "Athletic": 73, "Valencia": 72, "Betis": 71
}

def obtener_fuerza_equipo(equipo):
    """Obtiene fuerza base del equipo de fútbol"""
    for nombre, fuerza in EQUIPOS_FUERZA_FUTBOL.items():
        if nombre.lower() in equipo.lower() or equipo.lower() in nombre.lower():
            return fuerza
    return 70


def analizar_futbol_pro_v20(partido_data):
    """Analiza partido de fútbol con fuerza de equipos"""
    local = partido_data.get('home', partido_data.get('local', 'Local'))
    visitante = partido_data.get('away', partido_data.get('visitante', 'Visitante'))
    
    fuerza_local = obtener_fuerza_equipo(local)
    fuerza_visit = obtener_fuerza_equipo(visitante)
    
    # Goles esperados
    base_goles = 1.5
    expected_local = base_goles + (fuerza_local - 70) * 0.025
    expected_visit = base_goles + (fuerza_visit - 70) * 0.025
    total_proyectado = expected_local + expected_visit
    
    # Probabilidades
    prob_over_25 = 1 / (1 + np.exp(-(total_proyectado - 2.5) / 1.2))
    prob_btts = 0.45 + (expected_local * expected_visit / 5) * 0.4
    prob_local_win = 0.45 + (fuerza_local - fuerza_visit) / 150
    
    prob_over_25 = min(0.85, max(0.15, prob_over_25))
    prob_btts = min(0.85, max(0.15, prob_btts))
    prob_local_win = min(0.75, max(0.25, prob_local_win))
    
    if prob_over_25 > 0.6:
        recomendacion = "OVER 2.5"
        confianza = int(prob_over_25 * 100)
        probabilidad = prob_over_25
    elif prob_btts > 0.6:
        recomendacion = "BTTS"
        confianza = int(prob_btts * 100)
        probabilidad = prob_btts
    elif prob_local_win > 0.55:
        recomendacion = f"GANA {local}"
        confianza = int(prob_local_win * 100)
        probabilidad = prob_local_win
    else:
        recomendacion = "SIN VALOR CLARO"
        confianza = 50
        probabilidad = 0.5
    
    confianza = min(85, max(40, confianza))
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(probabilidad * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'proyeccion_local': round(expected_local, 1),
        'proyeccion_visitante': round(expected_visit, 1),
        'prob_over_25': round(prob_over_25 * 100, 1),
        'prob_btts': round(prob_btts * 100, 1),
        'etiqueta_verde': confianza >= 70,
        'edge': round((probabilidad - 0.5) * 100, 1)
    }
