# -*- coding: utf-8 -*-
"""
ANALIZADOR UFC CON ODDS - Integra odds de Action Network
"""

import sqlite3
import json

class AnalizadorUFCOdds:
    def __init__(self, p1_data, p2_data):
        self.p1 = p1_data
        self.p2 = p2_data
        self.odds_p1 = p1_data.get('odds', 'N/A') if p1_data else 'N/A'
        self.odds_p2 = p2_data.get('odds', 'N/A') if p2_data else 'N/A'
    
    def _pulgadas_a_cm(self, pulgadas):
        try:
            return int(float(pulgadas) * 2.54)
        except:
            return 0
    
    def _calcular_valor_esperado(self, prob, cuota):
        """Calcula EV (Expected Value) basado en odds"""
        if not cuota or cuota == 'N/A':
            return 0
        try:
            cuota_str = str(cuota)
            if cuota_str.startswith('+'):
                cuota_dec = 1 + (float(cuota_str[1:]) / 100)
            elif cuota_str.startswith('-'):
                cuota_dec = 1 + (100 / float(cuota_str[1:]))
            else:
                cuota_dec = float(cuota_str)
            ev = (prob * cuota_dec) - 1
            return round(ev * 100, 1)
        except:
            return 0
    
    def analizar(self):
        """Analiza combate con datos reales y odds"""
        
        p1_nombre = self.p1.get('nombre', 'Peleador 1') if self.p1 else 'Peleador 1'
        p2_nombre = self.p2.get('nombre', 'Peleador 2') if self.p2 else 'Peleador 2'
        
        # Datos de peleadores
        p1_ko = self.p1.get('ko_rate', 0.5) if self.p1 else 0.5
        p2_ko = self.p2.get('ko_rate', 0.5) if self.p2 else 0.5
        
        # Altura en cm
        altura1 = 0
        altura2 = 0
        if self.p1 and self.p1.get('altura'):
            try:
                altura1 = self._pulgadas_a_cm(float(self.p1['altura']))
            except:
                pass
        if self.p2 and self.p2.get('altura'):
            try:
                altura2 = self._pulgadas_a_cm(float(self.p2['altura']))
            except:
                pass
        
        # Alcance en cm
        alcance1 = 0
        alcance2 = 0
        if self.p1 and self.p1.get('alcance'):
            try:
                alcance1 = self._pulgadas_a_cm(float(self.p1['alcance']))
            except:
                pass
        if self.p2 and self.p2.get('alcance'):
            try:
                alcance2 = self._pulgadas_a_cm(float(self.p2['alcance']))
            except:
                pass
        
        # Calcular probabilidad base
        diff_ko = p1_ko - p2_ko
        diff_alcance = alcance1 - alcance2
        
        prob_base = 0.5
        factor_clave = "Combate parejo"
        metodo = "Decision"
        
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
        
        # Calcular EV con odds
        ev_p1 = self._calcular_valor_esperado(prob_base, self.odds_p1)
        ev_p2 = self._calcular_valor_esperado(1 - prob_base, self.odds_p2)
        
        # Decisión basada en EV
        if ev_p1 > 5 and ev_p1 > ev_p2:
            ganador = p1_nombre
            confianza = min(85, int(50 + ev_p1 * 2))
            probabilidad = prob_base
        elif ev_p2 > 5 and ev_p2 > ev_p1:
            ganador = p2_nombre
            confianza = min(85, int(50 + ev_p2 * 2))
            probabilidad = 1 - prob_base
        else:
            # Sin valor claro, usar probabilidad base
            ganador = p1_nombre if prob_base > 0.55 else p2_nombre
            confianza = int(max(prob_base, 1-prob_base) * 100)
            probabilidad = max(prob_base, 1-prob_base)
        
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
            'ev_p1': ev_p1,
            'ev_p2': ev_p2,
            'odds_p1': self.odds_p1,
            'odds_p2': self.odds_p2,
            'stats_p1': {
                'nombre': p1_nombre,
                'ko_rate': int(p1_ko * 100),
                'altura_cm': altura1,
                'alcance_cm': alcance1
            },
            'stats_p2': {
                'nombre': p2_nombre,
                'ko_rate': int(p2_ko * 100),
                'altura_cm': altura2,
                'alcance_cm': alcance2
            }
        }
