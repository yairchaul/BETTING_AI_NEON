import math
import numpy as np

class SoccerModelAcademico:
    # Modelo basado en investigación académica 
    
    def __init__(self):
        # Factores de liga (balanceados)
        self.league_factors = {
            'Premier League': {'attack_factor': 1.10, 'defense_factor': 0.95, 'home_boost': 1.15},
            'La Liga': {'attack_factor': 1.08, 'defense_factor': 0.96, 'home_boost': 1.12},
            'Bundesliga': {'attack_factor': 1.15, 'defense_factor': 0.92, 'home_boost': 1.18},
            'Serie A': {'attack_factor': 1.05, 'defense_factor': 0.98, 'home_boost': 1.10},
            'Ligue 1': {'attack_factor': 1.07, 'defense_factor': 0.97, 'home_boost': 1.12},
            'Eredivisie': {'attack_factor': 1.12, 'defense_factor': 0.94, 'home_boost': 1.15},
            'Primeira Liga': {'attack_factor': 1.00, 'defense_factor': 1.02, 'home_boost': 1.08},
            'Liga MX': {'attack_factor': 1.02, 'defense_factor': 1.00, 'home_boost': 1.10},
        }
        
        # Coeficientes del modelo PARX (balanceados)
        self.alpha = 0.20
        self.beta_attack = 0.15
        self.beta_defense = -0.10
        self.beta_home = 0.20  # Reducido para evitar sesgo
    
    def get_team_power(self, team_name):
        # Poder ofensivo y defensivo balanceado por equipo
        power_base = {
            # Premier League
            'Manchester City': {'attack': 2.2, 'defense': 0.9},
            'Liverpool': {'attack': 2.1, 'defense': 0.9},
            'Arsenal': {'attack': 2.0, 'defense': 1.0},
            'Chelsea': {'attack': 1.9, 'defense': 1.0},
            'Tottenham': {'attack': 1.9, 'defense': 1.1},
            'Newcastle': {'attack': 1.8, 'defense': 1.1},
            
            # La Liga
            'Real Madrid': {'attack': 2.2, 'defense': 0.8},
            'Barcelona': {'attack': 2.1, 'defense': 0.9},
            'Atletico Madrid': {'attack': 1.8, 'defense': 1.0},
            'Atlético': {'attack': 1.8, 'defense': 1.0},
            'Real Sociedad': {'attack': 1.7, 'defense': 1.1},
            
            # Bundesliga
            'Bayern': {'attack': 2.3, 'defense': 0.8},
            'Bayern Munich': {'attack': 2.3, 'defense': 0.8},
            'Borussia Dortmund': {'attack': 2.0, 'defense': 1.1},
            'Bayer': {'attack': 2.0, 'defense': 0.9},
            'Bayer Leverkusen': {'attack': 2.0, 'defense': 0.9},
            
            # Serie A
            'Juventus': {'attack': 1.8, 'defense': 0.9},
            'Milan': {'attack': 1.9, 'defense': 1.0},
            'Inter': {'attack': 2.0, 'defense': 0.9},
            'Atalanta': {'attack': 2.0, 'defense': 1.1},
            'Napoli': {'attack': 1.9, 'defense': 1.0},
            
            # Ligue 1
            'PSG': {'attack': 2.2, 'defense': 0.9},
            'Paris Saint Germain': {'attack': 2.2, 'defense': 0.9},
            'Marseille': {'attack': 1.7, 'defense': 1.1},
            'Lyon': {'attack': 1.8, 'defense': 1.1},
            
            # Eredivisie
            'Ajax': {'attack': 2.1, 'defense': 1.0},
            'PSV': {'attack': 2.0, 'defense': 1.0},
            'Feyenoord': {'attack': 1.9, 'defense': 1.1},
            
            # Primeira Liga
            'Benfica': {'attack': 2.0, 'defense': 0.9},
            'Porto': {'attack': 1.9, 'defense': 1.0},
            'Sporting': {'attack': 1.9, 'defense': 1.0},
            'Lisboa': {'attack': 1.9, 'defense': 1.0},
            
            # Liga MX
            'América': {'attack': 1.8, 'defense': 1.1},
            'Guadalajara': {'attack': 1.7, 'defense': 1.1},
            'Tigres': {'attack': 1.8, 'defense': 1.0},
            'Monterrey': {'attack': 1.8, 'defense': 1.0},
            
            # Turquía
            'Galatasaray': {'attack': 1.9, 'defense': 1.1},
            'Fenerbahce': {'attack': 1.8, 'defense': 1.1},
            'Besiktas': {'attack': 1.7, 'defense': 1.2},
        }
        
        # Buscar por coincidencia parcial
        for name, stats in power_base.items():
            if name.lower() in team_name.lower() or team_name.lower() in name.lower():
                return stats
        
        # Valores por defecto balanceados
        return {'attack': 1.7, 'defense': 1.1}
    
    def predict_match(self, home, away, competition, home_stats=None, away_stats=None):
        # Obtener poder de equipos
        home_power = self.get_team_power(home)
        away_power = self.get_team_power(away)
        
        # Factores de liga
        league = self.league_factors.get(competition, {'attack_factor': 1.0, 'defense_factor': 1.0, 'home_boost': 1.1})
        
        # Calcular λ (goles esperados) balanceados
        lambda_home = math.exp(
            self.alpha + 
            self.beta_attack * home_power['attack'] * league['attack_factor'] +
            self.beta_defense * away_power['defense'] * league['defense_factor'] +
            self.beta_home * league['home_boost']
        )
        
        lambda_away = math.exp(
            self.alpha + 
            self.beta_attack * away_power['attack'] * league['attack_factor'] +
            self.beta_defense * home_power['defense'] * league['defense_factor']
        )
        
        # Distribución de Poisson
        def poisson_prob(k, lam):
            return (math.exp(-lam) * lam**k) / math.factorial(k)
        
        # Calcular mercados
        over_1_5 = 1 - (poisson_prob(0, lambda_home) * poisson_prob(0, lambda_away) +
                        poisson_prob(1, lambda_home) * poisson_prob(0, lambda_away) +
                        poisson_prob(0, lambda_home) * poisson_prob(1, lambda_away))
        
        over_2_5 = 1 - sum(poisson_prob(i, lambda_home) * poisson_prob(j, lambda_away) 
                          for i in range(3) for j in range(3) if i + j <= 2)
        
        over_3_5 = 1 - sum(poisson_prob(i, lambda_home) * poisson_prob(j, lambda_away) 
                          for i in range(4) for j in range(4) if i + j <= 3)
        
        btts = (1 - poisson_prob(0, lambda_home)) * (1 - poisson_prob(0, lambda_away))
        
        lambda_1t_home = lambda_home * 0.35
        lambda_1t_away = lambda_away * 0.35
        over_1_5_1t = 1 - (poisson_prob(0, lambda_1t_home) * poisson_prob(0, lambda_1t_away) +
                           poisson_prob(1, lambda_1t_home) * poisson_prob(0, lambda_1t_away) +
                           poisson_prob(0, lambda_1t_home) * poisson_prob(1, lambda_1t_away))
        over_1_5_1t = min(0.60, over_1_5_1t)
        
        # Simulación Monte Carlo para 1X2
        n_sim = 10000
        home_wins = 0
        draws = 0
        away_wins = 0
        
        for _ in range(n_sim):
            h = np.random.poisson(lambda_home)
            a = np.random.poisson(lambda_away)
            if h > a:
                home_wins += 1
            elif a > h:
                away_wins += 1
            else:
                draws += 1
        
        return {
            'markets': {
                'over_1_5': round(over_1_5, 3),
                'over_2_5': round(over_2_5, 3),
                'over_3_5': round(over_3_5, 3),
                'btts': round(btts, 3),
                'over_1_5_1t': round(over_1_5_1t, 3)
            },
            'probs': {
                'home': round(home_wins / n_sim, 3),
                'draw': round(draws / n_sim, 3),
                'away': round(away_wins / n_sim, 3)
            },
            'expected_goals': {
                'home': round(lambda_home, 2),
                'away': round(lambda_away, 2),
                'total': round(lambda_home + lambda_away, 2)
            }
        }
