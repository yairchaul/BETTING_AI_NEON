import math

class SoccerModel:
    def __init__(self):
        self.league_factors = {
            'Premier League': 1.15,
            'La Liga': 1.10,
            'Bundesliga': 1.20,
            'Serie A': 1.05,
            'Ligue 1': 1.10,
            'Liga MX': 1.00
        }
    
    def poisson(self, k, lam):
        return (math.exp(-lam) * lam**k) / math.factorial(k)
    
    def predict_match(self, home_team, away_team, competition, home_stats=None, away_stats=None):
        home_power = 1.5
        away_power = 1.3
        
        if home_stats:
            home_power = home_stats.get('avg_goals', 1.5)
        if away_stats:
            away_power = away_stats.get('avg_goals', 1.3)
        
        league_factor = self.league_factors.get(competition, 1.0)
        home_expected = home_power * 1.2 * league_factor
        away_expected = away_power * 0.9 * league_factor
        total_goals = home_expected + away_expected
        
        return {
            'markets': {
                'over_1_5': 1 - self.poisson(0, total_goals) - self.poisson(1, total_goals),
                'over_2_5': 1 - sum(self.poisson(i, total_goals) for i in range(3)),
                'over_3_5': 1 - sum(self.poisson(i, total_goals) for i in range(4)),
                'btts': (1 - self.poisson(0, home_expected)) * (1 - self.poisson(0, away_expected)),
                'over_1_5_1t': min(0.6, 1 - self.poisson(0, total_goals*0.35) - self.poisson(1, total_goals*0.35))
            },
            'probs': {
                'home': round(home_expected / (home_expected + away_expected + 0.5), 3),
                'draw': round(0.5 / (home_expected + away_expected + 0.5), 3),
                'away': round(away_expected / (home_expected + away_expected + 0.5), 3)
            }
        }
