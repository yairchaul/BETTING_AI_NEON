import math
import numpy as np

class NBAModelEV:
    # Modelo NBA con análisis de Spread, Totales y Moneyline
    
    def __init__(self):
        self.home_advantage = 2.5
        self.spread_std = 11.5
        self.total_std = 12.5
        
        self.team_elo = {
            'Memphis Grizzlies': 1650, 'Philadelphia 76ers': 1630,
            'Dallas Mavericks': 1640, 'Atlanta Hawks': 1620,
            'Detroit Pistons': 1510, 'Brooklyn Nets': 1570,
            'Washington Wizards': 1520, 'Miami Heat': 1580,
            'Toronto Raptors': 1560, 'Houston Rockets': 1530,
            'Phoenix Suns': 1610, 'Milwaukee Bucks': 1620,
            'Boston Celtics': 1660, 'San Antonio Spurs': 1550,
            'Chicago Bulls': 1540, 'Golden State Warriors': 1640,
            'Charlotte Hornets': 1500, 'Portland Trail Blazers': 1530,
            'Indiana Pacers': 1520, 'Sacramento Kings': 1540,
            'Minnesota Timberwolves': 1580, 'Los Angeles Lakers': 1630
        }
    
    def calculate_game_probabilities(self, home, away, spread_line, total_line,
                                     odds_home_spread='-110', odds_away_spread='-110',
                                     moneyline_home='-110', moneyline_away='-110'):
        # Calcula probabilidades para NBA
        
        # ELO base
        elo_home = self.team_elo.get(home, 1500) + self.home_advantage * 10
        elo_away = self.team_elo.get(away, 1500)
        
        # Probabilidad moneyline
        win_prob_home = self._expected_score(elo_home, elo_away)
        
        # Convertir spread a número
        try:
            spread = float(spread_line.replace('+', ''))
        except:
            spread = 0
        
        # Probabilidad de cubrir el spread
        prob_cover = self._normal_cdf(spread + self.home_advantage, 0, self.spread_std)
        
        # Probabilidades de over/under
        try:
            total = float(total_line)
        except:
            total = 220
        
        league_avg = 225
        prob_over = self._normal_cdf(total - league_avg, 0, self.total_std)
        
        # Fair odds (quitando vig de la casa)
        fair_odds_spread = 1.0 / (prob_cover * 0.9524)
        fair_odds_over = 1.0 / (prob_over * 0.9524)
        fair_odds_under = 1.0 / ((1 - prob_over) * 0.9524)
        fair_odds_home_ml = 1.0 / (win_prob_home * 0.9524)
        fair_odds_away_ml = 1.0 / ((1 - win_prob_home) * 0.9524)
        
        # Calcular valor esperado
        ev_home_spread = self._calculate_ev(prob_cover, odds_home_spread)
        ev_away_spread = self._calculate_ev(1 - prob_cover, odds_away_spread)
        ev_over = self._calculate_ev(prob_over, odds_home_spread)  # odds_home_spread como placeholder
        ev_under = self._calculate_ev(1 - prob_over, odds_away_spread)
        ev_home_ml = self._calculate_ev(win_prob_home, moneyline_home)
        ev_away_ml = self._calculate_ev(1 - win_prob_home, moneyline_away)
        
        return {
            'spread_analysis': {
                'line': spread_line,
                'expected_margin': round(spread + self.home_advantage, 1),
                'prob_cover': round(prob_cover, 3),
                'fair_odds': round(fair_odds_spread, 2),
                'ev_home': ev_home_spread,
                'ev_away': ev_away_spread
            },
            'totals_analysis': {
                'total': total_line,
                'expected_total': round(total + (win_prob_home - 0.5) * 2, 1),
                'prob_over': round(prob_over, 3),
                'prob_under': round(1 - prob_over, 3),
                'fair_odds_over': round(fair_odds_over, 2),
                'fair_odds_under': round(fair_odds_under, 2),
                'ev_over': ev_over,
                'ev_under': ev_under
            },
            'moneyline_analysis': {
                'home_win_prob': round(win_prob_home, 3),
                'away_win_prob': round(1 - win_prob_home, 3),
                'fair_odds_home': round(fair_odds_home_ml, 2),
                'fair_odds_away': round(fair_odds_away_ml, 2),
                'ev_home': ev_home_ml,
                'ev_away': ev_away_ml
            }
        }
    
    def _expected_score(self, elo_a, elo_b):
        return 1 / (1 + math.pow(10, (elo_b - elo_a) / 400))
    
    def _normal_cdf(self, x, mean, std):
        return 0.5 * (1 + math.erf((x - mean) / (std * math.sqrt(2))))
    
    def _american_to_decimal(self, odds):
        try:
            odds = str(odds).replace('+', '')
            odds = int(odds)
            if odds > 0:
                return 1 + (odds / 100)
            else:
                return 1 + (100 / abs(odds))
        except:
            return 2.0
    
    def _calculate_ev(self, prob, odds):
        if not odds:
            return 0
        decimal = self._american_to_decimal(odds)
        return (prob * decimal) - 1
