 # modules/value_detector.py
import streamlit as st
import numpy as np

class ValueDetector:
    """
    Detector de apuestas de valor (value betting)
    Compara nuestra probabilidad calculada con las odds reales del mercado
    """
    
    def __init__(self):
        pass
    
    def american_to_decimal(self, american_odd):
        """Convierte odds americanas a decimales"""
        try:
            if american_odd == 'N/A' or not american_odd:
                return None
            
            # Convertir a string y limpiar
            odd_str = str(american_odd).strip()
            
            if odd_str.startswith('+'):
                # Ejemplo: +200 -> 3.00
                return (int(odd_str[1:]) / 100) + 1
            elif odd_str.startswith('-'):
                # Ejemplo: -150 -> 1.67
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
        Detecta si hay valor (edge) positivo
        threshold = 0.05 significa 5% de ventaja
        """
        if not market_odds or market_odds == 'N/A':
            return {
                'has_value': False,
                'edge': 0,
                'recommendation': 'No hay odds de mercado para comparar'
            }
        
        # Convertir odd americana a decimal
        decimal_odd = self.american_to_decimal(market_odds)
        if not decimal_odd:
            return {
                'has_value': False,
                'edge': 0,
                'recommendation': 'No se pudo convertir la odd'
            }
        
        # Calcular probabilidad implícita del mercado
        implied_prob = self.calculate_implied_probability(decimal_odd)
        
        # Calcular edge (ventaja)
        edge = our_probability - implied_prob
        
        # Determinar si hay valor
        has_value = edge > threshold
        
        # Generar recomendación
        if has_value:
            recommendation = f"🔥 VALUE BET! Tu probabilidad ({our_probability:.1%}) es {edge:.1%} mayor que la del mercado ({implied_prob:.1%})"
        elif edge > 0:
            recommendation = f"👍 Pequeña ventaja: {edge:.1%} (menor al umbral de {threshold:.1%})"
        else:
            recommendation = f"👎 Desventaja: {edge:.1%} - Mejor evitar"
        
        return {
            'has_value': has_value,
            'edge': edge,
            'implied_probability': implied_prob,
            'decimal_odd': decimal_odd,
            'recommendation': recommendation
        }
    
    def analyze_match_markets(self, match_analysis, match_odds):
        """
        Analiza todos los mercados de un partido en busca de valor
        """
        results = []
        
        # Mapeo de mercados a las odds correspondientes
        market_mapping = [
            ('Gana Local', 'all_odds', 0),
            ('Empate', 'all_odds', 1),
            ('Gana Visitante', 'all_odds', 2),
        ]
        
        for market_name, odds_key, odds_index in market_mapping:
            # Buscar la probabilidad de este mercado en el análisis
            market_prob = None
            for m in match_analysis.get('markets', []):
                if m['name'] == market_name:
                    market_prob = m['prob']
                    break
            
            if not market_prob:
                continue
            
            # Obtener la odd real de la imagen
            if odds_key in match_odds and len(match_odds[odds_key]) > odds_index:
                market_odd = match_odds[odds_key][odds_index]
            else:
                market_odd = 'N/A'
            
            # Detectar valor
            value_result = self.detect_value(market_prob, market_odd)
            value_result['market'] = market_name
            
            results.append(value_result)
        
        return results
    
    def get_best_value_bet(self, match_analysis, match_odds):
        """
        Obtiene la mejor apuesta de valor para un partido
        """
        results = self.analyze_match_markets(match_analysis, match_odds)
        
        # Filtrar solo las que tienen valor positivo
        value_bets = [r for r in results if r.get('has_value', False)]
        
        if value_bets:
            # Ordenar por edge (mayor a menor)
            value_bets.sort(key=lambda x: x.get('edge', 0), reverse=True)
            best = value_bets[0]
            best['type'] = 'value_bet'
            return best
        else:
            # Si no hay valor, devolver la de mayor probabilidad (como fallback)
            if results:
                results.sort(key=lambda x: x.get('implied_probability', 0), reverse=True)
                best = results[0]
                best['type'] = 'probabilidad'
                return best
        
        return None