# -*- coding: utf-8 -*-
"""
ANALIZADOR UFC MEJORADO - Con odds reales y altura en cm
"""

import re

class AnalizadorUFCMejorado:
    def __init__(self, p1_data, p2_data, odds_p1=None, odds_p2=None):
        self.p1 = p1_data
        self.p2 = p2_data
        self.odds_p1 = odds_p1
        self.odds_p2 = odds_p2
    
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
    
    def _calcular_valor_esperado(self, prob, cuota):
        """Calcula EV (Expected Value) basado en odds"""
        if not cuota:
            return 0
        try:
            # Convertir odds americanas a decimal
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
        """Analiza el combate con datos reales y odds"""
        
        p1_nombre = self.p1.get('nombre', 'Peleador 1') if self.p1 else 'Peleador 1'
        p2_nombre = self.p2.get('nombre', 'Peleador 2') if self.p2 else 'Peleador 2'
        
        # Obtener datos
        p1_ko = self.p1.get('ko_rate', 0.5) if self.p1 else 0.5
        p2_ko = self.p2.get('ko_rate', 0.5) if self.p2 else 0.5
        p1_grappling = self.p1.get('grappling', 0.5) if self.p1 else 0.5
        p2_grappling = self.p2.get('grappling', 0.5) if self.p2 else 0.5
        
        # Altura en cm (convertir si viene en pulgadas)
        altura1 = 0
        altura2 = 0
        if self.p1 and self.p1.get('altura'):
            altura_val = self._extraer_numero(self.p1['altura'])
            # Si es un número pequeño (menor de 100), son pulgadas, convertir a cm
            if altura_val < 100:
                altura1 = self._pulgadas_a_cm(altura_val)
            else:
                altura1 = int(altura_val)
        if self.p2 and self.p2.get('altura'):
            altura_val = self._extraer_numero(self.p2['altura'])
            if altura_val < 100:
                altura2 = self._pulgadas_a_cm(altura_val)
            else:
                altura2 = int(altura_val)
        
        # Alcance en cm
        alcance1 = 0
        alcance2 = 0
        if self.p1 and self.p1.get('alcance'):
            alcance_val = self._extraer_numero(self.p1['alcance'])
            if alcance_val < 100:
                alcance1 = self._pulgadas_a_cm(alcance_val)
            else:
                alcance1 = int(alcance_val)
        if self.p2 and self.p2.get('alcance'):
            alcance_val = self._extraer_numero(self.p2['alcance'])
            if alcance_val < 100:
                alcance2 = self._pulgadas_a_cm(alcance_val)
            else:
                alcance2 = int(alcance_val)
        
        diff_alcance = alcance1 - alcance2
        diff_ko = p1_ko - p2_ko
        diff_grappling = p1_grappling - p2_grappling
        
        # Calcular probabilidad base (sin odds)
        prob_base = 0.5
        
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
        else:
            prob_base = 0.52
            metodo = "Decision"
            factor_clave = "Combate parejo"
        
        # Ajustar con odds si están disponibles
        ev_p1 = 0
        ev_p2 = 0
        if self.odds_p1 and self.odds_p2:
            ev_p1 = self._calcular_valor_esperado(prob_base, self.odds_p1)
            ev_p2 = self._calcular_valor_esperado(1 - prob_base, self.odds_p2)
        
        # Decisión final (considerando odds)
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
            if prob_base > 0.55:
                ganador = p1_nombre
                confianza = int(prob_base * 100)
                probabilidad = prob_base
            elif prob_base < 0.45:
                ganador = p2_nombre
                confianza = int((1 - prob_base) * 100)
                probabilidad = 1 - prob_base
            else:
                ganador = p1_nombre if p1_ko > p2_ko else p2_nombre
                confianza = 55
                probabilidad = 0.55
        
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
                'alcance_cm': alcance1,
                'altura_cm': altura1,
                'grappling': int(p1_grappling * 100)
            },
            'stats_p2': {
                'nombre': p2_nombre,
                'ko_rate': int(p2_ko * 100),
                'alcance_cm': alcance2,
                'altura_cm': altura2,
                'grappling': int(p2_grappling * 100)
            }
        }
    
    def obtener_resumen(self):
        return {
            'p1': self.p1.get('nombre') if self.p1 else 'N/A',
            'p2': self.p2.get('nombre') if self.p2 else 'N/A',
            'ko1': self.p1.get('ko_rate', 0) if self.p1 else 0,
            'ko2': self.p2.get('ko_rate', 0) if self.p2 else 0,
            'odds_p1': self.odds_p1,
            'odds_p2': self.odds_p2
        }
