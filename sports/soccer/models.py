import math
import numpy as np

class SoccerModel:
    # Modelo académico para fútbol
    
    def get_team_power(self, team_name):
        power_base = {
            'Liverpool': {'attack': 2.1, 'defense': 0.9},
            'Arsenal': {'attack': 2.0, 'defense': 1.0},
            'Chelsea': {'attack': 1.9, 'defense': 1.0},
            'Tottenham': {'attack': 1.9, 'defense': 1.1},
            'Manchester City': {'attack': 2.2, 'defense': 0.9},
            'Newcastle': {'attack': 1.8, 'defense': 1.1},
            'Galatasaray': {'attack': 1.9, 'defense': 1.1},
            'Barcelona': {'attack': 2.1, 'defense': 0.9},
            'Real Madrid': {'attack': 2.2, 'defense': 0.8},
            'Atletico Madrid': {'attack': 1.8, 'defense': 1.0},
            'Bayern': {'attack': 2.3, 'defense': 0.8},
            'Bayer': {'attack': 2.0, 'defense': 0.9},
            'PSG': {'attack': 2.2, 'defense': 0.9},
        }
        
        for name, stats in power_base.items():
            if name.lower() in team_name.lower():
                return stats
        return {'attack': 1.7, 'defense': 1.1}
    
    def predict_match(self, home, away, competition, home_stats, away_stats):
        lambda_home = home_stats['attack'] * 1.1
        lambda_away = away_stats['attack']
        
        def poisson(k, lam):
            return (math.exp(-lam) * lam**k) / math.factorial(k)
        
        over_1_5 = 1 - poisson(0, lambda_home+lambda_away) - poisson(1, lambda_home+lambda_away)
        over_2_5 = 1 - sum(poisson(i, lambda_home+lambda_away) for i in range(3))
        over_3_5 = 1 - sum(poisson(i, lambda_home+lambda_away) for i in range(4))
        btts = (1 - poisson(0, lambda_home)) * (1 - poisson(0, lambda_away))
        over_1_5_1t = 1 - poisson(0, (lambda_home+lambda_away)*0.35) - poisson(1, (lambda_home+lambda_away)*0.35)
        
        n_sim = 10000
        home_wins = sum(1 for _ in range(n_sim) if np.random.poisson(lambda_home) > np.random.poisson(lambda_away))
        away_wins = sum(1 for _ in range(n_sim) if np.random.poisson(lambda_home) < np.random.poisson(lambda_away))
        draws = n_sim - home_wins - away_wins
        
        return {
            'markets': {
                'over_1_5': round(over_1_5, 3),
                'over_2_5': round(over_2_5, 3),
                'over_3_5': round(over_3_5, 3),
                'btts': round(btts, 3),
                'over_1_5_1t': round(over_1_5_1t, 3)
            },
            'probs': {
                'home': home_wins / n_sim,
                'draw': draws / n_sim,
                'away': away_wins / n_sim
            }
        }
