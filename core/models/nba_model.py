import math

class NBAModel:
    # Modelo para predicciones NBA
    
    def calculate_game_probabilities(self, home_team, away_team, home_stats=None, away_stats=None):
        # Calcula probabilidades para un juego NBA
        if home_stats is None:
            home_stats = {'points': 115.0, 'points_allowed': 112.0, 'win_rate': 0.65}
        if away_stats is None:
            away_stats = {'points': 112.0, 'points_allowed': 113.0, 'win_rate': 0.55}
        
        # Diferencia de puntos esperada
        point_diff = (home_stats['points'] - home_stats['points_allowed']) - \
                     (away_stats['points'] - away_stats['points_allowed'])
        
        # Ventaja localía (+2.5 puntos)
        expected_margin = point_diff + 2.5
        
        # Probabilidad de cubrir el spread (usando distribución normal)
        prob_cover = self._normal_cdf(expected_margin, 0, 12)
        
        # Total esperado
        expected_total = home_stats['points'] + away_stats['points']
        
        return {
            'expected_margin': round(expected_margin, 1),
            'prob_cover': round(prob_cover, 3),
            'expected_total': round(expected_total, 1),
            'prob_over': round(self._normal_cdf(expected_total - 220, 0, 12), 3),
            'prob_under': round(1 - self._normal_cdf(expected_total - 220, 0, 12), 3),
            'home_win_prob': round(home_stats['win_rate'] / (home_stats['win_rate'] + away_stats['win_rate']), 3)
        }
    
    def _normal_cdf(self, x, mean, std):
        # Función de distribución acumulada normal
        return 0.5 * (1 + math.erf((x - mean) / (std * math.sqrt(2))))
