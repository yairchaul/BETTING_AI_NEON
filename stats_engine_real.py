"""
StatsEngine con datos REALES de API-Football
"""
import numpy as np
from api_client import FootballStatsAPI

class StatsEngineReal:
    """Motor de estadísticas con datos reales de equipos"""
    
    def __init__(self):
        self.api = FootballStatsAPI()
        self.cache = {}
    
    def calcular_futbol(self, evento):
        """
        Calcula probabilidades usando:
        - Stats REALES de cada equipo (vía API)
        - Historial de enfrentamientos
        - Cuotas actuales
        """
        # Obtener stats reales de los equipos
        stats_local = self.api.get_team_stats(evento['local'])
        stats_visit = self.api.get_team_stats(evento['visitante'])
        
        # Obtener historial
        h2h = self.api.get_head_to_head(evento['local'], evento['visitante'])
        
        # GF base de stats reales
        gf_local_base = stats_local['gf_local']
        gf_visit_base = stats_visit['gf_visitante']
        
        # Ajustar por odds (forma reciente)
        # A menor odds (favorito), mayor factor
        factor_local = 1 / evento['odds_local'] * 2.2
        factor_visit = 1 / evento['odds_visitante'] * 2.2
        
        gf_local = gf_local_base * factor_local
        gf_visit = gf_visit_base * factor_visit
        
        # Ajustar por historial si hay datos suficientes
        if h2h['total'] >= 3:
            factor_h2h = h2h['promedio_goles'] / (gf_local_base + gf_visit_base)
            gf_local *= np.sqrt(factor_h2h)
            gf_visit *= np.sqrt(factor_h2h)
        
        # Calcular Poisson
        probs = self._calcular_poisson(gf_local, gf_visit)
        
        # Agregar metadata
        probs['stats_local'] = stats_local
        probs['stats_visit'] = stats_visit
        probs['h2h'] = h2h
        probs['gf_local_real'] = gf_local
        probs['gf_visit_real'] = gf_visit
        
        return probs
    
    def _calcular_poisson(self, gf_local, gf_visit):
        """Cálculo exacto de Poisson"""
        max_goles = 6
        
        # Distribuciones
        dist_local = [np.exp(-gf_local) * (gf_local**i) / np.math.factorial(i) for i in range(max_goles + 1)]
        dist_visit = [np.exp(-gf_visit) * (gf_visit**j) / np.math.factorial(j) for j in range(max_goles + 1)]
        
        # Probabilidades 1X2
        prob_local = 0
        prob_empate = 0
        prob_visit = 0
        
        for i in range(max_goles + 1):
            for j in range(max_goles + 1):
                prob = dist_local[i] * dist_visit[j]
                if i > j:
                    prob_local += prob
                elif i == j:
                    prob_empate += prob
                else:
                    prob_visit += prob
        
        # Overs
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
        
        return {
            'prob_local': prob_local,
            'prob_empate': prob_empate,
            'prob_visit': prob_visit,
            'over_1_5': over_15,
            'over_2_5': over_25,
            'over_3_5': over_35,
            'btts_si': btts_si,
            'btts_no': 1 - btts_si
        }
