"""
ANALIZADOR FÚTBOL MEJORADO - Con datos mock mientras se llena BD
"""

import numpy as np
from scipy.stats import poisson
from selector_mejor_opcion_jerarquico import SelectorMejorOpcionJerarquico

class AnalizadorFutbolHeuristicoMejorado:
    def __init__(self, stats_local, stats_visit, nombre_local, nombre_visit, db_path='data/betting_stats.db'):
        self.stats_local = stats_local or {}
        self.stats_visit = stats_visit or {}
        self.local = nombre_local
        self.visitante = nombre_visit
        self.db_path = db_path
    
    def _obtener_goles_mock(self, equipo):
        """Genera datos mock basados en fuerza percibida del equipo"""
        equipos_fuertes = ["Manchester", "Liverpool", "Arsenal", "Chelsea", "Barcelona", "Real Madrid", "Bayern", "PSG"]
        equipos_medios = ["Aston Villa", "Newcastle", "Tottenham", "Atletico", "Milan", "Inter", "Juventus"]
        
        if any(fuerte in equipo for fuerte in equipos_fuertes):
            return [2, 3, 2, 1, 3], [1, 0, 1, 2, 1]  # goles a favor, goles en contra
        elif any(medio in equipo for medio in equipos_medios):
            return [1, 2, 1, 1, 2], [1, 1, 2, 1, 1]
        else:
            return [1, 0, 1, 1, 0], [2, 1, 2, 1, 2]
    
    def analizar(self):
        """Analiza partido con Poisson + Monte Carlo usando datos mock"""
        
        # Generar datos mock
        goles_local_favor, goles_local_contra = self._obtener_goles_mock(self.local)
        goles_visit_favor, goles_visit_contra = self._obtener_goles_mock(self.visitante)
        
        prom_local = np.mean(goles_local_favor)
        prom_visit = np.mean(goles_visit_favor)
        def_local = np.mean(goles_local_contra)
        def_visit = np.mean(goles_visit_contra)
        
        # Proyección ataque vs defensa
        lambda_local = (prom_local * 0.6 + def_visit * 0.4) * 1.02
        lambda_visit = (prom_visit * 0.6 + def_local * 0.4) * 1.02
        
        # Simulación Monte Carlo
        np.random.seed(42)
        sim_local = poisson.rvs(lambda_local, size=10000)
        sim_visit = poisson.rvs(lambda_visit, size=10000)
        sim_total = sim_local + sim_visit
        
        # Probabilidades
        probs = {
            'over_1.5_pt': np.mean(sim_local > 0.75),
            'over_3.5': np.mean(sim_total > 3.5),
            'btts': np.mean((sim_local > 0) & (sim_visit > 0)),
            'over_1.5': np.mean(sim_total > 1.5),
            'over_2.5': np.mean(sim_total > 2.5),
            'local': np.mean(sim_local > sim_visit),
            'visitante': np.mean(sim_visit > sim_local),
            'combo': np.mean((sim_local > sim_visit) & (sim_total > 2.5))
        }
        
        # Usar selector jerárquico
        selector = SelectorMejorOpcionJerarquico()
        resultado = selector.seleccionar(probs, deporte="futbol", equipos=(self.local, self.visitante))
        
        # Agregar datos adicionales
        resultado['total_proyectado'] = round(np.mean(sim_total), 1)
        resultado['proyeccion'] = f"{round(np.mean(sim_local), 1)} - {round(np.mean(sim_visit), 1)}"
        resultado['tipo'] = resultado.get('tipo', 'FÚTBOL')
        
        return resultado
    
    def obtener_resumen(self):
        return {
            'local': self.local,
            'visitante': self.visitante
        }
