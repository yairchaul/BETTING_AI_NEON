# -*- coding: utf-8 -*-
"""
MOTOR MLB PRO - Versión final con datos reales de BD
"""

import numpy as np
from scipy.stats import poisson
import sqlite3
from datetime import datetime

class MotorMLBPro:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
    
    def obtener_ultimos_5(self, equipo):
        """Obtiene últimos 5 partidos REALES desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT puntos_favor, puntos_contra FROM historial_equipos 
                WHERE nombre_equipo = ? AND deporte = 'mlb' 
                ORDER BY fecha DESC LIMIT 5
            """, (equipo,))
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) >= 3:
                prom_favor = np.mean([r[0] for r in rows])
                prom_contra = np.mean([r[1] for r in rows])
                return {
                    'prom_favor': prom_favor,
                    'prom_contra': prom_contra,
                    'tiene_datos': True,
                    'partidos': len(rows)
                }
        except Exception as e:
            print(f"Error BD {equipo}: {e}")
        
        # Fallback conservador si no hay datos
        return {
            'prom_favor': 4.2,
            'prom_contra': 4.2,
            'tiene_datos': False,
            'partidos': 0
        }
    
    def analizar_partido(self, partido):
        """Analiza partido MLB con datos REALES de BD"""
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        linea_ou = partido.get('odds', {}).get('over_under', 8.5)
        
        stats_l = self.obtener_ultimos_5(local)
        stats_v = self.obtener_ultimos_5(visitante)
        
        # Proyección con datos reales
        expected_local = (stats_l['prom_favor'] * 0.55 + stats_v['prom_contra'] * 0.45) * 1.02
        expected_visit = (stats_v['prom_favor'] * 0.55 + stats_l['prom_contra'] * 0.45) * 1.02
        total_proyectado = expected_local + expected_visit
        
        # Simulación Monte Carlo
        np.random.seed(42)
        sim_local = poisson.rvs(expected_local, size=10000)
        sim_visit = poisson.rvs(expected_visit, size=10000)
        sim_total = sim_local + sim_visit
        
        prob_over = np.mean(sim_total > linea_ou)
        
        # Calcular confianza según datos disponibles
        if stats_l['tiene_datos'] and stats_v['tiene_datos']:
            confianza_base = 70
        elif stats_l['tiene_datos'] or stats_v['tiene_datos']:
            confianza_base = 60
        else:
            confianza_base = 45
        
        # Ajustar confianza según probabilidad
        if prob_over > 0.65 or prob_over < 0.35:
            confianza = min(85, confianza_base + 10)
        elif prob_over > 0.55 or prob_over < 0.45:
            confianza = confianza_base
        else:
            confianza = confianza_base - 10
        
        confianza = max(40, min(85, confianza))
        
        # Decisión
        if confianza >= 55:
            if prob_over > 0.55:
                recomendacion = f"OVER {linea_ou}"
                probabilidad = round(prob_over * 100, 1)
            elif prob_over < 0.45:
                recomendacion = f"UNDER {linea_ou}"
                probabilidad = round((1 - prob_over) * 100, 1)
            else:
                recomendacion = "SIN VALOR CLARO"
                probabilidad = 0
        else:
            recomendacion = "SIN VALOR CLARO - Datos insuficientes"
            probabilidad = 0
        
        resultado = {
            'recomendacion': recomendacion,
            'confianza': confianza,
            'probabilidad': probabilidad,
            'total_proyectado': round(total_proyectado, 1),
            'proyeccion_local': round(expected_local, 1),
            'proyeccion_visitante': round(expected_visit, 1),
            'etiqueta_verde': confianza >= 70 and probabilidad >= 60,
            'tiene_datos_reales': stats_l['tiene_datos'] and stats_v['tiene_datos']
        }
        
        # Gemini como decisor final
        try:
            import streamlit as st
            if hasattr(st.session_state, 'analizador_gemini') and st.session_state.analizador_gemini:
                decision = st.session_state.analizador_gemini.orquestrar_decision_final(
                    deporte="mlb", 
                    partido=partido, 
                    analisis_heuristico=resultado
                )
                resultado['gemini_decision'] = decision
        except:
            resultado['gemini_decision'] = None
        
        return resultado

def get_motor_mlb():
    return MotorMLBPro()
