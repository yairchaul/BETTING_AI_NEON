# -*- coding: utf-8 -*-
"""
MOTOR UFC PRO - Con datos de prueba
"""

import numpy as np

def analizar_ufc_pro_v20(partido_data):
    """Analiza combate UFC con datos de prueba"""
    p1_nombre = partido_data.get('peleador1', 'Peleador 1')
    p2_nombre = partido_data.get('peleador2', 'Peleador 2')
    
    # Datos de prueba basados en nombres conocidos
    peleadores_fuertes = ["Adesanya", "Grasso", "Brasil", "Simon", "Stirling"]
    
    factor_p1 = 1.3 if any(f in p1_nombre for f in peleadores_fuertes) else 1.0
    factor_p2 = 1.3 if any(f in p2_nombre for f in peleadores_fuertes) else 1.0
    
    # Calcular ventajas
    if factor_p1 > factor_p2:
        ganador = p1_nombre
        confianza = 65 + (factor_p1 - factor_p2) * 20
        metodo = "KO/TKO" if factor_p1 > 1.2 else "Decisión"
    elif factor_p2 > factor_p1:
        ganador = p2_nombre
        confianza = 65 + (factor_p2 - factor_p1) * 20
        metodo = "KO/TKO" if factor_p2 > 1.2 else "Decisión"
    else:
        ganador = p1_nombre
        confianza = 55
        metodo = "Decisión"
    
    confianza = min(85, max(40, confianza))
    
    return {
        'recomendacion': f"GANA {ganador} por {metodo}",
        'confianza': int(confianza),
        'metodo': metodo,
        'ganador': ganador,
        'etiqueta_verde': confianza >= 70,
        'stats_p1': {'nombre': p1_nombre, 'ko_rate': 50, 'alcance_cm': 180},
        'stats_p2': {'nombre': p2_nombre, 'ko_rate': 50, 'alcance_cm': 180}
    }
