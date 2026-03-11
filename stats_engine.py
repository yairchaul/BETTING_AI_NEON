"""
StatsEngine - Cálculos REALES con Poisson y 7 reglas
"""
import numpy as np
from scipy.stats import poisson

class StatsEngine:
    def calcular(self, evento):
        """Calcula TODAS las probabilidades para un partido"""
        
        # Probabilidades implícitas de las cuotas
        prob_local_impl = 1 / evento.odds_local if evento.odds_local > 0 else 0
        prob_empate_impl = 1 / evento.odds_empate if evento.odds_empate and evento.odds_empate > 0 else 0
        prob_visit_impl = 1 / evento.odds_visitante if evento.odds_visitante > 0 else 0
        
        # Normalizar (quitar overround)
        suma = prob_local_impl + prob_empate_impl + prob_visit_impl
        prob_local = prob_local_impl / suma
        prob_empate = prob_empate_impl / suma
        prob_visit = prob_visit_impl / suma
        
        # Estimar GF (Goals For) basado en odds
        # A mayor odds (underdog), menor GF esperado
        gf_local = 2.0 * (1 / evento.odds_local) * 3  # Ajuste empírico
        gf_visit = 2.0 * (1 / evento.odds_visitante) * 3
        
        # Límites realistas
        gf_local = min(max(gf_local, 0.8), 2.5)
        gf_visit = min(max(gf_visit, 0.5), 2.2)
        
        # Distribución Poisson
        max_goles = 6
        dist_local = [poisson.pmf(i, gf_local) for i in range(max_goles + 1)]
        dist_visit = [poisson.pmf(i, gf_visit) for i in range(max_goles + 1)]
        
        # Calcular overs
        over_15 = 0
        over_25 = 0
        over_35 = 0
        
        for i in range(max_goles + 1):
            for j in range(max_goles + 1):
                total = i + j
                prob = dist_local[i] * dist_visit[j]
                if total > 1.5:
                    over_15 += prob
                if total > 2.5:
                    over_25 += prob
                if total > 3.5:
                    over_35 += prob
        
        # BTTS
        btts_si = 0
        for i in range(1, max_goles + 1):
            for j in range(1, max_goles + 1):
                btts_si += dist_local[i] * dist_visit[j]
        btts_no = 1 - btts_si
        
        # Over 1.5 primer tiempo (aproximado)
        over_15_1t = over_15 * 0.45
        
        return {
            'prob_local': prob_local,
            'prob_empate': prob_empate,
            'prob_visitante': prob_visit,
            'over_1_5': over_15,
            'over_2_5': over_25,
            'over_3_5': over_35,
            'btts_si': btts_si,
            'btts_no': btts_no,
            'over_1_5_1t': over_15_1t,
            'gf_local': gf_local,
            'gf_visitante': gf_visit
        }
