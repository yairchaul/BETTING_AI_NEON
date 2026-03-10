# Reglas específicas para UFC

def aplicar_reglas_ufc(probabilities, fighter1, fighter2):
    # Aplica reglas para apuestas UFC
    picks = []
    
    # Regla 1: Moneyline con favorito claro
    if probabilities['fighter1_win_prob'] > 0.65:
        picks.append({
            'nivel': 1,
            'mercado': f'Gana {fighter1}',
            'prob': probabilities['fighter1_win_prob']
        })
    elif probabilities['fighter2_win_prob'] > 0.65:
        picks.append({
            'nivel': 1,
            'mercado': f'Gana {fighter2}',
            'prob': probabilities['fighter2_win_prob']
        })
    
    # Regla 2: Método de victoria con alta probabilidad
    method_probs = probabilities['method_probs']
    for method, prob in method_probs.items():
        if prob > 0.40:
            method_name = {
                'ko_tko': 'KO/TKO',
                'submission': 'Sumisión',
                'decision': 'Decisión'
            }.get(method, method)
            picks.append({
                'nivel': 2,
                'mercado': f'Victoria por {method_name}',
                'prob': prob
            })
    
    return picks
