# Reglas jerárquicas para fútbol

def aplicar_reglas_soccer(markets, probs, home, away):
    picks = []
    
    # REGLA 1: Over 1.5 1T > 60%
    if markets['over_1_5_1t'] > 0.60:
        picks.append({'nivel': 1, 'mercado': 'Over 1.5 1T', 'prob': markets['over_1_5_1t']})
        return picks
    
    # REGLA 2: Over 3.5 >60% + Favorito >55%
    if markets['over_3_5'] > 0.60:
        if probs['home'] > 0.55:
            picks.append({'nivel': 2, 'mercado': f'Gana {home}', 'prob': probs['home']})
            picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': markets['over_3_5']})
            return picks
        if probs['away'] > 0.55:
            picks.append({'nivel': 2, 'mercado': f'Gana {away}', 'prob': probs['away']})
            picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': markets['over_3_5']})
            return picks
    
    # REGLA 3: BTTS > 60%
    if markets['btts'] > 0.60:
        picks.append({'nivel': 3, 'mercado': 'BTTS Sí', 'prob': markets['btts']})
        return picks
    
    # REGLA 4: Mejor Over
    if probs['home'] < 0.55 and probs['away'] < 0.55:
        overs = [
            ('Over 1.5', markets['over_1_5']),
            ('Over 2.5', markets['over_2_5']),
            ('Over 3.5', markets['over_3_5'])
        ]
        overs_validos = [(n, p) for n, p in overs if p > 0.55]
        if overs_validos:
            mejor = min(overs_validos, key=lambda x: abs(x[1] - 0.55))
            picks.append({'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]})
        else:
            mejor = max(overs, key=lambda x: x[1])
            picks.append({'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]})
        return picks
    
    # REGLA 5: Favorito Local
    if probs['home'] > 0.50 and probs['away'] < 0.40:
        picks.append({'nivel': 5, 'mercado': f'Gana {home}', 'prob': probs['home']})
        overs = [('Over 1.5', markets['over_1_5']), ('Over 2.5', markets['over_2_5']), ('Over 3.5', markets['over_3_5'])]
        mejor = max(overs, key=lambda x: x[1])
        picks.append({'nivel': 5, 'mercado': mejor[0], 'prob': mejor[1]})
        return picks
    
    # REGLA 6: Favorito Visitante
    if probs['away'] > 0.50 and probs['home'] < 0.40:
        picks.append({'nivel': 6, 'mercado': f'Gana {away}', 'prob': probs['away']})
        overs = [('Over 1.5', markets['over_1_5']), ('Over 2.5', markets['over_2_5']), ('Over 3.5', markets['over_3_5'])]
        mejor = max(overs, key=lambda x: x[1])
        picks.append({'nivel': 6, 'mercado': mejor[0], 'prob': mejor[1]})
        return picks
    
    # Default
    overs = [('Over 1.5', markets['over_1_5']), ('Over 2.5', markets['over_2_5']), ('Over 3.5', markets['over_3_5'])]
    mejor = max(overs, key=lambda x: x[1])
    picks.append({'nivel': 7, 'mercado': mejor[0], 'prob': mejor[1]})
    return picks
