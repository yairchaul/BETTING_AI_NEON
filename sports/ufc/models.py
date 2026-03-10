import numpy as np
import math

class UFCModelMATUA:
    # Modelo MATUA para UFC con 10,000 simulaciones
    
    def __init__(self):
        # Factores calibrados
        self.factors = {
            'odds_correlation': 0.25,
            'reach_advantage': 0.02,
            'age_advantage': 0.01
        }
        
        # Esquina roja tiene 58.6% de victorias
        self.red_corner_advantage = 0.586
        
        # Base de datos de peleadores (simulada por ahora)
        self.fighter_stats = {
            'Josh Emmett': {'ko_rate': 0.48, 'sub_rate': 0.04, 'reach': 178, 'age': 41},
            'Kevin Vallejos': {'ko_rate': 0.55, 'sub_rate': 0.06, 'reach': 182, 'age': 24},
            'Piera Rodriguez': {'ko_rate': 0.18, 'sub_rate': 0.18, 'reach': 170, 'age': 28},
            'Sam Hughes': {'ko_rate': 0.09, 'sub_rate': 0.09, 'reach': 168, 'age': 30},
            'Elijah Smith': {'ko_rate': 0.30, 'sub_rate': 0.10, 'reach': 175, 'age': 27},
            'Su Young You': {'ko_rate': 0.35, 'sub_rate': 0.15, 'reach': 173, 'age': 29},
            'Bia Mesquita': {'ko_rate': 0.10, 'sub_rate': 0.40, 'reach': 168, 'age': 26},
            'Montserrat Rendon': {'ko_rate': 0.20, 'sub_rate': 0.20, 'reach': 170, 'age': 28},
            'Luan Lacerda': {'ko_rate': 0.40, 'sub_rate': 0.20, 'reach': 180, 'age': 27},
            'Hecher Sosa': {'ko_rate': 0.35, 'sub_rate': 0.15, 'reach': 178, 'age': 29},
            'Bolaji Oki': {'ko_rate': 0.38, 'sub_rate': 0.12, 'reach': 182, 'age': 26},
            'Manoel Sousa': {'ko_rate': 0.30, 'sub_rate': 0.25, 'reach': 179, 'age': 28},
            'Chris Curtis': {'ko_rate': 0.42, 'sub_rate': 0.08, 'reach': 185, 'age': 37},
            'Myktybek Orolbai': {'ko_rate': 0.35, 'sub_rate': 0.20, 'reach': 180, 'age': 29},
            'Brad Tavares': {'ko_rate': 0.20, 'sub_rate': 0.05, 'reach': 183, 'age': 37},
            'Eryk Anders': {'ko_rate': 0.35, 'sub_rate': 0.05, 'reach': 185, 'age': 37},
            'Charles Johnson': {'ko_rate': 0.25, 'sub_rate': 0.10, 'reach': 170, 'age': 33},
            'Bruno Silva': {'ko_rate': 0.45, 'sub_rate': 0.05, 'reach': 180, 'age': 35},
            'Vitor Petrino': {'ko_rate': 0.30, 'sub_rate': 0.20, 'reach': 188, 'age': 27},
            'Steven Asplund': {'ko_rate': 0.25, 'sub_rate': 0.15, 'reach': 182, 'age': 29},
            'Marwan Rahiki': {'ko_rate': 0.40, 'sub_rate': 0.10, 'reach': 180, 'age': 26},
            'Harry Hardwick': {'ko_rate': 0.30, 'sub_rate': 0.15, 'reach': 178, 'age': 28},
            'Andre Fili': {'ko_rate': 0.35, 'sub_rate': 0.05, 'reach': 180, 'age': 34},
            'Jose Delgado': {'ko_rate': 0.40, 'sub_rate': 0.10, 'reach': 178, 'age': 27},
            'Ion Cutelaba': {'ko_rate': 0.45, 'sub_rate': 0.05, 'reach': 185, 'age': 31},
            'Oumar Sy': {'ko_rate': 0.30, 'sub_rate': 0.15, 'reach': 190, 'age': 28},
            'Amanda Lemos': {'ko_rate': 0.35, 'sub_rate': 0.10, 'reach': 165, 'age': 37},
            'Gillian Robertson': {'ko_rate': 0.10, 'sub_rate': 0.45, 'reach': 163, 'age': 29},
        }
    
    def get_fighter_stats(self, name):
        # Obtiene estadísticas de peleador
        if name in self.fighter_stats:
            return self.fighter_stats[name]
        return {'ko_rate': 0.3, 'sub_rate': 0.15, 'reach': 175, 'age': 30}
    
    def calculate_fight_probabilities(self, fighter1, fighter2,
                                     f1_stats=None, f2_stats=None,
                                     odds1=None, odds2=None):
        # Calcula probabilidades completas
        
        # Obtener estadísticas
        f1 = self.get_fighter_stats(fighter1)
        f2 = self.get_fighter_stats(fighter2)
        
        # Probabilidad base por odds
        if odds1 and odds2:
            prob1_odds = self._odds_to_probability(odds1)
            prob2_odds = self._odds_to_probability(odds2)
            odds_factor = prob1_odds / (prob1_odds + prob2_odds)
        else:
            odds_factor = 0.5
        
        # Ventajas físicas
        reach_adv = (f1['reach'] - f2['reach']) * self.factors['reach_advantage']
        age_adv = (f2['age'] - f1['age']) * self.factors['age_advantage']
        
        # Poder de finalización
        f1_power = f1['ko_rate'] * 1.5 + f1['sub_rate'] * 1.2
        f2_power = f2['ko_rate'] * 1.5 + f2['sub_rate'] * 1.2
        
        # Probabilidad base
        base_prob = 0.5 + (f1_power - f2_power) * 0.1 + reach_adv + age_adv
        base_prob = base_prob * 0.7 + odds_factor * 0.3
        base_prob = max(0.05, min(0.95, base_prob))
        
        # SIMULACIÓN MONTE CARLO (10,000)
        n_sim = 10000
        results = {
            'fighter1_wins': 0,
            'fighter2_wins': 0,
            'ko': 0, 'sub': 0, 'dec': 0,
            'rounds': [0, 0, 0, 0, 0]
        }
        
        for _ in range(n_sim):
            # Determinar ganador
            winner = 1 if np.random.random() < base_prob else 2
            
            if winner == 1:
                results['fighter1_wins'] += 1
                # Método según estilo
                rand = np.random.random()
                if rand < f1['ko_rate']:
                    results['ko'] += 1
                    # Round de KO
                    round_ko = int(np.random.exponential(2)) + 1
                    if round_ko <= 5:
                        results['rounds'][round_ko-1] += 1
                elif rand < f1['ko_rate'] + f1['sub_rate']:
                    results['sub'] += 1
                    round_sub = int(np.random.exponential(2)) + 1
                    if round_sub <= 5:
                        results['rounds'][round_sub-1] += 1
                else:
                    results['dec'] += 1
                    results['rounds'][4] += 1  # Decisión en round 5
            else:
                results['fighter2_wins'] += 1
                rand = np.random.random()
                if rand < f2['ko_rate']:
                    results['ko'] += 1
                    round_ko = int(np.random.exponential(2)) + 1
                    if round_ko <= 5:
                        results['rounds'][round_ko-1] += 1
                elif rand < f2['ko_rate'] + f2['sub_rate']:
                    results['sub'] += 1
                    round_sub = int(np.random.exponential(2)) + 1
                    if round_sub <= 5:
                        results['rounds'][round_sub-1] += 1
                else:
                    results['dec'] += 1
                    results['rounds'][4] += 1
        
        total_finishes = results['ko'] + results['sub']
        
        return {
            'moneyline': {
                'fighter1_win': results['fighter1_wins'],
                'fighter2_win': results['fighter2_wins']
            },
            'method_probs': {
                'ko_tko': results['ko'] / n_sim,
                'submission': results['sub'] / n_sim,
                'decision': results['dec'] / n_sim
            },
            'round_probs': {
                'round_1': results['rounds'][0] / max(total_finishes, 1),
                'round_2': results['rounds'][1] / max(total_finishes, 1),
                'round_3': results['rounds'][2] / max(total_finishes, 1),
                'round_4': results['rounds'][3] / max(total_finishes, 1),
                'round_5': results['rounds'][4] / max(total_finishes, 1)
            },
            'expected_value': self._calculate_ev(base_prob, odds1, odds2)
        }
    
    def _odds_to_probability(self, odds):
        # Convierte odds americanos a probabilidad
        odds = int(odds)
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return -odds / (-odds + 100)
    
    def _calculate_ev(self, prob, odds1, odds2):
        ev = {}
        if odds1:
            dec1 = self._american_to_decimal(odds1)
            ev['fighter1_ev'] = (prob * dec1) - 1
        if odds2:
            dec2 = self._american_to_decimal(odds2)
            ev['fighter2_ev'] = ((1 - prob) * dec2) - 1
        return ev
    
    def _american_to_decimal(self, odds):
        odds = int(odds)
        if odds > 0:
            return 1 + (odds / 100)
        else:
            return 1 + (100 / abs(odds))
