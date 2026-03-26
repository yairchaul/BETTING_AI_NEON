# -*- coding: utf-8 -*-
"""
ANALIZADOR UFC FINAL - Con odds reales y EV como factor decisivo
Integra datos de peleadores + odds de Action Network
"""

import sqlite3
import json
import re

class AnalizadorUFCFinal:
    def __init__(self, p1_nombre, p2_nombre, db_path="data/betting_stats.db"):
        self.p1_nombre = p1_nombre
        self.p2_nombre = p2_nombre
        self.db_path = db_path
        self.p1_data = self._obtener_peleador(p1_nombre)
        self.p2_data = self._obtener_peleador(p2_nombre)
        self.odds_p1 = self.p1_data.get('odds', 'N/A') if self.p1_data else 'N/A'
        self.odds_p2 = self.p2_data.get('odds', 'N/A') if self.p2_data else 'N/A'
    
    def _obtener_peleador(self, nombre):
        """Obtiene datos del peleador desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
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
                    'altura': row[2] if row[2] else 'N/A',
                    'peso': row[3] if row[3] else 'N/A',
                    'alcance': row[4] if row[4] else 'N/A',
                    'postura': row[5] if row[5] else 'Desconocida',
                    'ko_rate': float(row[6]) if row[6] else 0.5,
                    'grappling': float(row[7]) if row[7] else 0.5,
                    'odds': row[8] if row[8] else 'N/A'
                }
            return None
        except Exception as e:
            print(f"Error obteniendo {nombre}: {e}")
            return None
    
    def _pulgadas_a_cm(self, pulgadas):
        """Convierte pulgadas a cm"""
        try:
            return int(float(pulgadas) * 2.54)
        except:
            return 0
    
    def _extraer_numero(self, valor):
        if valor is None:
            return 0
        if isinstance(valor, (int, float)):
            return valor
        if isinstance(valor, str):
            nums = re.findall(r'\d+\.?\d*', valor)
            return float(nums[0]) if nums else 0
        return 0
    
    def _odd_a_decimal(self, odd):
        """Convierte odds americanos a decimal"""
        if not odd or odd == 'N/A':
            return None
        odd_str = str(odd)
        if odd_str.startswith('+'):
            return 1 + (float(odd_str[1:]) / 100)
        elif odd_str.startswith('-'):
            return 1 + (100 / float(odd_str[1:]))
        return float(odd_str)
    
    def _calcular_valor_esperado(self, prob, odd):
        """Calcula EV (Expected Value)"""
        cuota_dec = self._odd_a_decimal(odd)
        if cuota_dec is None:
            return 0
        ev = (prob * cuota_dec) - 1
        return round(ev * 100, 1)
    
    def analizar(self):
        """Analiza combate con datos reales y odds como factor decisivo"""
        
        if not self.p1_data or not self.p2_data:
            return {
                'recomendacion': 'DATOS INSUFICIENTES',
                'confianza': 40,
                'probabilidad': 0,
                'metodo': 'N/A',
                'etiqueta_verde': False,
                'factor_clave': 'No hay datos suficientes'
            }
        
        p1_nombre = self.p1_data['nombre']
        p2_nombre = self.p2_data['nombre']
        
        # Datos de peleadores
        p1_ko = self.p1_data.get('ko_rate', 0.5)
        p2_ko = self.p2_data.get('ko_rate', 0.5)
        p1_grappling = self.p1_data.get('grappling', 0.5)
        p2_grappling = self.p2_data.get('grappling', 0.5)
        
        # Altura en cm
        altura1 = self._extraer_numero(self.p1_data.get('altura', '0'))
        if altura1 < 100:  # Si es pulgadas
            altura1 = self._pulgadas_a_cm(altura1)
        altura2 = self._extraer_numero(self.p2_data.get('altura', '0'))
        if altura2 < 100:
            altura2 = self._pulgadas_a_cm(altura2)
        
        # Alcance en cm
        alcance1 = self._extraer_numero(self.p1_data.get('alcance', '0'))
        if alcance1 < 100:
            alcance1 = self._pulgadas_a_cm(alcance1)
        alcance2 = self._extraer_numero(self.p2_data.get('alcance', '0'))
        if alcance2 < 100:
            alcance2 = self._pulgadas_a_cm(alcance2)
        
        # Calcular probabilidad base (sin odds)
        diff_alcance = alcance1 - alcance2
        diff_ko = p1_ko - p2_ko
        diff_grappling = p1_grappling - p2_grappling
        
        prob_base = 0.5
        factor_clave = "Combate parejo"
        metodo = "Decision"
        
        # Jerarquía de factores
        if diff_alcance >= 5 and p1_ko > 0.6:
            prob_base = 0.65 + min(0.15, diff_alcance / 100)
            metodo = "KO/TKO"
            factor_clave = f"Ventaja alcance: +{diff_alcance}cm"
        elif diff_alcance <= -5 and p2_ko > 0.6:
            prob_base = 0.65 + min(0.15, abs(diff_alcance) / 100)
            metodo = "KO/TKO"
            factor_clave = f"Ventaja alcance: +{abs(diff_alcance)}cm"
        elif diff_ko > 0.2:
            prob_base = 0.60 + min(0.15, diff_ko)
            metodo = "KO/TKO" if diff_ko > 0.3 else "Decision"
            factor_clave = f"KO Rate superior: +{int(diff_ko*100)}%"
        elif diff_ko < -0.2:
            prob_base = 0.60 + min(0.15, abs(diff_ko))
            metodo = "KO/TKO" if abs(diff_ko) > 0.3 else "Decision"
            factor_clave = f"KO Rate superior: +{int(abs(diff_ko)*100)}%"
        elif diff_grappling > 0.2:
            prob_base = 0.55 + min(0.10, diff_grappling)
            metodo = "Sumision/Decision"
            factor_clave = f"Grappling superior: +{int(diff_grappling*100)}%"
        elif diff_grappling < -0.2:
            prob_base = 0.55 + min(0.10, abs(diff_grappling))
            metodo = "Sumision/Decision"
            factor_clave = f"Grappling superior: +{int(abs(diff_grappling)*100)}%"
        
        # Calcular EV con odds reales
        ev_p1 = self._calcular_valor_esperado(prob_base, self.odds_p1)
        ev_p2 = self._calcular_valor_esperado(1 - prob_base, self.odds_p2)
        
        # DECISIÓN FINAL: BASADA EN EV (Expected Value)
        if ev_p1 > 5 and ev_p1 > ev_p2:
            ganador = p1_nombre
            probabilidad = prob_base
            confianza = min(85, int(50 + ev_p1 * 2))
            ev_usado = ev_p1
            factor_adicional = f"EV positivo: +{ev_p1}%"
        elif ev_p2 > 5 and ev_p2 > ev_p1:
            ganador = p2_nombre
            probabilidad = 1 - prob_base
            confianza = min(85, int(50 + ev_p2 * 2))
            ev_usado = ev_p2
            factor_adicional = f"EV positivo: +{ev_p2}%"
        else:
            # Sin EV claro, usar probabilidad base
            if prob_base > 0.55:
                ganador = p1_nombre
                probabilidad = prob_base
                confianza = int(prob_base * 100)
                ev_usado = ev_p1
                factor_adicional = f"Sin EV claro (EV: {ev_p1}% / {ev_p2}%)"
            elif prob_base < 0.45:
                ganador = p2_nombre
                probabilidad = 1 - prob_base
                confianza = int((1 - prob_base) * 100)
                ev_usado = ev_p2
                factor_adicional = f"Sin EV claro (EV: {ev_p1}% / {ev_p2}%)"
            else:
                # Empate, decidir por odds del mercado
                if self.odds_p1 != 'N/A' and self.odds_p2 != 'N/A':
                    # El favorito (odd más bajo) es más probable
                    odd1_num = abs(float(self.odds_p1))
                    odd2_num = abs(float(self.odds_p2))
                    if odd1_num < odd2_num:
                        ganador = p1_nombre
                        probabilidad = 0.55
                        confianza = 55
                    else:
                        ganador = p2_nombre
                        probabilidad = 0.55
                        confianza = 55
                    factor_adicional = f"Favorito por odds ({self.odds_p1} vs {self.odds_p2})"
                else:
                    ganador = p1_nombre if p1_ko > p2_ko else p2_nombre
                    probabilidad = 0.52
                    confianza = 52
                    factor_adicional = "Combate parejo sin EV"
        
        confianza = min(85, max(40, confianza))
        etiqueta_verde = confianza >= 70 and (ev_p1 > 5 or ev_p2 > 5)
        
        return {
            'recomendacion': f"GANA {ganador} por {metodo}",
            'confianza': confianza,
            'probabilidad': round(probabilidad * 100, 1),
            'metodo': metodo,
            'ganador': ganador,
            'etiqueta_verde': etiqueta_verde,
            'factor_clave': factor_clave,
            'factor_adicional': factor_adicional,
            'ev_p1': ev_p1,
            'ev_p2': ev_p2,
            'odds_p1': self.odds_p1,
            'odds_p2': self.odds_p2,
            'stats_p1': {
                'nombre': p1_nombre,
                'record': self.p1_data.get('record', 'N/A'),
                'ko_rate': int(p1_ko * 100),
                'altura_cm': altura1,
                'alcance_cm': alcance1,
                'grappling': int(p1_grappling * 100),
                'odds': self.odds_p1
            },
            'stats_p2': {
                'nombre': p2_nombre,
                'record': self.p2_data.get('record', 'N/A'),
                'ko_rate': int(p2_ko * 100),
                'altura_cm': altura2,
                'alcance_cm': alcance2,
                'grappling': int(p2_grappling * 100),
                'odds': self.odds_p2
            }
        }

def obtener_analisis_ufc(p1_nombre, p2_nombre):
    """Función rápida para obtener análisis de combate UFC"""
    analizador = AnalizadorUFCFinal(p1_nombre, p2_nombre)
    return analizador.analizar()
