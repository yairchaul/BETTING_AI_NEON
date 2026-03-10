class NBARules:
    # Reglas jerárquicas para NBA (análogas a las 6 reglas de fútbol)
    # Analiza: Handicap (Spread), Puntos Totales (Over/Under), Equipo a Ganar (Moneyline)
    
    def __init__(self):
        self.umbral_spread = 0.60          # Spread con valor claro
        self.umbral_spread_medio = 0.55     # Spread en zona de valor
        self.umbral_total = 0.60            # Over/Under dominante
        self.umbral_total_medio = 0.55      # Over/Under en zona de valor
        self.umbral_moneyline = 0.65        # Favorito muy claro
        self.umbral_combinado = 0.50        # Probabilidad mínima para combinados
        self.umbral_ev = 0.05               # Valor esperado mínimo (+5%)
    
    def aplicar_reglas(self, analysis, home, away):
        # Aplica 6 reglas jerárquicas para NBA
        picks = []
        
        # REGLA 1: Spread con valor claro >60%
        if analysis['spread_analysis']['prob_cover'] > self.umbral_spread:
            equipo = home if analysis['spread_analysis']['expected_margin'] > 0 else away
            picks.append({
                'nivel': 1,
                'mercado': f'{equipo} Spread',
                'prob': analysis['spread_analysis']['prob_cover'],
                'tipo': 'spread_dominante',
                'detalle': f"Spread con {analysis['spread_analysis']['prob_cover']:.1%} de probabilidad",
                'ev': analysis['spread_analysis']['ev_home'] if equipo == home else analysis['spread_analysis']['ev_away']
            })
            return picks
        
        # REGLA 2: Over/Total dominante >60%
        if analysis['totals_analysis']['prob_over'] > self.umbral_total:
            picks.append({
                'nivel': 2,
                'mercado': 'Over',
                'prob': analysis['totals_analysis']['prob_over'],
                'tipo': 'over_dominante',
                'detalle': f"Over con {analysis['totals_analysis']['prob_over']:.1%} de probabilidad",
                'ev': analysis['totals_analysis']['ev_over']
            })
            return picks
        elif analysis['totals_analysis']['prob_under'] > self.umbral_total:
            picks.append({
                'nivel': 2,
                'mercado': 'Under',
                'prob': analysis['totals_analysis']['prob_under'],
                'tipo': 'under_dominante',
                'detalle': f"Under con {analysis['totals_analysis']['prob_under']:.1%} de probabilidad",
                'ev': analysis['totals_analysis']['ev_under']
            })
            return picks
        
        # REGLA 3: Favorito claro Moneyline
        if analysis['moneyline_analysis']['home_win_prob'] > self.umbral_moneyline:
            picks.append({
                'nivel': 3,
                'mercado': f'Gana {home}',
                'prob': analysis['moneyline_analysis']['home_win_prob'],
                'tipo': 'moneyline_favorito',
                'detalle': f"Favorito con {analysis['moneyline_analysis']['home_win_prob']:.1%} de probabilidad",
                'ev': analysis['moneyline_analysis']['ev_home']
            })
            return picks
        elif analysis['moneyline_analysis']['away_win_prob'] > self.umbral_moneyline:
            picks.append({
                'nivel': 3,
                'mercado': f'Gana {away}',
                'prob': analysis['moneyline_analysis']['away_win_prob'],
                'tipo': 'moneyline_favorito',
                'detalle': f"Favorito con {analysis['moneyline_analysis']['away_win_prob']:.1%} de probabilidad",
                'ev': analysis['moneyline_analysis']['ev_away']
            })
            return picks
        
        # REGLA 4: Spread en zona de valor (cercano a 55%)
        prob_cover = analysis['spread_analysis']['prob_cover']
        if 0.50 <= prob_cover <= 0.60:
            equipo = home if analysis['spread_analysis']['expected_margin'] > 0 else away
            picks.append({
                'nivel': 4,
                'mercado': f'{equipo} Spread',
                'prob': prob_cover,
                'tipo': 'spread_valor',
                'detalle': f"Spread en zona de valor ({prob_cover:.1%})",
                'ev': analysis['spread_analysis']['ev_home'] if equipo == home else analysis['spread_analysis']['ev_away']
            })
            return picks
        
        # REGLA 5: Combinado Spread + Over (análogo a Favorito + Over en fútbol)
        if prob_cover > 0.50 and analysis['totals_analysis']['prob_over'] > 0.50:
            prob_combinado = prob_cover * analysis['totals_analysis']['prob_over']
            if prob_combinado > self.umbral_combinado:
                picks.append({
                    'nivel': 5,
                    'mercado': f'Combinado: Spread + Over',
                    'prob': prob_combinado,
                    'tipo': 'combinado',
                    'detalle': f"Probabilidad combinada: {prob_combinado:.1%}"
                })
                return picks
        
        # REGLA 6: Value bets por EV positivo
        max_ev = max(
            analysis['spread_analysis']['ev_home'],
            analysis['spread_analysis']['ev_away'],
            analysis['totals_analysis']['ev_over'],
            analysis['totals_analysis']['ev_under'],
            analysis['moneyline_analysis']['ev_home'],
            analysis['moneyline_analysis']['ev_away']
        )
        
        if max_ev > self.umbral_ev:
            if max_ev == analysis['spread_analysis']['ev_home']:
                picks.append({
                    'nivel': 6,
                    'mercado': f'+EV {home} Spread',
                    'prob': analysis['spread_analysis']['prob_cover'],
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
            elif max_ev == analysis['spread_analysis']['ev_away']:
                picks.append({
                    'nivel': 6,
                    'mercado': f'+EV {away} Spread',
                    'prob': 1 - analysis['spread_analysis']['prob_cover'],
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
            elif max_ev == analysis['totals_analysis']['ev_over']:
                picks.append({
                    'nivel': 6,
                    'mercado': '+EV Over',
                    'prob': analysis['totals_analysis']['prob_over'],
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
            elif max_ev == analysis['totals_analysis']['ev_under']:
                picks.append({
                    'nivel': 6,
                    'mercado': '+EV Under',
                    'prob': analysis['totals_analysis']['prob_under'],
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
            elif max_ev == analysis['moneyline_analysis']['ev_home']:
                picks.append({
                    'nivel': 6,
                    'mercado': f'+EV {home} Moneyline',
                    'prob': analysis['moneyline_analysis']['home_win_prob'],
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
            elif max_ev == analysis['moneyline_analysis']['ev_away']:
                picks.append({
                    'nivel': 6,
                    'mercado': f'+EV {away} Moneyline',
                    'prob': analysis['moneyline_analysis']['away_win_prob'],
                    'tipo': 'value',
                    'ev': max_ev,
                    'detalle': f"Valor esperado +{max_ev:.1%}"
                })
        
        return picks
