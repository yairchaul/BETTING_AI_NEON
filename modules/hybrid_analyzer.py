# modules/hybrid_analyzer.py
import streamlit as st
import numpy as np
from modules.smart_searcher import SmartSearcher
from modules.real_analyzer import RealAnalyzer
from modules.groq_analyzer import GroqAnalyzer
from modules.groq_vision import GroqVisionParser

class HybridAnalyzer:
    """
    Analizador que combina:
    - Football API (cuando encuentra los equipos)
    - Groq AI (cuando no encuentra o como respaldo)
    - Búsqueda inteligente en conocimiento de Groq
    """
    
    def __init__(self):
        self.searcher = SmartSearcher()
        self.real_analyzer = RealAnalyzer()
        self.groq_analyzer = GroqAnalyzer() if st.secrets.get("GROQ_API_KEY") else None
        self.groq_vision = GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None
    
    def analyze_match(self, home_name, away_name, odds_data=None):
        """
        Análisis híbrido: intenta APIs, si falla usa Groq
        """
        result = {
            'home_team': home_name,
            'away_team': away_name,
            'home_found': False,
            'away_found': False,
            'markets': [],
            'probabilidades': {},
            'source': 'unknown'
        }
        
        # INTENTO 1: Buscar en APIs tradicionales
        with st.spinner(f"🔍 Buscando {home_name} en APIs..."):
            home_team = self.searcher.find_team(home_name)
        
        with st.spinner(f"🔍 Buscando {away_name} en APIs..."):
            away_team = self.searcher.find_team(away_name)
        
        if home_team and away_team:
            # Tenemos los equipos, obtener stats reales
            analysis = self.real_analyzer.analyze_match(home_name, away_name)
            analysis['source'] = 'API Sports Database'
            return analysis
        
        # INTENTO 2: Usar Groq con análisis inteligente
        if self.groq_analyzer:
            st.info(f"🤖 Usando Groq AI para analizar {home_name} vs {away_name}")
            
            # Intentar con análisis completo primero
            groq_result = self.groq_analyzer.analyze_match(home_name, away_name, odds_data)
            
            if not groq_result:
                # Si falla, intentar con búsqueda
                groq_result = self.groq_analyzer.analyze_with_search(home_name, away_name, odds_data)
            
            if groq_result:
                # Convertir resultado de Groq a formato de mercados
                markets = []
                
                # Mapeo de resultados de Groq a mercados
                mercado_mapping = [
                    ('resultado_local', 'Gana Local', '1X2'),
                    ('resultado_empate', 'Empate', '1X2'),
                    ('resultado_visitante', 'Gana Visitante', '1X2'),
                    ('btts', 'Ambos anotan (BTTS)', 'BTTS'),
                    ('over_1_5', 'Over 1.5 goles', 'Totales'),
                    ('over_2_5', 'Over 2.5 goles', 'Totales'),
                    ('over_3_5', 'Over 3.5 goles', 'Totales'),
                    ('over_4_5', 'Over 4.5 goles', 'Totales (Especial)'),
                    ('over_5_5', 'Over 5.5 goles', 'Totales (Especial)'),
                    ('over_0_5_1t', 'Over 0.5 goles (1T)', 'Primer Tiempo'),
                    ('over_1_5_1t', 'Over 1.5 goles (1T)', 'Primer Tiempo'),
                ]
                
                for key, nombre, categoria in mercado_mapping:
                    if key in groq_result and groq_result[key] is not None:
                        markets.append({
                            'name': nombre,
                            'prob': float(groq_result[key]),
                            'category': categoria
                        })
                
                # Si no hay suficientes mercados, agregar algunos por defecto
                if len(markets) < 3:
                    markets.extend([
                        {'name': 'Over 0.5 goles', 'prob': 0.95, 'category': 'Totales'},
                        {'name': 'Over 1.5 goles', 'prob': 0.80, 'category': 'Totales'},
                        {'name': 'Over 0.5 goles (1T)', 'prob': 0.70, 'category': 'Primer Tiempo'},
                    ])
                
                # Calcular promedio de goles
                avg_goals = groq_result.get('over_2_5', 0.5) * 3
                if avg_goals < 2.0:
                    avg_goals = 2.5
                
                result['markets'] = sorted(markets, key=lambda x: x['prob'], reverse=True)
                result['home_found'] = True
                result['away_found'] = True
                result['source'] = f"Groq AI - {groq_result.get('liga', 'Análisis inteligente')}"
                result['probabilidades'] = {'goles_promedio': avg_goals}
                result['groq_analysis'] = groq_result
                
                return result
        
        # INTENTO 3: Fallback a genérico
        st.warning(f"⚠️ Usando estadísticas genéricas para {home_name} vs {away_name}")
        generic = self.real_analyzer._generate_generic_analysis(home_name, away_name)
        generic['source'] = 'Estadísticas genéricas'
        return generic
    
    def analyze_image_with_groq(self, image_bytes):
        """
        Usa Groq Vision para extraer partidos directamente de la imagen
        """
        if self.groq_vision:
            try:
                matches = self.groq_vision.extract_matches_with_vision(image_bytes)
                if matches:
                    return matches
            except Exception as e:
                st.warning(f"Groq Vision falló: {e}")
        
        return None


# Función de utilidad para convertir odds americanas a decimales
def american_to_decimal(american_odd):
    """Convierte odds americanas (+150, -200) a decimales"""
    try:
        if isinstance(american_odd, str):
            if american_odd.startswith('+'):
                return (int(american_odd[1:]) / 100) + 1
            elif american_odd.startswith('-'):
                return (100 / abs(int(american_odd))) + 1
        return float(american_odd)
    except:
        return 2.0
