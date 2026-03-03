# modules/value_detector.py
import streamlit as st

class ValueDetector:
    """
    Detector de apuestas de valor (value betting)
    Usa Valor Esperado (EV) como métrica principal
    """
    
    def __init__(self):
        pass
    
    def american_to_decimal(self, american_odd):
        """Convierte odds americanas a decimales"""
        try:
            if american_odd == 'N/A' or not american_odd:
                return None
            
            odd_str = str(american_odd).strip()
            
            if odd_str.startswith('+'):
                return (int(odd_str[1:]) / 100) + 1
            elif odd_str.startswith('-'):
                return (100 / abs(int(odd_str))) + 1
            else:
                return float(odd_str)
        except:
            return None
    
    def calculate_implied_probability(self, decimal_odd):
        """Calcula probabilidad implícita de una odd decimal"""
        if not decimal_odd or decimal_odd <= 0:
            return None
        return 1 / decimal_odd
    
    def detect_value(self, our_probability, market_odds, threshold=0.05):
        """
        Detecta si hay valor usando Valor Esperado (EV)
        EV = (Probabilidad * Cuota) - 1
        """
        if not market_odds or market_odds == 'N/A':
            return {
                'has_value': False,
                'ev': 0,
                'fair_odd': None,
                'decimal_odd': None,
                'recommendation': 'No hay odds de mercado'
            }
        
        decimal_odd = self.american_to_decimal(market_odds)
        if not decimal_odd:
            return {
                'has_value': False,
                'ev': 0,
                'fair_odd': None,
                'decimal_odd': None,
                'recommendation': 'Odd inválida'
            }
        
        # Fair odd basada en nuestra probabilidad
        fair_odd = 1 / our_probability if our_probability > 0 else 0
        
        # VALOR ESPERADO (EV) - Fórmula correcta
        ev = (our_probability * decimal_odd) - 1
        
        # Hay valor si EV > umbral
        has_value = ev > threshold
        
        if has_value:
            recommendation = f"🔥 VALUE! EV: {ev:.1%}"
        elif ev > 0:
            recommendation = f"👍 Pequeño EV: {ev:.1%}"
        else:
            recommendation = f"👎 EV negativo: {ev:.1%}"
        
        return {
            'has_value': has_value,
            'ev': ev,
            'fair_odd': fair_odd,
            'decimal_odd': decimal_odd,
            'american_odd': market_odds,
            'recommendation': recommendation
        }
    
    def get_best_value_bet(self, match_analysis, match_odds):
        """Obtiene la mejor apuesta de valor para un partido"""
        results = []
        
        # Mapeo de mercados
        markets_to_check = [
            ('Gana Local', 0),
            ('Empate', 1),
            ('Gana Visitante', 2),
        ]
        
        for market_name, idx in markets_to_check:
            # Buscar la probabilidad
            market_prob = None
            for m in match_analysis.get('markets', []):
                if market_name.lower() in m['name'].lower():
                    market_prob = m['prob']
                    break
            
            if not market_prob:
                continue
            
            # Obtener la odd
            if 'all_odds' in match_odds and len(match_odds['all_odds']) > idx:
                market_odd = match_odds['all_odds'][idx]
            else:
                market_odd = 'N/A'
            
            value_result = self.detect_value(market_prob, market_odd)
            value_result['market'] = market_name
            results.append(value_result)
        
        # Filtrar por EV positivo
        value_bets = [r for r in results if r.get('ev', 0) > 0.05]
        
        if value_bets:
            value_bets.sort(key=lambda x: x['ev'], reverse=True)
            best = value_bets[0]
            best['type'] = 'value_bet'
            return best
        elif results:
            results.sort(key=lambda x: x.get('fair_odd', 0), reverse=True)
            best = results[0]
            best['type'] = 'probabilidad'
            return best
        
        return None
