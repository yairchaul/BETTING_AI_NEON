# -*- coding: utf-8 -*-
"""
MOTOR MLB PRO - Con datos de prueba
"""

import numpy as np

def analizar_mlb_pro_v20(partido_data):
    """Analiza partido MLB con datos de prueba"""
    local = partido_data.get('home', partido_data.get('local', 'Local'))
    visitante = partido_data.get('away', partido_data.get('visitante', 'Visitante'))
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 8.5)
    
    # Datos de prueba
    equipos_fuertes = ["Dodgers", "Yankees", "Braves", "Astros", "Phillies"]
    equipos_debiles = ["Athletics", "Rockies", "Royals", "Pirates"]
    
    factor_local = 1.2 if local in equipos_fuertes else (0.8 if local in equipos_debiles else 1.0)
    factor_visit = 1.2 if visitante in equipos_fuertes else (0.8 if visitante in equipos_debiles else 1.0)
    
    base_local = 4.8
    base_visit = 4.5
    
    expected_local = base_local * factor_local
    expected_visit = base_visit * factor_visit
    total_proyectado = expected_local + expected_visit
    
    prob_over = 1 / (1 + np.exp(-(total_proyectado - linea_ou) / 2))
    
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
        'etiqueta_verde': confianza >= 70
    }
