# -*- coding: utf-8 -*-
"""
MOTOR FÚTBOL PRO - Con datos de prueba
"""

import numpy as np

def analizar_futbol_pro_v20(partido_data):
    """Analiza partido de fútbol con datos de prueba"""
    local = partido_data.get('home', partido_data.get('local', 'Local'))
    visitante = partido_data.get('away', partido_data.get('visitante', 'Visitante'))
    
    # Datos de prueba basados en fuerza percibida
    equipos_fuertes = ["Real Madrid", "Barcelona", "Manchester City", "Liverpool", "Bayern", "PSG"]
    equipos_debiles = ["Getafe", "Elche", "Cadiz", "Almeria"]
    
    factor_local = 1.3 if local in equipos_fuertes else (0.7 if local in equipos_debiles else 1.0)
    factor_visit = 1.3 if visitante in equipos_fuertes else (0.7 if visitante in equipos_debiles else 1.0)
    
    base_local = 1.8
    base_visit = 1.5
    
    expected_local = base_local * factor_local
    expected_visit = base_visit * factor_visit
    total_proyectado = expected_local + expected_visit
    
    prob_over_25 = 1 / (1 + np.exp(-(total_proyectado - 2.5) / 1.5))
    prob_btts = 0.5 + (expected_local * expected_visit / 6) * 0.3
    prob_local_win = 0.45 + (factor_local - factor_visit) * 0.15
    
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
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(probabilidad * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'proyeccion_local': round(expected_local, 1),
        'proyeccion_visitante': round(expected_visit, 1),
        'prob_over_25': round(prob_over_25 * 100, 1),
        'prob_btts': round(prob_btts * 100, 1),
        'etiqueta_verde': confianza >= 70
    }
