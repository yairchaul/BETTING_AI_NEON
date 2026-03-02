# modules/pro_analyzer.py
import streamlit as st
import numpy as np
from modules.team_knowledge import TeamKnowledge
from modules.inference_engine import InferenceEngine
from modules.groq_enhancer import GroqEnhancer
from modules.smart_searcher import SmartSearcher
from modules.real_analyzer import RealAnalyzer

class ProAnalyzer:
    """
    Analizador profesional que combina:
    - Conocimiento de equipos y ligas
    - Reglas de apostador
    - Datos de APIs
    - Groq como respaldo
    """
    
    def __init__(self):
        self.knowledge = TeamKnowledge()
        self.engine = InferenceEngine(self.knowledge)
        self.searcher = SmartSearcher()
        self.real = RealAnalyzer()
        self.groq = GroqEnhancer() if st.secrets.get("GROQ_API_KEY") else None
    
    def analyze_match(self, home_name, away_name, odds_data=None):
        """
        Análisis completo de un partido
        """
        st.info(f"🔍 Analizando {home_name} vs {away_name}...")
        
        # PASO 1: Intentar obtener datos de APIs
        home_team = self.searcher.find_team(home_name)
        away_team = self.searcher.find_team(away_name)
        
        # PASO 2: Obtener estadísticas reales si es posible
        home_stats = {}
        away_stats = {}
        league_data = self.knowledge.leagues_data['default']
        
        if home_team and away_team:
            # Tenemos los equipos, obtener stats reales
            analysis = self.real.analyze_match(home_name, away_name)
            markets = analysis['markets']
            
            # Extraer estadísticas
            home_stats = self._extract_stats_from_markets(markets, 'home')
            away_stats = self._extract_stats_from_markets(markets, 'away')
            
            # Identificar liga
            league_name, league_data = self.knowledge.identify_league(home_team.get('name', home_name))
            
            # Aplicar reglas del apostador
            best_bet = self.engine.get_best_bet(
                home_name, away_name, home_stats, away_stats, league_data
            )
            
            return {
                'home_team': home_team.get('name', home_name),
                'away_team': away_team.get('name', away_name),
                'markets': markets,
                'best_bet': best_bet,
                'source': 'API + Reglas de apostador',
                'confidence': best_bet['confidence']
            }
        
        # PASO 3: Si no hay datos de API, usar Groq
        elif self.groq:
            st.warning(f"🤔 Equipos no encontrados en API, consultando Groq...")
            groq_analysis = self.groq.analyze_unknown_teams(home_name, away_name)
            
            if groq_analysis:
                # Crear mercados basados en análisis de Groq
                markets = self._create_markets_from_groq(groq_analysis)
                
                best_bet = {
                    'market': groq_analysis.get('mejor_apuesta', 'Over 1.5 goles'),
                    'confidence': groq_analysis.get('confianza', 'MEDIA'),
                    'reason': groq_analysis.get('explicacion', 'Análisis de Groq'),
                    'probability': groq_analysis.get('probabilidad_estimada', 60) / 100
                }
                
                return {
                    'home_team': home_name,
                    'away_team': away_name,
                    'markets': markets,
                    'best_bet': best_bet,
                    'source': f"Groq AI - {groq_analysis.get('liga', 'Liga desconocida')}",
                    'confidence': best_bet['confidence'],
                    'groq_details': groq_analysis
                }
        
        # PASO 4: Fallback a análisis genérico
        generic = self.real._generate_generic_analysis(home_name, away_name)
        
        best_bet = {
            'market': 'Over 1.5 goles',
            'confidence': 'BAJA',
            'reason': 'Sin datos específicos, apuesta conservadora',
            'probability': 0.70
        }
        
        return {
            'home_team': home_name,
            'away_team': away_name,
            'markets': generic['markets'],
            'best_bet': best_bet,
            'source': 'Estadísticas genéricas',
            'confidence': 'BAJA'
        }
    
    def _extract_stats_from_markets(self, markets, team_type):
        """Extrae estadísticas de los mercados"""
        stats = {
            'goles': 1.5,
            'recibe': 1.2,
            'victorias': 50,
            'btts': 50
        }
        
        # Buscar mercados que den pistas
        for m in markets:
            if 'Local' in m['name'] and team_type == 'home':
                stats['victorias'] = m['prob'] * 100
            elif 'Visitante' in m['name'] and team_type == 'away':
                stats['victorias'] = m['prob'] * 100
            elif 'Over 2.5' in m['name']:
                stats['goles'] = 1.5 + (m['prob'] * 2)
        
        return stats
    
    def _create_markets_from_groq(self, groq_analysis):
        """Crea mercados a partir del análisis de Groq"""
        markets = []
        
        # Mapeo básico
        markets.append({
            'name': 'Gana Local',
            'prob': 0.40,
            'category': '1X2'
        })
        markets.append({
            'name': 'Empate',
            'prob': 0.25,
            'category': '1X2'
        })
        markets.append({
            'name': 'Gana Visitante',
            'prob': 0.35,
            'category': '1X2'
        })
        
        # Ajustar según análisis
        nivel_local = groq_analysis.get('nivel_local', 'MEDIANO')
        nivel_visit = groq_analysis.get('nivel_visitante', 'MEDIANO')
        
        if nivel_local == 'GRANDE' and nivel_visit == 'PEQUEÑO':
            markets[0]['prob'] = 0.70
            markets[2]['prob'] = 0.15
        
        # Totales
        goles_prom = groq_analysis.get('goles_promedio_liga', 2.5)
        markets.append({
            'name': 'Over 1.5 goles',
            'prob': min(0.95, goles_prom / 2),
            'category': 'Totales'
        })
        markets.append({
            'name': 'Over 2.5 goles',
            'prob': min(0.80, (goles_prom - 1.5) / 2),
            'category': 'Totales'
        })
        markets.append({
            'name': 'Ambos anotan (BTTS)',
            'prob': 0.50,
            'category': 'BTTS'
        })
        
        return sorted(markets, key=lambda x: x['prob'], reverse=True)
