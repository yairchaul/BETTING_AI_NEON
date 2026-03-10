# Reglas específicas para NBA

def aplicar_reglas_nba(probabilities, home, away, spread_line=None, total_line=None):
    # Aplica reglas para apuestas NBA
    picks = []
    
    # Regla 1: Spread con valor >55%
    if probabilities['prob_cover'] > 0.55:
        picks.append({
            'nivel': 1,
            'mercado': f'Spread {home}',
            'prob': probabilities['prob_cover'],
            'detalle': f"Margen esperado: {probabilities['expected_margin']:+.1f}"
        })
    
    # Regla 2: Over/Under con valor >60%
    if probabilities['prob_over'] > 0.60:
        picks.append({
            'nivel': 2,
            'mercado': 'Over',
            'prob': probabilities['prob_over'],
            'detalle': f"Total esperado: {probabilities['expected_total']}"
        })
    elif probabilities['prob_under'] > 0.60:
        picks.append({
            'nivel': 2,
            'mercado': 'Under',
            'prob': probabilities['prob_under'],
            'detalle': f"Total esperado: {probabilities['expected_total']}"
        })
    
    # Regla 3: Moneyline cuando hay gran diferencia
    if probabilities['home_win_prob'] > 0.70:
        picks.append({
            'nivel': 3,
            'mercado': f'Gana {home}',
            'prob': probabilities['home_win_prob']
        })
    elif probabilities['home_win_prob'] < 0.30:
        picks.append({
            'nivel': 3,
            'mercado': f'Gana {away}',
            'prob': 1 - probabilities['home_win_prob']
        })
    
    return picks
