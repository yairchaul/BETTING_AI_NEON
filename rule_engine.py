"""
Motor de reglas - 7 REGLAS JERÁRQUICAS para selección de picks
"""
from typing import Dict, List, Optional

class RuleEngine:
    """Aplica las 7 reglas en orden de prioridad"""
    
    def __init__(self):
        self.reglas = [
            self._regla_1_over_15_1t,
            self._regla_2_over_35_favorito,
            self._regla_3_btts,
            self._regla_4_equilibrado,
            self._regla_5_favorito_local,
            self._regla_6_favorito_visitante,
            self._regla_7_default
        ]
    
    def aplicar_reglas(self, evento, m: Dict) -> List[Dict]:
        """Aplica reglas en orden y retorna picks"""
        for i, regla in enumerate(self.reglas, 1):
            picks = regla(evento, m)
            if picks:
                for pick in picks:
                    pick['nivel'] = i
                return picks
        return []
    
    def _regla_1_over_15_1t(self, evento, m):
        """Regla 1: Over 1.5 Primer Tiempo > 60%"""
        if m.get('over_1_5_1t', 0) > 0.60:
            return [{
                'mercado': 'Over 1.5 1T',
                'probabilidad': m['over_1_5_1t'],
                'descripcion': 'Over 1.5 Primer Tiempo',
                'odds': self._calc_odds(m['over_1_5_1t'])
            }]
        return None
    
    def _regla_2_over_35_favorito(self, evento, m):
        """Regla 2: Over 3.5 > 60% + Favorito >55%"""
        if m.get('over_3_5', 0) > 0.60:
            picks = []
            if m.get('prob_local', 0) > 0.55:
                picks.append({
                    'mercado': f'Gana {evento.equipo_local}',
                    'probabilidad': m['prob_local'],
                    'descripcion': f'Victoria {evento.equipo_local[:20]}',
                    'odds': evento.odds_local
                })
                picks.append({
                    'mercado': 'Over 3.5',
                    'probabilidad': m['over_3_5'],
                    'descripcion': 'Más de 3.5 goles',
                    'odds': self._calc_odds(m['over_3_5'])
                })
                return picks
            elif m.get('prob_visitante', 0) > 0.55:
                picks.append({
                    'mercado': f'Gana {evento.equipo_visitante}',
                    'probabilidad': m['prob_visitante'],
                    'descripcion': f'Victoria {evento.equipo_visitante[:20]}',
                    'odds': evento.odds_visitante
                })
                picks.append({
                    'mercado': 'Over 3.5',
                    'probabilidad': m['over_3_5'],
                    'descripcion': 'Más de 3.5 goles',
                    'odds': self._calc_odds(m['over_3_5'])
                })
                return picks
        return None
    
    def _regla_3_btts(self, evento, m):
        """Regla 3: BTTS > 60%"""
        if m.get('btts_si', 0) > 0.60:
            return [{
                'mercado': 'BTTS Sí',
                'probabilidad': m['btts_si'],
                'descripcion': 'Ambos equipos anotan',
                'odds': self._calc_odds(m['btts_si'])
            }]
        return None
    
    def _regla_4_equilibrado(self, evento, m):
        """Regla 4: Partido equilibrado → mejor over cerca de 55%"""
        prob_local = m.get('prob_local', 0)
        prob_visitante = m.get('prob_visitante', 0)
        
        if prob_local < 0.55 and prob_visitante < 0.55:
            overs = [
                ('Over 1.5', m.get('over_1_5', 0)),
                ('Over 2.5', m.get('over_2_5', 0)),
                ('Over 3.5', m.get('over_3_5', 0))
            ]
            overs_validos = [(n, p) for n, p in overs if p > 0.55]
            
            if overs_validos:
                mejor = min(overs_validos, key=lambda x: abs(x[1] - 0.55))
                return [{
                    'mercado': mejor[0],
                    'probabilidad': mejor[1],
                    'descripcion': f'{mejor[0]} (valor óptimo)',
                    'odds': self._calc_odds(mejor[1])
                }]
            else:
                mejor = max(overs, key=lambda x: x[1])
                return [{
                    'mercado': mejor[0],
                    'probabilidad': mejor[1],
                    'descripcion': f'{mejor[0]} (mayor prob)',
                    'odds': self._calc_odds(mejor[1])
                }]
        return None
    
    def _regla_5_favorito_local(self, evento, m):
        """Regla 5: Favorito local + mejor over"""
        prob_local = m.get('prob_local', 0)
        prob_visitante = m.get('prob_visitante', 0)
        
        if prob_local > 0.50 and prob_visitante < 0.40:
            picks = [{
                'mercado': f'Gana {evento.equipo_local}',
                'probabilidad': prob_local,
                'descripcion': f'Victoria {evento.equipo_local[:20]}',
                'odds': evento.odds_local
            }]
            overs = [
                ('Over 1.5', m.get('over_1_5', 0)),
                ('Over 2.5', m.get('over_2_5', 0)),
                ('Over 3.5', m.get('over_3_5', 0))
            ]
            mejor = max(overs, key=lambda x: x[1])
            picks.append({
                'mercado': mejor[0],
                'probabilidad': mejor[1],
                'descripcion': f'{mejor[0]} (combinado)',
                'odds': self._calc_odds(mejor[1])
            })
            return picks
        return None
    
    def _regla_6_favorito_visitante(self, evento, m):
        """Regla 6: Favorito visitante + mejor over"""
        prob_local = m.get('prob_local', 0)
        prob_visitante = m.get('prob_visitante', 0)
        
        if prob_visitante > 0.50 and prob_local < 0.40:
            picks = [{
                'mercado': f'Gana {evento.equipo_visitante}',
                'probabilidad': prob_visitante,
                'descripcion': f'Victoria {evento.equipo_visitante[:20]}',
                'odds': evento.odds_visitante
            }]
            overs = [
                ('Over 1.5', m.get('over_1_5', 0)),
                ('Over 2.5', m.get('over_2_5', 0)),
                ('Over 3.5', m.get('over_3_5', 0))
            ]
            mejor = max(overs, key=lambda x: x[1])
            picks.append({
                'mercado': mejor[0],
                'probabilidad': mejor[1],
                'descripcion': f'{mejor[0]} (combinado)',
                'odds': self._calc_odds(mejor[1])
            })
            return picks
        return None
    
    def _regla_7_default(self, evento, m):
        """Regla 7: Default - mejor over"""
        overs = [
            ('Over 1.5', m.get('over_1_5', 0)),
            ('Over 2.5', m.get('over_2_5', 0)),
            ('Over 3.5', m.get('over_3_5', 0))
        ]
        mejor = max(overs, key=lambda x: x[1])
        return [{
            'mercado': mejor[0],
            'probabilidad': mejor[1],
            'descripcion': f'{mejor[0]} (default)',
            'odds': self._calc_odds(mejor[1])
        }]
    
    def _calc_odds(self, prob):
        """Calcula odds decimal de probabilidad"""
        if prob <= 0:
            return 2.0
        return round(1 / prob * 0.95, 2)
