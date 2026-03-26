# -*- coding: utf-8 -*-
"""
ANALIZADOR UFC HEURISTICO - Con datos reales de ufc.com
"""

import re

class AnalizadorUFCHuristico:
    def __init__(self, p1_data, p2_data):
        self.p1 = p1_data
        self.p2 = p2_data
    
    def _extraer_numero(self, valor):
        if valor is None:
            return 0
        if isinstance(valor, (int, float)):
            return valor
        if isinstance(valor, str):
            nums = re.findall(r'\d+', valor)
            return int(nums[0]) if nums else 0
        return 0
    
    def analizar(self):
        p1_nombre = self.p1.get('nombre', 'Peleador 1') if self.p1 else 'Peleador 1'
        p2_nombre = self.p2.get('nombre', 'Peleador 2') if self.p2 else 'Peleador 2'
        
        # Obtener datos REALES
        p1_ko = self.p1.get('ko_rate', 0.5) if self.p1 else 0.5
        p2_ko = self.p2.get('ko_rate', 0.5) if self.p2 else 0.5
        p1_grappling = self.p1.get('grappling', 0.5) if self.p1 else 0.5
        p2_grappling = self.p2.get('grappling', 0.5) if self.p2 else 0.5
        
        # Extraer alcance (manejo robusto)
        alcance1 = 0
        alcance2 = 0
        if self.p1 and self.p1.get('alcance'):
            alcance1 = self._extraer_numero(self.p1['alcance'])
            if alcance1 < 0:
                alcance1 = 0
        if self.p2 and self.p2.get('alcance'):
            alcance2 = self._extraer_numero(self.p2['alcance'])
            if alcance2 < 0:
                alcance2 = 0
        
        diff_alcance = alcance1 - alcance2
        diff_ko = p1_ko - p2_ko
        diff_grappling = p1_grappling - p2_grappling
        
        # Análisis jerarquico con datos validados
        if diff_alcance >= 5 and p1_ko > 0.6:
            ganador = p1_nombre
            confianza = 70 + min(15, diff_alcance)
            metodo = "KO/TKO"
            factor_clave = f"Ventaja alcance: +{diff_alcance} cm"
        elif diff_alcance <= -5 and p2_ko > 0.6:
            ganador = p2_nombre
            confianza = 70 + min(15, abs(diff_alcance))
            metodo = "KO/TKO"
            factor_clave = f"Ventaja alcance: +{abs(diff_alcance)} cm"
        elif diff_ko > 0.2:
            ganador = p1_nombre
            confianza = 65
            metodo = "KO/TKO" if diff_ko > 0.3 else "Decision"
            factor_clave = f"KO Rate superior: +{int(diff_ko*100)}%"
        elif diff_ko < -0.2:
            ganador = p2_nombre
            confianza = 65
            metodo = "KO/TKO" if abs(diff_ko) > 0.3 else "Decision"
            factor_clave = f"KO Rate superior: +{int(abs(diff_ko)*100)}%"
        elif diff_grappling > 0.2:
            ganador = p1_nombre
            confianza = 62
            metodo = "Sumision/Decision"
            factor_clave = f"Grappling superior: +{int(diff_grappling*100)}%"
        elif diff_grappling < -0.2:
            ganador = p2_nombre
            confianza = 62
            metodo = "Sumision/Decision"
            factor_clave = f"Grappling superior: +{int(abs(diff_grappling)*100)}%"
        else:
            ganador = p1_nombre if p1_ko > p2_ko else p2_nombre
            confianza = 55
            metodo = "Decision"
            factor_clave = "Combate parejo"
        
        confianza = min(85, max(40, confianza))
        etiqueta_verde = confianza >= 75
        
        return {
            'recomendacion': f"GANA {ganador} por {metodo}",
            'confianza': confianza,
            'metodo': metodo,
            'ganador': ganador,
            'etiqueta_verde': etiqueta_verde,
            'ventaja_alcance': diff_alcance,
            'factor_clave': factor_clave,
            'stats_p1': {
                'nombre': p1_nombre,
                'ko_rate': int(p1_ko * 100),
                'alcance': alcance1,
                'grappling': int(p1_grappling * 100)
            },
            'stats_p2': {
                'nombre': p2_nombre,
                'ko_rate': int(p2_ko * 100),
                'alcance': alcance2,
                'grappling': int(p2_grappling * 100)
            }
        }
    
    def obtener_resumen(self):
        return {
            'p1': self.p1.get('nombre') if self.p1 else 'N/A',
            'p2': self.p2.get('nombre') if self.p2 else 'N/A',
            'ko1': self.p1.get('ko_rate', 0) if self.p1 else 0,
            'ko2': self.p2.get('ko_rate', 0) if self.p2 else 0,
            'alcance1': self.p1.get('alcance', 'N/A') if self.p1 else 'N/A',
            'alcance2': self.p2.get('alcance', 'N/A') if self.p2 else 'N/A'
        }
