"""
SELECTOR JERÁRQUICO UNIFICADO - Decide la mejor apuesta según umbrales dinámicos
Integrado con tu estructura existente
"""

import numpy as np

class SelectorMejorOpcionJerarquico:
    """Selector que elige la mejor opción según jerarquía y umbrales"""
    
    # Umbrales por deporte (puedes modificarlos)
    UMBRALES = {
        'futbol': {
            'over_1.5_pt': 0.62,      # Over 1.5 1er tiempo
            'over_3.5': 0.60,         # Over 3.5 goles
            'btts': 0.60,             # Ambos anotan
            'over_general': 0.55,     # Over 1.5/2.5/3.5
            'ml': 0.58,               # Moneyline
            'combo': 0.55             # Combo victoria + over
        },
        'nba': {
            'handicap': 0.60,         # Spread / Handicap
            'ou': 0.60,               # Over/Under
            'ml': 0.57,               # Moneyline
            'player_prop': 0.58       # Props de jugadores
        },
        'mlb': {
            'runline': 0.60,          # Run Line
            'ou': 0.60,               # Over/Under
            'ml': 0.57,               # Moneyline
            'homerun_prop': 0.58      # Props de HR
        }
    }
    
    @classmethod
    def seleccionar(cls, probs_dict, deporte="futbol", equipos=None):
        """
        Selecciona la mejor apuesta según jerarquía
        
        Args:
            probs_dict: dict con probabilidades calculadas
            deporte: "futbol", "nba", "mlb"
            equipos: tuple (local, visitante) para nombres
        
        Returns:
            dict con pick, probabilidad, confianza
        """
        u = cls.UMBRALES.get(deporte, cls.UMBRALES['futbol'])
        local, visitante = equipos or ("Local", "Visitante")
        
        # ========== FÚTBOL ==========
        if deporte == 'futbol':
            # 1. Over 1.5 1er Tiempo
            if probs_dict.get('over_1.5_pt', 0) >= u['over_1.5_pt']:
                return {
                    'pick': 'Over 1.5 1er Tiempo',
                    'probabilidad': round(probs_dict['over_1.5_pt'] * 100, 1),
                    'confianza': int(probs_dict['over_1.5_pt'] * 100),
                    'tipo': 'OVER_1.5_PT'
                }
            
            # 2. Over 3.5 Goles
            if probs_dict.get('over_3.5', 0) >= u['over_3.5']:
                return {
                    'pick': 'Over 3.5 Goles',
                    'probabilidad': round(probs_dict['over_3.5'] * 100, 1),
                    'confianza': int(probs_dict['over_3.5'] * 100),
                    'tipo': 'OVER_3.5'
                }
            
            # 3. BTTS (Ambos Anotan)
            if probs_dict.get('btts', 0) >= u['btts']:
                return {
                    'pick': 'Ambos Equipos Anotan (BTTS)',
                    'probabilidad': round(probs_dict['btts'] * 100, 1),
                    'confianza': int(probs_dict['btts'] * 100),
                    'tipo': 'BTTS'
                }
            
            # 4. Over general (el más fuerte entre 1.5, 2.5, 3.5)
            overs = [
                ('Over 1.5', probs_dict.get('over_1.5', 0)),
                ('Over 2.5', probs_dict.get('over_2.5', 0)),
                ('Over 3.5', probs_dict.get('over_3.5', 0))
            ]
            best_over = max(overs, key=lambda x: x[1])
            if best_over[1] >= u['over_general']:
                return {
                    'pick': best_over[0],
                    'probabilidad': round(best_over[1] * 100, 1),
                    'confianza': int(best_over[1] * 100),
                    'tipo': best_over[0].replace(' ', '_')
                }
            
            # 5. Moneyline Local
            if probs_dict.get('local', 0) >= u['ml']:
                return {
                    'pick': f"Gana {local}",
                    'probabilidad': round(probs_dict['local'] * 100, 1),
                    'confianza': int(probs_dict['local'] * 100),
                    'tipo': 'ML_LOCAL'
                }
            
            # 6. Moneyline Visitante
            if probs_dict.get('visitante', 0) >= u['ml']:
                return {
                    'pick': f"Gana {visitante}",
                    'probabilidad': round(probs_dict['visitante'] * 100, 1),
                    'confianza': int(probs_dict['visitante'] * 100),
                    'tipo': 'ML_VISIT'
                }
            
            # 7. Combo (Victoria + Over 2.5)
            if probs_dict.get('combo', 0) >= u['combo']:
                return {
                    'pick': f"Combo: {local} gana + Over 2.5",
                    'probabilidad': round(probs_dict['combo'] * 100, 1),
                    'confianza': int(probs_dict['combo'] * 100),
                    'tipo': 'COMBO'
                }
        
        # ========== NBA ==========
        elif deporte == 'nba':
            # 1. Handicap / Spread
            if probs_dict.get('handicap', 0) >= u['handicap']:
                return {
                    'pick': f"Spread {probs_dict.get('spread_equipo', '')}",
                    'probabilidad': round(probs_dict['handicap'] * 100, 1),
                    'confianza': int(probs_dict['handicap'] * 100),
                    'tipo': 'SPREAD'
                }
            
            # 2. Over/Under
            if probs_dict.get('ou', 0) >= u['ou']:
                direccion = "OVER" if probs_dict.get('ou_direccion', 'over') == 'over' else "UNDER"
                return {
                    'pick': f"{direccion} {probs_dict.get('linea_ou', 225)}",
                    'probabilidad': round(probs_dict['ou'] * 100, 1),
                    'confianza': int(probs_dict['ou'] * 100),
                    'tipo': 'OVER_UNDER'
                }
            
            # 3. Moneyline
            if probs_dict.get('ml', 0) >= u['ml']:
                ganador = local if probs_dict.get('ml_local', 0.5) > 0.5 else visitante
                return {
                    'pick': f"Gana {ganador}",
                    'probabilidad': round(probs_dict['ml'] * 100, 1),
                    'confianza': int(probs_dict['ml'] * 100),
                    'tipo': 'ML'
                }
            
            # 4. Player Props (base para futuro)
            if probs_dict.get('player_prop', 0) >= u['player_prop']:
                return {
                    'pick': f"Player Prop: {probs_dict.get('prop_jugador', '')}",
                    'probabilidad': round(probs_dict['player_prop'] * 100, 1),
                    'confianza': int(probs_dict['player_prop'] * 100),
                    'tipo': 'PROP'
                }
        
        # ========== MLB ==========
        elif deporte == 'mlb':
            # 1. Run Line
            if probs_dict.get('runline', 0) >= u['runline']:
                return {
                    'pick': f"Run Line {probs_dict.get('runline_equipo', '')}",
                    'probabilidad': round(probs_dict['runline'] * 100, 1),
                    'confianza': int(probs_dict['runline'] * 100),
                    'tipo': 'RUN_LINE'
                }
            
            # 2. Over/Under
            if probs_dict.get('ou', 0) >= u['ou']:
                direccion = "OVER" if probs_dict.get('ou_direccion', 'over') == 'over' else "UNDER"
                return {
                    'pick': f"{direccion} {probs_dict.get('linea_ou', 8)} carreras",
                    'probabilidad': round(probs_dict['ou'] * 100, 1),
                    'confianza': int(probs_dict['ou'] * 100),
                    'tipo': 'OVER_UNDER'
                }
            
            # 3. Moneyline
            if probs_dict.get('ml', 0) >= u['ml']:
                ganador = local if probs_dict.get('ml_local', 0.5) > 0.5 else visitante
                return {
                    'pick': f"Gana {ganador}",
                    'probabilidad': round(probs_dict['ml'] * 100, 1),
                    'confianza': int(probs_dict['ml'] * 100),
                    'tipo': 'ML'
                }
        
        # Sin pick claro
        return {
            'pick': 'SIN VALOR CLARO',
            'probabilidad': 0,
            'confianza': 0,
            'tipo': 'NONE'
        }
    
    @staticmethod
    def calcular_player_prop_prob(promedio, desviacion, linea_prop=25.5):
        """Calcula probabilidad de OVER en props de jugadores"""
        from scipy.stats import norm
        z = (linea_prop - promedio) / (desviacion + 0.01)
        prob_over = 1 - norm.cdf(z)
        return round(prob_over, 4)


# Mantener compatibilidad con importaciones existentes
seleccionar_mejor_opcion = SelectorMejorOpcionJerarquico.seleccionar
