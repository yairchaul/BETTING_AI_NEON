import streamlit as st
import numpy as np
import re

class ValueDetector:
    """
    Detector de apuestas de valor (value betting) OPTIMIZADO
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

    def calculate_kelly_stake(self, prob, odds, bankroll=1000, fraction=0.25):
        """Calcula stake óptimo usando Kelly Criterion fraccionado"""
        b = odds - 1
        if b <= 0: return 0
        p = prob
        q = 1 - p
        kelly_fraction = (b * p - q) / b
        optimal_stake = bankroll * kelly_fraction * fraction
        return max(0, min(optimal_stake, bankroll * 0.1)) # Máximo 10% del bankroll

    def detect_value(self, our_probability, market_odds, threshold_ev=0.05, bankroll=1000):
        if not market_odds or market_odds == 'N/A':
            return {'has_value': False, 'ev': 0, 'stake': 0, 'recommendation': 'Sin cuotas'}

        decimal_odd = self.american_to_decimal(market_odds)
        if not decimal_odd:
            return {'has_value': False, 'ev': 0, 'stake': 0, 'recommendation': 'Odd inválida'}

        fair_odd = 1 / our_probability if our_probability > 0 else 0
        ev = (our_probability * decimal_odd) - 1
        
        high_value = ev > 0.10
        stake = self.calculate_kelly_stake(our_probability, decimal_odd, bankroll)
        
        confidence = 'ALTA' if ev > 0.15 else 'MEDIA' if ev > 0.08 else 'BAJA'
        has_value = ev > threshold_ev

        return {
            'has_value': has_value,
            'high_value': high_value,
            'ev': ev,
            'fair_odd': fair_odd,
            'decimal_odd': decimal_odd,
            'stake': round(stake, 2),
            'confidence': confidence,
            'recommendation': f"EV: {ev:.1%} | Stake: ${stake:.2f}"
        }

    def get_best_value_bet(self, match_analysis, match_odds, bankroll=1000):
        results = []
        # Mapeo de mercados
        market_map = [
            ('Gana Local', 0),
            ('Empate', 1),
            ('Gana Visitante', 2)
        ]
        
        for name, idx in market_map:
            # Buscar prob en el análisis de la IA
            prob = next((m['prob'] for m in match_analysis.get('markets', []) if name in m['name']), None)
            if prob:
                # Obtener cuota del OCR
                all_odds = match_odds.get('all_odds', [])
                market_odd = all_odds[idx] if len(all_odds) > idx else 'N/A'
                
                res = self.detect_value(prob, market_odd, bankroll=bankroll)
                res['market'] = name
                res['market_prob'] = prob
                results.append(res)
        
        if not results: return None
        # Priorizar High Value, luego Value, luego Probabilidad
        results.sort(key=lambda x: (x.get('high_value', 0), x.get('has_value', 0), x['ev']), reverse=True)
        
        best = results[0]
        if best.get('high_value'): best['type'] = 'high_value'
        elif best.get('has_value'): best['type'] = 'value_bet'
        else: best['type'] = 'probabilidad'
        
        return best
