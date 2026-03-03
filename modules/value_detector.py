# modules/value_detector.py
import streamlit as st
import numpy as np

class ValueDetector:
    """
    Detector de apuestas de valor (value betting)
    Compara probabilidades de IA vs cuotas reales del mercado
    Incluye sistema de High Value y cálculo de stake óptimo
    """
    
    def __init__(self):
        self.threshold_ev = 0.05
    
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
    
    def decimal_to_american(self, decimal_odd):
        """Convierte odds decimales a americanas"""
        try:
            if decimal_odd >= 2.0:
                return f"+{int((decimal_odd - 1) * 100)}"
            else:
                return f"-{int(100 / (decimal_odd - 1))}"
        except:
            return "N/A"
    
    def calculate_implied_probability(self, decimal_odd):
        """Calcula probabilidad implícita de una odd decimal"""
        if not decimal_odd or decimal_odd <= 0:
            return None
        return 1 / decimal_odd
    
    def calculate_kelly_stake(self, prob, odds, bankroll=1000, fraction=0.25):
        """
        Calcula stake óptimo usando Kelly Criterion fraccionado
        """
        b = odds - 1
        if b <= 0:
            return 0
        
        p = prob
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        optimal_stake = bankroll * kelly_fraction * fraction
        
        return max(0, min(optimal_stake, bankroll * 0.1))
    
    def detect_value(self, our_probability, market_odds, threshold_ev=0.05, bankroll=1000):
        """
        Detecta si hay valor usando Valor Esperado (EV)
        EV = (Probabilidad * Cuota) - 1
        """
        if not market_odds or market_odds == 'N/A':
            return {
                'has_value': False,
                'ev': 0,
                'high_value': False,
                'fair_odd': None,
                'decimal_odd': None,
                'stake': 0,
                'confidence': 'BAJA',
                'recommendation': 'No hay odds de mercado'
            }
        
        decimal_odd = self.american_to_decimal(market_odds)
        if not decimal_odd:
            return {
                'has_value': False,
                'ev': 0,
                'high_value': False,
                'fair_odd': None,
                'decimal_odd': None,
                'stake': 0,
                'confidence': 'BAJA',
                'recommendation': 'Odd inválida'
            }
        
        fair_odd = 1 / our_probability if our_probability > 0 else 0
        implied_prob = self.calculate_implied_probability(decimal_odd)
        
        # VALOR ESPERADO (EV)
        ev = (our_probability * decimal_odd) - 1
        
        high_value = ev > 0.10
        stake = self.calculate_kelly_stake(our_probability, decimal_odd, bankroll)
        
        if ev > 0.15:
            confidence = 'ALTA'
        elif ev > 0.08:
            confidence = 'MEDIA'
        elif ev > 0.03:
            confidence = 'BAJA'
        else:
            confidence = 'MUY BAJA'
        
        has_value = ev > threshold_ev
        
        if has_value:
            if high_value:
                recommendation = f"🔥 HIGH VALUE! EV: {ev:.1%} | Stake: ${stake:.2f}"
            else:
                recommendation = f"📈 VALUE! EV: {ev:.1%} | Stake: ${stake:.2f}"
        elif ev > 0:
            recommendation = f"👍 Pequeño EV: {ev:.1%} (bajo umbral)"
        else:
            recommendation = f"👎 EV negativo: {ev:.1%}"
        
        return {
            'has_value': has_value,
            'high_value': high_value,
            'ev': ev,
            'fair_odd': fair_odd,
            'implied_probability': implied_prob,
            'decimal_odd': decimal_odd,
            'american_odd': market_odds,
            'stake': round(stake, 2),
            'confidence': confidence,
            'recommendation': recommendation
        }
    
    def get_best_value_bet(self, match_analysis, match_odds, bankroll=1000):
        """Obtiene la mejor apuesta de valor para un partido"""
        results = []
        
        market_map = [
            ('Gana Local', 0),
            ('Empate', 1),
            ('Gana Visitante', 2)
        ]
        
        for market_name, idx in market_map:
            # Buscar probabilidad en el análisis
            market_prob = None
            for m in match_analysis.get('markets', []):
                if market_name.lower() in m['name'].lower():
                    market_prob = m['prob']
                    break
            
            if not market_prob:
                continue
            
            # Obtener odd de la imagen
            all_odds = match_odds.get('all_odds', [])
            market_odd = all_odds[idx] if len(all_odds) > idx else 'N/A'
            
            value_result = self.detect_value(market_prob, market_odd, bankroll=bankroll)
            value_result['market'] = market_name
            value_result['market_prob'] = market_prob
            results.append(value_result)
        
        if not results:
            return None
        
        # Ordenar: HIGH VALUE > VALUE > Probabilidad
        results.sort(key=lambda x: (
            x.get('high_value', False),
            x.get('has_value', False),
            x['ev']
        ), reverse=True)
        
        best = results[0]
        if best.get('high_value'):
            best['type'] = 'high_value'
        elif best.get('has_value'):
            best['type'] = 'value_bet'
        else:
            best['type'] = 'probabilidad'
        
        return best
