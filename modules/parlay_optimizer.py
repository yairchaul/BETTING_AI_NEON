# modules/parlay_optimizer.py
import numpy as np
import random
from itertools import combinations

class ParlayOptimizer:
    """
    Optimizador de parlays usando algoritmos genéticos
    Con validación estricta de picks duplicados
    """
    
    def __init__(self):
        self.generation = 0
    
    def find_optimal_parlays(self, available_picks, max_size=3, target_ev=0.05, population_size=20):
        """
        Encuentra parlays óptimos basados en EV (Valor Esperado)
        """
        if len(available_picks) < 2:
            return []
        
        # Filtrar picks con EV positivo
        value_picks = [p for p in available_picks if p.get('ev', 0) > target_ev]
        
        # Si no hay picks con EV, usar todos pero con advertencia
        if not value_picks:
            value_picks = available_picks
        
        best_parlays = []
        
        # Probar todas las combinaciones de tamaño 2 y 3
        for size in [2, 3]:
            if size > len(value_picks) or size > max_size:
                continue
                
            for combo in combinations(value_picks, size):
                # Verificar que cada elemento sea un diccionario válido
                valid_combo = True
                for pick in combo:
                    if not isinstance(pick, dict):
                        valid_combo = False
                        break
                    if 'match' not in pick or 'prob' not in pick:
                        valid_combo = False
                        break
                
                if not valid_combo:
                    continue
                
                # Verificar que no haya duplicados del mismo partido
                matches = set()
                for pick in combo:
                    if pick['match'] in matches:
                        valid_combo = False
                        break
                    matches.add(pick['match'])
                
                if not valid_combo:
                    continue
                
                # Calcular probabilidad y odds
                prob_total = 1.0
                odds_total = 1.0
                ev_total = 0.0
                
                for pick in combo:
                    prob_total *= pick['prob']
                    odds_total *= pick.get('odd', 1/pick['prob'])
                    ev_total += pick.get('ev', 0)
                
                # EV combinado (aproximación)
                ev_combined = (prob_total * odds_total) - 1
                
                best_parlays.append({
                    'picks': list(combo),
                    'prob': prob_total,
                    'odds': odds_total,
                    'ev_combined': ev_combined,
                    'ev_sum': ev_total,
                    'size': size
                })
        
        # Ordenar por EV combinado
        best_parlays.sort(key=lambda x: x['ev_combined'], reverse=True)
        
        # Eliminar parlays con probabilidad extremadamente baja
        best_parlays = [p for p in best_parlays if p['prob'] > 0.01]
        
        return best_parlays[0] if best_parlays else None
    
    def find_best_combinations(self, picks, max_size=3, min_ev=0.05):
        """
        Encuentra las mejores combinaciones por fuerza bruta (para comparación)
        """
        best_combinations = []
        
        for size in range(2, max_size + 1):
            for combo in combinations(picks, size):
                prob_total = np.prod([p['prob'] for p in combo])
                odds_total = np.prod([p.get('odd', 1/p['prob']) for p in combo])
                ev = (prob_total * odds_total) - 1
                
                if ev >= min_ev:
                    best_combinations.append({
                        'picks': combo,
                        'prob': prob_total,
                        'odds': odds_total,
                        'ev': ev,
                        'size': size
                    })
        
        # Ordenar por EV
        best_combinations.sort(key=lambda x: x['ev'], reverse=True)
        return best_combinations[:10]
    
    def _mutate(self, parlay, available_picks, mutation_rate=0.2):
        """Muta un parlay garantizando que no haya partidos duplicados"""
        if random.random() > mutation_rate:
            return parlay
        
        if not parlay or not available_picks:
            return parlay

        # Elegir un índice al azar para cambiar
        idx_to_replace = random.randint(0, len(parlay) - 1)
        
        # Identificar qué partidos YA están en el parlay (menos el que vamos a quitar)
        current_matches = {p['match'] for i, p in enumerate(parlay) if i != idx_to_replace}
        
        # Filtrar picks disponibles que NO pertenezcan a los partidos actuales
        valid_new_picks = [p for p in available_picks if p['match'] not in current_matches]
        
        if valid_new_picks:
            # Reemplazar con un pick de un partido distinto
            parlay[idx_to_replace] = random.choice(valid_new_picks)
        
        return parlay
    
    def calculate_kelly_stake(self, prob, odds, bankroll, fraction=0.25):
        """Calcula stake óptimo usando Kelly Criterion"""
        b = odds - 1
        if b <= 0:
            return 0
        
        p = prob
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        optimal_stake = bankroll * kelly_fraction * fraction
        
        return max(0, min(optimal_stake, bankroll * 0.1))
    
    def efficient_frontier(self, parlays, bankroll=1000):
        """Calcula la frontera eficiente de parlays"""
        results = []
        for parlay in parlays:
            if len(parlay) < 2:
                continue
            
            prob_total = np.prod([p.get('prob', 0.5) for p in parlay])
            odds_total = np.prod([p.get('odd', 2.0) for p in parlay])
            
            expected_return = (prob_total * odds_total) - 1
            risk = 1 - prob_total
            
            sharpe = expected_return / risk if risk > 0 else 0
            
            results.append({
                'parlay': parlay,
                'prob': prob_total,
                'odds': odds_total,
                'expected_return': expected_return,
                'risk': risk,
                'sharpe': sharpe,
                'stake': self.calculate_kelly_stake(prob_total, odds_total, bankroll)
            })
        
        return sorted(results, key=lambda x: x['sharpe'], reverse=True)
