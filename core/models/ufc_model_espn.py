class UFCModelESPN:
    # Modelo para predicciones UFC usando datos de ESPN
    
    def calculate_fight_probabilities(self, fighter1, fighter2):
        # Calcula probabilidades usando estadísticas reales de ESPN
        if not fighter1 or not fighter2:
            return self._default_probs()
        
        f1_stats = fighter1.get('stats', {})
        f2_stats = fighter2.get('stats', {})
        
        # Calcular poder de striking
        f1_strike_acc = f1_stats.get('significant_strikes_landed', 0) / max(f1_stats.get('significant_strikes_attempted', 1), 1)
        f2_strike_acc = f2_stats.get('significant_strikes_landed', 0) / max(f2_stats.get('significant_strikes_attempted', 1), 1)
        
        # Calcular poder de derribos
        f1_td_acc = f1_stats.get('takedowns_landed', 0) / max(f1_stats.get('takedowns_attempted', 1), 1)
        f2_td_acc = f2_stats.get('takedowns_landed', 0) / max(f2_stats.get('takedowns_attempted', 1), 1)
        
        # Factores de ventaja
        reach_adv = (fighter1.get('reach', 170) - fighter2.get('reach', 170)) / 20
        age_adv = (fighter2.get('age', 30) - fighter1.get('age', 30)) / 10
        
        # Calcular win probability
        base_prob = 0.5
        base_prob += reach_adv * 0.05
        base_prob += age_adv * 0.04
        base_prob += (f1_strike_acc - f2_strike_acc) * 0.1
        base_prob += (f1_td_acc - f2_td_acc) * 0.1
        
        base_prob = min(0.95, max(0.05, base_prob))
        
        # Calcular probabilidades de método
        f1_ko_rate = fighter1.get('stats', {}).get('knockouts', 0) / max(fighter1.get('stats', {}).get('total_fights', 1), 1)
        f2_ko_rate = fighter2.get('stats', {}).get('knockouts', 0) / max(fighter2.get('stats', {}).get('total_fights', 1), 1)
        
        f1_sub_rate = fighter1.get('stats', {}).get('submissions', 0) / max(fighter1.get('stats', {}).get('total_fights', 1), 1)
        f2_sub_rate = fighter2.get('stats', {}).get('submissions', 0) / max(fighter2.get('stats', {}).get('total_fights', 1), 1)
        
        ko_prob = (f1_ko_rate * base_prob + f2_ko_rate * (1 - base_prob)) / 2
        sub_prob = (f1_sub_rate * base_prob + f2_sub_rate * (1 - base_prob)) / 2
        dec_prob = 1 - ko_prob - sub_prob
        
        return {
            'fighter1_win_prob': round(base_prob, 3),
            'fighter2_win_prob': round(1 - base_prob, 3),
            'method_probs': {
                'ko_tko': round(ko_prob, 3),
                'submission': round(sub_prob, 3),
                'decision': round(dec_prob, 3)
            }
        }
    
    def _default_probs(self):
        return {
            'fighter1_win_prob': 0.5,
            'fighter2_win_prob': 0.5,
            'method_probs': {
                'ko_tko': 0.3,
                'submission': 0.2,
                'decision': 0.5
            }
        }
