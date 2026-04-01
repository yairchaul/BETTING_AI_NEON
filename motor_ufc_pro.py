# -*- coding: utf-8 -*-
"""
MOTOR UFC PRO - Con fuerza base por peleador desde BD y análisis de odds
"""

import sqlite3
import logging
import numpy as np

logger = logging.getLogger(__name__)


def obtener_peleador_desde_bd(nombre):
    """Obtiene datos de un peleador desde la BD"""
    try:
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds
            FROM peleadores_ufc 
            WHERE nombre LIKE ? OR nombre = ?
            LIMIT 1
        ''', (f"%{nombre}%", nombre))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'nombre': row[0],
                'record': row[1] if row[1] else '0-0-0',
                'altura': int(row[2]) if row[2] else 175,
                'peso': row[3] if row[3] else 'N/A',
                'alcance': int(row[4]) if row[4] else 180,
                'postura': row[5] if row[5] else 'N/A',
                'ko_rate': row[6] if row[6] else 0.5,
                'grappling': row[7] if row[7] else 0.5,
                'odds': row[8] if row[8] else 'N/A'
            }
        return None
    except Exception as e:
        logger.error(f"Error obteniendo {nombre}: {e}")
        return None


def analizar_ufc_pro_v20(partido_data):
    """
    Analiza combate UFC con datos de BD o fallback
    Retorna estructura compatible con render_analisis_card
    """
    p1_nombre = partido_data.get('peleador1', 'Peleador 1')
    p2_nombre = partido_data.get('peleador2', 'Peleador 2')
    
    # Intentar obtener datos de BD
    p1 = obtener_peleador_desde_bd(p1_nombre)
    p2 = obtener_peleador_desde_bd(p2_nombre)
    
    # Fallback si no hay datos en BD
    if not p1:
        p1 = {
            'nombre': p1_nombre, 
            'ko_rate': 0.5, 
            'alcance': 180, 
            'grappling': 0.5,
            'record': 'N/A',
            'odds': 'N/A'
        }
    if not p2:
        p2 = {
            'nombre': p2_nombre, 
            'ko_rate': 0.5, 
            'alcance': 180, 
            'grappling': 0.5,
            'record': 'N/A',
            'odds': 'N/A'
        }
    
    # Calcular ventajas
    diff_alcance = p1['alcance'] - p2['alcance']
    diff_ko = p1['ko_rate'] - p2['ko_rate']
    diff_grappling = p1['grappling'] - p2['grappling']
    
    # Probabilidad de KO
    prob_ko = 0.3 + (abs(diff_ko) * 0.3)
    prob_ko = min(0.8, max(0.1, prob_ko))
    
    # Jerarquía de decisión
    if diff_alcance > 8 and p1['ko_rate'] > 0.6:
        ganador = p1['nombre']
        confianza = 70 + min(15, diff_alcance // 2)
        metodo = "KO/TKO"
        probabilidad = 65 + diff_ko * 20
    elif diff_alcance < -8 and p2['ko_rate'] > 0.6:
        ganador = p2['nombre']
        confianza = 70 + min(15, abs(diff_alcance) // 2)
        metodo = "KO/TKO"
        probabilidad = 65 + abs(diff_ko) * 20
    elif diff_ko > 0.2:
        ganador = p1['nombre']
        confianza = 65 + int(diff_ko * 50)
        metodo = "KO/TKO" if diff_ko > 0.3 else "Decisión"
        probabilidad = 60 + diff_ko * 30
    elif diff_ko < -0.2:
        ganador = p2['nombre']
        confianza = 65 + int(abs(diff_ko) * 50)
        metodo = "KO/TKO" if abs(diff_ko) > 0.3 else "Decisión"
        probabilidad = 60 + abs(diff_ko) * 30
    elif diff_grappling > 0.2:
        ganador = p1['nombre']
        confianza = 60 + int(diff_grappling * 30)
        metodo = "Sumisión/Decisión"
        probabilidad = 55 + diff_grappling * 25
    elif diff_grappling < -0.2:
        ganador = p2['nombre']
        confianza = 60 + int(abs(diff_grappling) * 30)
        metodo = "Sumisión/Decisión"
        probabilidad = 55 + abs(diff_grappling) * 25
    else:
        # Empate técnico, favorecer al que tiene mejor KO rate
        ganador = p1['nombre'] if p1['ko_rate'] > p2['ko_rate'] else p2['nombre']
        confianza = 55
        metodo = "Decisión"
        probabilidad = 52
    
    confianza = min(85, max(40, confianza))
    probabilidad = min(85, max(35, probabilidad))
    
    # Edge = confianza vs 50% base
    edge = round((probabilidad - 50) / 100, 2)
    
    return {
        'recomendacion': f"GANA {ganador.upper()} por {metodo}",
        'confianza': int(confianza),
        'probabilidad': int(probabilidad),
        'metodo': metodo,
        'ganador': ganador,
        'total_proyectado': p1['ko_rate'] + p2['ko_rate'],  # Métrica alternativa
        'etiqueta_verde': confianza >= 65,
        'edge': edge,
        'stats_p1': {
            'nombre': p1['nombre'], 
            'ko_rate': int(p1['ko_rate'] * 100), 
            'alcance_cm': p1['alcance'],
            'record': p1.get('record', 'N/A'),
            'odds': p1.get('odds', 'N/A')
        },
        'stats_p2': {
            'nombre': p2['nombre'], 
            'ko_rate': int(p2['ko_rate'] * 100), 
            'alcance_cm': p2['alcance'],
            'record': p2.get('record', 'N/A'),
            'odds': p2.get('odds', 'N/A')
        }
    }
