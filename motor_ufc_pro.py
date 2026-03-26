# -*- coding: utf-8 -*-
"""
MOTOR UFC PRO - Análisis de combates UFC con datos reales
"""

import numpy as np
import sqlite3

class MotorUFCPro:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
    
    def obtener_datos_peleador(self, nombre):
        """Obtiene datos reales del peleador desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling
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
                    'altura': int(row[2]) if row[2] and str(row[2]).isdigit() else 170,
                    'alcance': int(row[4]) if row[4] and str(row[4]).isdigit() else 170,
                    'ko_rate': float(row[6]) if row[6] else 0.5,
                    'grappling': float(row[7]) if row[7] else 0.5,
                    'tiene_datos': True
                }
            return None
        except Exception as e:
            print(f"Error obteniendo {nombre}: {e}")
            return None
    
    def analizar_combate(self, peleador1_nombre, peleador2_nombre):
        """Analiza combate UFC con datos reales"""
        
        # Obtener datos de ambos peleadores
        p1 = self.obtener_datos_peleador(peleador1_nombre)
        p2 = self.obtener_datos_peleador(peleador2_nombre)
        
        if not p1 or not p2:
            return {
                'recomendacion': 'DATOS INSUFICIENTES',
                'confianza': 40,
                'etiqueta_verde': False,
                'gemini_decision': 'No hay datos suficientes de los peleadores'
            }
        
        # Calcular ventajas
        ventaja_alcance = p1['alcance'] - p2['alcance']
        ventaja_ko = p1['ko_rate'] - p2['ko_rate']
        
        # Decisión basada en datos
        if ventaja_alcance > 5 and p1['ko_rate'] > 0.6:
            ganador = p1['nombre']
            confianza = 70 + min(15, ventaja_alcance)
            metodo = "KO/TKO"
        elif ventaja_alcance < -5 and p2['ko_rate'] > 0.6:
            ganador = p2['nombre']
            confianza = 70 + min(15, abs(ventaja_alcance))
            metodo = "KO/TKO"
        elif ventaja_ko > 0.2:
            ganador = p1['nombre'] if ventaja_ko > 0 else p2['nombre']
            confianza = 65
            metodo = "KO/TKO" if abs(ventaja_ko) > 0.3 else "Decisión"
        elif p1['grappling'] > p2['grappling'] + 0.2:
            ganador = p1['nombre']
            confianza = 65
            metodo = "Sumisión/Decisión"
        elif p2['grappling'] > p1['grappling'] + 0.2:
            ganador = p2['nombre']
            confianza = 65
            metodo = "Sumisión/Decisión"
        else:
            ganador = p1['nombre'] if p1['ko_rate'] > p2['ko_rate'] else p2['nombre']
            confianza = 55
            metodo = "Decisión"
        
        confianza = min(85, confianza)
        
        resultado = {
            'recomendacion': f"GANA {ganador} por {metodo}",
            'confianza': confianza,
            'metodo': metodo,
            'ganador': ganador,
            'etiqueta_verde': confianza >= 75,
            'stats_p1': {
                'ko_rate': int(p1['ko_rate'] * 100),
                'alcance': p1['alcance'],
                'grappling': int(p1['grappling'] * 100)
            },
            'stats_p2': {
                'ko_rate': int(p2['ko_rate'] * 100),
                'alcance': p2['alcance'],
                'grappling': int(p2['grappling'] * 100)
            }
        }
        
        return resultado

def get_motor_ufc():
    return MotorUFCPro()
