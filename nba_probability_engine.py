"""
Motor de probabilidades para NBA - Jerarquía de 3 niveles
"""
import math

class NBAProbabilityEngine:
    """
    Calcula probabilidades para NBA con jerarquía:
    Nivel 1: Handicap (Spread)
    Nivel 2: Totals (Over/Under)
    Nivel 3: Moneyline
    """
    
    def analizar_partido(self, partido):
        odds = partido['odds']
        
        # ========================================
        # NIVEL 1: HANDICAP (SPREAD)
        # ========================================
        recomendaciones = []
        
        if 'spreads' in odds:
            spread_local = odds['spreads'][partido['local']]
            spread_visit = odds['spreads'][partido['visitante']]
            
            # Probabilidad de cubrir spread (modelo basado en moneyline)
            ml_local = odds['h2h'][partido['local']]
            ml_visit = odds['h2h'][partido['visitante']]
            
            prob_local_ml = 1/ml_local
            prob_visit_ml = 1/ml_visit
            total_ml = prob_local_ml + prob_visit_ml
            prob_local_ml = prob_local_ml / total_ml
            prob_visit_ml = prob_visit_ml / total_ml
            
            # Ajuste para spread
            if spread_local['point'] < 0:  # Favorito
                prob_spread_local = prob_local_ml * 0.95
                prob_spread_visit = 1 - prob_spread_local
            else:  # Underdog
                prob_spread_local = prob_local_ml * 1.05
                prob_spread_visit = 1 - prob_spread_local
            
            prob_spread_local = min(max(prob_spread_local, 0.3), 0.7)
            prob_spread_visit = 1 - prob_spread_local
            
            # Value para spreads
            value_local = (prob_spread_local * spread_local['price']) - 1
            value_visit = (prob_spread_visit * spread_visit['price']) - 1
            
            if value_local > 0.02:
                recomendaciones.append({
                    'nivel': 1,
                    'tipo': 'spread',
                    'desc': f"{partido['local']} {spread_local['point']:+g}",
                    'probabilidad': prob_spread_local,
                    'cuota': spread_local['price'],
                    'value': value_local
                })
            
            if value_visit > 0.02:
                recomendaciones.append({
                    'nivel': 1,
                    'tipo': 'spread',
                    'desc': f"{partido['visitante']} {spread_visit['point']:+g}",
                    'probabilidad': prob_spread_visit,
                    'cuota': spread_visit['price'],
                    'value': value_visit
                })
        
        # ========================================
        # NIVEL 2: TOTALES (OVER/UNDER)
        # ========================================
        if 'totals' in odds:
            total = odds['totals']['Over']
            
            # Estimar puntos totales basado en odds
            pts_estimados = self._estimar_puntos(odds)
            diff = pts_estimados - total['point']
            
            # Probabilidad de Over (distribución normal aproximada)
            if diff > 8:
                prob_over = 0.75
            elif diff > 4:
                prob_over = 0.65
            elif diff > 0:
                prob_over = 0.55
            elif diff > -4:
                prob_over = 0.45
            elif diff > -8:
                prob_over = 0.35
            else:
                prob_over = 0.25
            
            prob_under = 1 - prob_over
            
            value_over = (prob_over * total['price']) - 1
            value_under = (prob_under * odds['totals']['Under']['price']) - 1
            
            if value_over > 0.02:
                recomendaciones.append({
                    'nivel': 2,
                    'tipo': 'total',
                    'desc': f"OVER {total['point']}",
                    'probabilidad': prob_over,
                    'cuota': total['price'],
                    'value': value_over
                })
            
            if value_under > 0.02:
                recomendaciones.append({
                    'nivel': 2,
                    'tipo': 'total',
                    'desc': f"UNDER {total['point']}",
                    'probabilidad': prob_under,
                    'cuota': odds['totals']['Under']['price'],
                    'value': value_under
                })
        
        # ========================================
        # NIVEL 3: MONEYLINE
        # ========================================
        if 'h2h' in odds:
            ml_local = odds['h2h'][partido['local']]
            ml_visit = odds['h2h'][partido['visitante']]
            
            prob_local = 1/ml_local
            prob_visit = 1/ml_visit
            total_prob = prob_local + prob_visit
            prob_local = prob_local / total_prob
            prob_visit = prob_visit / total_prob
            
            value_local = (prob_local * ml_local) - 1
            value_visit = (prob_visit * ml_visit) - 1
            
            if value_local > 0.02:
                recomendaciones.append({
                    'nivel': 3,
                    'tipo': 'moneyline',
                    'desc': f"{partido['local']} gana",
                    'probabilidad': prob_local,
                    'cuota': ml_local,
                    'value': value_local
                })
            
            if value_visit > 0.02:
                recomendaciones.append({
                    'nivel': 3,
                    'tipo': 'moneyline',
                    'desc': f"{partido['visitante']} gana",
                    'probabilidad': prob_visit,
                    'cuota': ml_visit,
                    'value': value_visit
                })
        
        # Ordenar por nivel (primero spread, luego totals, luego moneyline)
        return sorted(recomendaciones, key=lambda x: x['nivel'])
    
    def _estimar_puntos(self, odds):
        """Estima puntos totales basado en moneyline"""
        ml_local = list(odds['h2h'].values())[0]
        ml_visit = list(odds['h2h'].values())[1]
        
        prob_local = 1/ml_local
        prob_visit = 1/ml_visit
        
        # Equipos favoritos tienden a anotar más
        if prob_local > prob_visit:
            return 225 + (prob_local - 0.5) * 20
        else:
            return 225 + (prob_visit - 0.5) * 20
