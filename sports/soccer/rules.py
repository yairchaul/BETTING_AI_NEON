class SoccerRules:
    # Reglas jerárquicas para fútbol
    
    def __init__(self):
        self.umbral_over_1t = 0.60
        self.umbral_over_3_5 = 0.60
        self.umbral_favorito_over = 0.55
        self.umbral_btts = 0.60
        self.umbral_over = 0.55
        self.objetivo_over = 0.55
        self.umbral_favorito = 0.50
        self.umbral_underdog = 0.40
    
    def aplicar_reglas(self, markets, probs, home, away):
        picks = []
        
        # REGLA 1: Over 1.5 1T
        if markets['over_1_5_1t'] > self.umbral_over_1t:
            picks.append({'nivel': 1, 'mercado': 'Over 1.5 1T', 'prob': markets['over_1_5_1t']})
            return picks
        
        # REGLA 2: Over 3.5 + Favorito
        if markets['over_3_5'] > self.umbral_over_3_5:
            if probs['home'] > self.umbral_favorito_over:
                picks.append({'nivel': 2, 'mercado': f'Gana {home}', 'prob': probs['home']})
                picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': markets['over_3_5']})
                return picks
            if probs['away'] > self.umbral_favorito_over:
                picks.append({'nivel': 2, 'mercado': f'Gana {away}', 'prob': probs['away']})
                picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': markets['over_3_5']})
                return picks
        
        # REGLA 3: BTTS
        if markets['btts'] > self.umbral_btts:
            picks.append({'nivel': 3, 'mercado': 'BTTS Sí', 'prob': markets['btts']})
            return picks
        
        # REGLA 4: Mejor Over
        if probs['home'] < self.umbral_favorito and probs['away'] < self.umbral_favorito:
            overs = [('Over 1.5', markets['over_1_5']), ('Over 2.5', markets['over_2_5']), ('Over 3.5', markets['over_3_5'])]
            overs_validos = [(n, p) for n, p in overs if p > self.umbral_over]
            if overs_validos:
                mejor = min(overs_validos, key=lambda x: abs(x[1] - self.objetivo_over))
                picks.append({'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]})
            else:
                mejor = max(overs, key=lambda x: x[1])
                picks.append({'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]})
            return picks
        
        # REGLA 5: Favorito Local
        if probs['home'] > self.umbral_favorito and probs['away'] < self.umbral_underdog:
            picks.append({'nivel': 5, 'mercado': f'Gana {home}', 'prob': probs['home']})
            overs = [('Over 1.5', markets['over_1_5']), ('Over 2.5', markets['over_2_5']), ('Over 3.5', markets['over_3_5'])]
            mejor = max(overs, key=lambda x: x[1])
            picks.append({'nivel': 5, 'mercado': mejor[0], 'prob': mejor[1]})
            return picks
        
        # REGLA 6: Favorito Visitante
        if probs['away'] > self.umbral_favorito and probs['home'] < self.umbral_underdog:
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
