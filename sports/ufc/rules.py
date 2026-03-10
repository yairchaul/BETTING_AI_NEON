class UFCRules:
    # Reglas jerárquicas para UFC (análogas a las 6 reglas de fútbol)
    # Analiza: Moneyline, Método de Victoria, Rounds
    
    def __init__(self):
        self.umbral_moneyline = 0.65        # Favorito muy claro
        self.umbral_method = 0.45           # Método dominante
        self.umbral_round = 0.30            # Round más probable
        self.umbral_ev = 0.05               # Valor esperado mínimo
    
    def aplicar_reglas(self, probs, fighter1, fighter2, odds1, odds2):
        picks = []
        
        prob1 = probs['moneyline']['fighter1_win'] / 10000
        prob2 = probs['moneyline']['fighter2_win'] / 10000
        ev_dict = probs.get('expected_value', {})
        
        # REGLA 1: Moneyline con favorito muy claro (>65%)
        if prob1 > self.umbral_moneyline:
            picks.append({
                'nivel': 1,
                'mercado': f'Gana {fighter1}',
                'prob': prob1,
                'tipo': 'moneyline_dominante',
                'ev': ev_dict.get('fighter1_ev', 0),
                'detalle': f"Favorito con {prob1:.1%} de probabilidad"
            })
            return picks
        elif prob2 > self.umbral_moneyline:
            picks.append({
                'nivel': 1,
                'mercado': f'Gana {fighter2}',
                'prob': prob2,
                'tipo': 'moneyline_dominante',
                'ev': ev_dict.get('fighter2_ev', 0),
                'detalle': f"Favorito con {prob2:.1%} de probabilidad"
            })
            return picks
        
        # REGLA 2: Método de victoria con alta probabilidad
        method_probs = probs['method_probs']
        for method, prob in method_probs.items():
            if prob > self.umbral_method:
                method_name = {
                    'ko_tko': 'KO/TKO',
                    'submission': 'Sumisión',
                    'decision': 'Decisión'
                }.get(method, method)
                picks.append({
                    'nivel': 2,
                    'mercado': f'Victoria por {method_name}',
                    'prob': prob,
                    'tipo': 'method',
                    'ev': 0,
                    'detalle': f"{prob:.1%} de terminar por {method_name}"
                })
        
        # REGLA 3: Round más probable de finalización
        round_probs = probs['round_probs']
        if round_probs:
            mejor_round = max(round_probs, key=round_probs.get)
            prob_round = round_probs[mejor_round]
            if prob_round > self.umbral_round:
                round_num = mejor_round.replace('_', ' ')
                picks.append({
                    'nivel': 3,
                    'mercado': f'Termina en {round_num}',
                    'prob': prob_round,
                    'tipo': 'round',
                    'ev': 0,
                    'detalle': f"{prob_round:.1%} de terminar en ese asalto"
                })
        
        # REGLA 4: Valor esperado positivo
        max_ev = max(
            ev_dict.get('fighter1_ev', 0),
            ev_dict.get('fighter2_ev', 0)
        )
        
        if max_ev > self.umbral_ev:
            if max_ev == ev_dict.get('fighter1_ev', 0):
                picks.append({
                    'nivel': 4,
                    'mercado': f'+EV {fighter1}',
                    'prob': prob1,
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
            else:
                picks.append({
                    'nivel': 4,
                    'mercado': f'+EV {fighter2}',
                    'prob': prob2,
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
        
        return picks
