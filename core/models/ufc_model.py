class UFCModel:
    # Modelo para predicciones UFC
    
    def calculate_fight_probabilities(self, fighter1, fighter2, f1_stats=None, f2_stats=None):
        # Calcula probabilidades para una pelea UFC
        if f1_stats is None:
            f1_stats = {'win_rate': 0.85, 'ko_rate': 0.45, 'sub_rate': 0.30, 'reach': 185}
        if f2_stats is None:
            f2_stats = {'win_rate': 0.70, 'ko_rate': 0.40, 'sub_rate': 0.25, 'reach': 180}
        
        # Probabilidad base de victoria
        total_rate = f1_stats['win_rate'] + f2_stats['win_rate']
        f1_win_prob = f1_stats['win_rate'] / total_rate
        
        # Ventaja de alcance
        reach_advantage = (f1_stats['reach'] - f2_stats['reach']) / 10
        f1_win_prob += reach_advantage * 0.05
        f1_win_prob = min(0.95, max(0.05, f1_win_prob))
        
        # Probabilidades de método
        total_ko = f1_stats['ko_rate'] + f2_stats['ko_rate']
        total_sub = f1_stats['sub_rate'] + f2_stats['sub_rate']
        total_dec = 2 - total_ko - total_sub
        
        ko_prob = (f1_stats['ko_rate'] * f1_win_prob + f2_stats['ko_rate'] * (1 - f1_win_prob)) / 2
        sub_prob = (f1_stats['sub_rate'] * f1_win_prob + f2_stats['sub_rate'] * (1 - f1_win_prob)) / 2
        dec_prob = 1 - ko_prob - sub_prob
        
        return {
            'fighter1_win_prob': round(f1_win_prob, 3),
            'fighter2_win_prob': round(1 - f1_win_prob, 3),
            'method_probs': {
                'ko_tko': round(ko_prob, 3),
                'submission': round(sub_prob, 3),
                'decision': round(dec_prob, 3)
            }
        }
