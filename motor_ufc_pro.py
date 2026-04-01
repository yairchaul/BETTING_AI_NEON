# -*- coding: utf-8 -*-
"""
MOTOR UFC PRO - Análisis con datos de peleadores
"""

import numpy as np
import logging
from database_manager import db

logger = logging.getLogger(__name__)

def analizar_ufc_pro_v20(partido_data):
    """
    Analiza combate UFC con datos de peleadores
    
    Args:
        partido_data: dict con peleador1, peleador2
    
    Returns:
        dict con recomendacion, confianza, etc.
    """
    p1_nombre = partido_data.get('peleador1', '')
    p2_nombre = partido_data.get('peleador2', '')
    
    # Obtener datos de peleadores
    p1 = db.obtener_peleador_ufc(p1_nombre)
    p2 = db.obtener_peleador_ufc(p2_nombre)
    
    if not p1 or not p2:
        logger.warning(f"Datos insuficientes para {p1_nombre} vs {p2_nombre}")
        return {
            'recomendacion': 'DATOS INSUFICIENTES',
            'confianza': 40,
            'etiqueta_verde': False
        }
    
    # Extraer alcances
    try:
        alcance1 = float(p1.get('alcance', 0)) if p1.get('alcance') != 'N/A' else 0
        alcance2 = float(p2.get('alcance', 0)) if p2.get('alcance') != 'N/A' else 0
    except:
        alcance1 = alcance2 = 0
    
    # Convertir pulgadas a cm si es necesario
    if 50 <= alcance1 <= 95:
        alcance1 = alcance1 * 2.54
    if 50 <= alcance2 <= 95:
        alcance2 = alcance2 * 2.54
    
    # Extraer KO rates
    ko1 = p1.get('ko_rate', 0.5)
    ko2 = p2.get('ko_rate', 0.5)
    
    # Análisis
    diff_alcance = alcance1 - alcance2
    
    if diff_alcance >= 5 and ko1 > 0.6:
        ganador = p1.get('nombre')
        confianza = 70 + min(15, diff_alcance / 2)
        metodo = "KO/TKO"
    elif diff_alcance <= -5 and ko2 > 0.6:
        ganador = p2.get('nombre')
        confianza = 70 + min(15, abs(diff_alcance) / 2)
        metodo = "KO/TKO"
    elif ko1 > ko2 + 0.2:
        ganador = p1.get('nombre')
        confianza = 65
        metodo = "KO/TKO" if ko1 > 0.7 else "Decisión"
    elif ko2 > ko1 + 0.2:
        ganador = p2.get('nombre')
        confianza = 65
        metodo = "KO/TKO" if ko2 > 0.7 else "Decisión"
    else:
        ganador = p1.get('nombre') if ko1 > ko2 else p2.get('nombre')
        confianza = 55
        metodo = "Decisión"
    
    confianza = min(85, max(40, confianza))
    
    return {
        'recomendacion': f"GANA {ganador} por {metodo}",
        'confianza': int(confianza),
        'metodo': metodo,
        'ganador': ganador,
        'etiqueta_verde': confianza >= 70,
        'ventaja_alcance': round(diff_alcance, 1),
        'stats_p1': {
            'nombre': p1.get('nombre'),
            'ko_rate': int(ko1 * 100),
            'alcance_cm': int(alcance1)
        },
        'stats_p2': {
            'nombre': p2.get('nombre'),
            'ko_rate': int(ko2 * 100),
            'alcance_cm': int(alcance2)
        }
    }
