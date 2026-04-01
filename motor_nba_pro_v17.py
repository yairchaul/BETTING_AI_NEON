# -*- coding: utf-8 -*-
"""
MOTOR NBA PRO V17 - Con datos de prueba
"""

import numpy as np
import random
import logging

logger = logging.getLogger(__name__)

def analizar_nba_pro_v17(partido_data):
    """Analiza partido NBA con datos de prueba robustos"""
    local = partido_data.get('home', partido_data.get('local', 'Local'))
    visitante = partido_data.get('away', partido_data.get('visitante', 'Visitante'))
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 225.0)
    
    # Datos de prueba basados en fuerza percibida de equipos
    equipos_fuertes = ["Lakers", "Celtics", "Bucks", "Nuggets", "Suns", "Warriors"]
    equipos_debiles = ["Pistons", "Wizards", "Hornets", "Blazers", "Spurs"]
    
    # Calcular proyecciones basadas en fuerza
    factor_local = 1.5 if local in equipos_fuertes else (0.5 if local in equipos_debiles else 1.0)
    factor_visit = 1.5 if visitante in equipos_fuertes else (0.5 if visitante in equipos_debiles else 1.0)
    
    base_local = 112.0
    base_visit = 110.0
    
    expected_local = base_local + factor_local * 3
    expected_visit = base_visit + factor_visit * 3
    total_proyectado = expected_local + expected_visit
    
    # Probabilidad de OVER
    prob_over = 1 / (1 + np.exp(-(total_proyectado - linea_ou) / 10))
    
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
