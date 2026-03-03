# modules/parlay_optimizer.py
import numpy as np
from itertools import combinations

class ParlayOptimizer:
    """
    Optimizador de parlays que maximiza EV y diversifica mercados
    """
    
    def find_optimal_parlays(self, available_picks, max_size=3, target_ev=0.01):
        """
        Encuentra el mejor parlay basado en EV y diversificación
        """
        if len(available_picks) < 2:
            return None
        
        # Priorizar picks con EV positivo
        value_picks = [p for p in available_picks if p.get('ev', 0) > target_ev]
        
        # Si no hay suficientes picks con EV, usar todos
        picks_to_use = value_picks if len(value_picks) >= 2 else available_picks
        
        best_parlays = []
        
        for size in range(2, max_size + 1):
            for combo in combinations(picks_to_use, size):
                # Validar: no repetir partido
                matches = set()
                valid = True
                for p in combo:
                    if p['match'] in matches:
                        valid = False
                        break
                    matches.add(p['match'])
                
                if not valid:
                    continue
                
                # Calcular diversidad de categorías
                categories = set([p.get('category', '') for p in combo])
                diversity_score = len(categories) / size
                
                # Calcular probabilidad y odds totales
                prob_total = 1.0
                odds_total = 1.0
                for p in combo:
                    prob_total *= p['prob']
                    odds_total *= p.get('odd', 1/p['prob'])
                
                ev_combined = (prob_total * odds_total) - 1
                
                # Fitness combina EV y diversidad
                fitness = ev_combined * diversity_score
                
                best_parlays.append({
                    'picks': list(combo),
                    'prob': prob_total,
                    'odds': odds_total,
                    'ev_combined': ev_combined,
                    'fitness': fitness,
                    'diversity': diversity_score
                })
        
        if not best_parlays:
            return None
        
        # Ordenar por fitness (EV ajustado por diversidad)
        best_parlays.sort(key=lambda x: x['fitness'], reverse=True)
        return best_parlays[0]
