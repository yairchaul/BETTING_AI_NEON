# -*- coding: utf-8 -*-
"""
MOTOR UFC PRO - Análisis de combates UFC con datos reales de BD
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

class MotorUFCPro:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
    
    def obtener_datos_peleador(self, nombre):
        """Obtiene datos reales del peleador desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds
                FROM peleadores_ufc 
                WHERE nombre LIKE ? OR nombre = ?
                LIMIT 1
            """, (f"%{nombre}%", nombre))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'nombre': row[0],
                    'record': row[1] if row[1] else '0-0-0',
                    'altura': int(row[2]) if row[2] and str(row[2]).isdigit() else 175,
                    'alcance': int(row[4]) if row[4] and str(row[4]).isdigit() else 180,
                    'ko_rate': float(row[6]) if row[6] else 0.5,
                    'grappling': float(row[7]) if row[7] else 0.5,
                    'odds': row[8] if row[8] else 'N/A',
                    'tiene_datos': True
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo {nombre}: {e}")
            return None
    
    def analizar_combate(self, peleador1_nombre, peleador2_nombre):
        """Analiza combate UFC con datos reales"""
        
        # Obtener datos de ambos peleadores
        p1 = self.obtener_datos_peleador(peleador1_nombre)
        p2 = self.obtener_datos_peleador(peleador2_nombre)
        
        # Fallback si no hay datos
        if not p1:
            p1 = {'nombre': peleador1_nombre, 'ko_rate': 0.5, 'alcance': 180, 'grappling': 0.5, 'record': 'N/A', 'tiene_datos': False}
        if not p2:
            p2 = {'nombre': peleador2_nombre, 'ko_rate': 0.5, 'alcance': 180, 'grappling': 0.5, 'record': 'N/A', 'tiene_datos': False}
        
        # Calcular ventajas
        ventaja_alcance = p1['alcance'] - p2['alcance']
        ventaja_ko = p1['ko_rate'] - p2['ko_rate']
        ventaja_grappling = p1['grappling'] - p2['grappling']
        
        # Jerarquía de decisión
        if ventaja_alcance > 8 and p1['ko_rate'] > 0.6:
            ganador = p1['nombre']
            confianza = 70 + min(15, ventaja_alcance)
            metodo = "KO/TKO"
        elif ventaja_alcance < -8 and p2['ko_rate'] > 0.6:
            ganador = p2['nombre']
            confianza = 70 + min(15, abs(ventaja_alcance))
            metodo = "KO/TKO"
        elif ventaja_ko > 0.2:
            ganador = p1['nombre']
            confianza = 65 + int(ventaja_ko * 50)
            metodo = "KO/TKO" if ventaja_ko > 0.3 else "Decisión"
        elif ventaja_ko < -0.2:
            ganador = p2['nombre']
            confianza = 65 + int(abs(ventaja_ko) * 50)
            metodo = "KO/TKO" if abs(ventaja_ko) > 0.3 else "Decisión"
        elif ventaja_grappling > 0.2:
            ganador = p1['nombre']
            confianza = 60 + int(ventaja_grappling * 30)
            metodo = "Sumisión/Decisión"
        elif ventaja_grappling < -0.2:
            ganador = p2['nombre']
            confianza = 60 + int(abs(ventaja_grappling) * 30)
            metodo = "Sumisión/Decisión"
        else:
            ganador = p1['nombre'] if p1['ko_rate'] > p2['ko_rate'] else p2['nombre']
            confianza = 55
            metodo = "Decisión"
        
        confianza = min(85, max(40, confianza))
        
        # Probabilidad basada en confianza
        probabilidad = confianza
        
        return {
            'recomendacion': f"GANA {ganador.upper()} por {metodo}",
            'confianza': int(confianza),
            'probabilidad': int(probabilidad),
            'metodo': metodo,
            'ganador': ganador,
            'total_proyectado': round((p1['ko_rate'] + p2['ko_rate']) * 10, 1),
            'etiqueta_verde': confianza >= 70,
            'edge': round((confianza - 50) / 100, 2),
            'stats_p1': {
                'nombre': p1['nombre'],
                'record': p1.get('record', 'N/A'),
                'ko_rate': int(p1['ko_rate'] * 100),
                'alcance_cm': p1['alcance'],
                'grappling': int(p1['grappling'] * 100),
                'odds': p1.get('odds', 'N/A'),
                'tiene_datos': p1.get('tiene_datos', False)
            },
            'stats_p2': {
                'nombre': p2['nombre'],
                'record': p2.get('record', 'N/A'),
                'ko_rate': int(p2['ko_rate'] * 100),
                'alcance_cm': p2['alcance'],
                'grappling': int(p2['grappling'] * 100),
                'odds': p2.get('odds', 'N/A'),
                'tiene_datos': p2.get('tiene_datos', False)
            }
        }

def analizar_ufc_pro_v20(partido_data):
    """Función wrapper para compatibilidad con main"""
    motor = MotorUFCPro()
    p1 = partido_data.get('peleador1', '')
    p2 = partido_data.get('peleador2', '')
    return motor.analizar_combate(p1, p2)

def get_motor_ufc():
    return MotorUFCPro()
