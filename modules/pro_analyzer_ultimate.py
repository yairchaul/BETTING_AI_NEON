# modules/pro_analyzer_ultimate.py
import streamlit as st
import requests
import json
import numpy as np
from datetime import datetime
from modules.team_knowledge import TeamKnowledge
from modules.smart_searcher import SmartSearcher
from modules.montecarlo_pro import MonteCarloPro
from modules.elo_system import ELOSystem
from modules.xgboost_predictor import XGBoostPredictor
from math import exp, factorial

class ProAnalyzerUltimate:
    """
    Analizador profesional con cobertura GLOBAL de ligas + Monte Carlo + ELO + XGBoost
    """
    
    def __init__(self):
        self.knowledge = TeamKnowledge()
        self.searcher = SmartSearcher()
        self.montecarlo = MonteCarloPro(simulations=50000)
        self.elo = ELOSystem(k_factor=32, home_advantage=100)
        self.xgb = XGBoostPredictor()
        self.max_edge = 0.06  # máximo 6% diferencia vs mercado
        
        # Pesos para el modelo híbrido
        self.weights = {
            'market': 0.3,
            'poisson': 0.2,
            'elo': 0.2,
            'xgb': 0.3
        }
        
        # APIs disponibles
        self.apis = {
            'football_api': st.secrets.get("FOOTBALL_API_KEY", ""),
            'odds_api': st.secrets.get("ODDS_API_KEY", ""),
            'google_cse': {
                'key': st.secrets.get("GOOGLE_API_KEY", ""),
                'cx': st.secrets.get("GOOGLE_CSE_ID", "")
            }
        }
        
        # BASE DE DATOS COMPLETA DE LIGAS (TU BASE COMPLETA)
        self.leagues_db = self._build_complete_leagues_database()
        
        # Reglas de inferencia profesional (como respaldo)
        self.rules = self._build_universal_rules()
    
    def _build_complete_leagues_database(self):
        """Base de datos completa con TODAS las ligas del mundo"""
        return {
            # ============================================================================
            # MEXICO Y CENTROAMERICA
            # ============================================================================
            'Mexico Liga MX': {
                'pais': 'Mexico',
                'nivel': 'ALTO',
                'goles_promedio': 2.7,
                'local_ventaja': 58,
                'btts_pct': 54,
                'tarjetas_promedio': 5.2,
                'top_equipos': ['America', 'Chivas', 'Tigres', 'Monterrey', 'Cruz Azul', 'Pumas', 'Santos', 'Pachuca', 'Toluca', 'Leon'],
                'descripcion': 'Liga muy competitiva, local fuerte, partidos abiertos',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'OFENSIVO'
            },
            'Mexico Liga de Expansion MX': {
                'pais': 'Mexico',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 55,
                'btts_pct': 48,
                'top_equipos': ['Atletico La Paz', 'Cancun', 'Tepatitlan', 'Venados', 'Correcaminos', 'Alebrijes', 'Cimarrones', 'Dorados', 'Mineros', 'Tapatio'],
                'descripcion': 'Segunda division mexicana, menos goles que Liga MX',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'EQUILIBRADO'
            },
            'Mexico Segunda Division': {
                'pais': 'Mexico',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 52,
                'btts_pct': 44,
                'top_equipos': [],
                'descripcion': 'Tercera division mexicana, pocos datos, partidos cerrados',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # ESTADOS UNIDOS
            # ============================================================================
            'USA MLS': {
                'pais': 'Estados Unidos',
                'nivel': 'ALTO',
                'goles_promedio': 3.0,
                'local_ventaja': 60,
                'btts_pct': 65,
                'top_equipos': ['Inter Miami', 'LAFC', 'LA Galaxy', 'Atlanta', 'Seattle', 'NYCFC', 'Philadelphia', 'Columbus', 'Cincinnati', 'Orlando'],
                'descripcion': 'Muchos goles, viajes largos, partidos locos',
                'under_2_5_prob': 38,
                'over_2_5_prob': 62,
                'estilo': 'OFENSIVO'
            },
            'USA MLS Next Pro': {
                'pais': 'Estados Unidos',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 55,
                'btts_pct': 58,
                'top_equipos': [],
                'descripcion': 'Liga de desarrollo MLS, muchos goles',
                'under_2_5_prob': 45,
                'over_2_5_prob': 55,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # BRASIL
            # ============================================================================
            'Brazil Serie A': {
                'pais': 'Brasil',
                'nivel': 'ALTO',
                'goles_promedio': 2.4,
                'local_ventaja': 65,
                'btts_pct': 48,
                'top_equipos': ['Flamengo', 'Palmeiras', 'Corinthians', 'Sao Paulo', 'Santos', 'Gremio', 'Internacional', 'Cruzeiro', 'Atletico Mineiro', 'Botafogo', 'Fluminense', 'Vasco'],
                'descripcion': 'Local muy fuerte, viajes largos afectan',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'LOCALISTA'
            },
            'Brazil Serie B': {
                'pais': 'Brasil',
                'nivel': 'MEDIO',
                'goles_promedio': 2.2,
                'local_ventaja': 62,
                'btts_pct': 44,
                'top_equipos': ['Sport', 'Ceara', 'Goias', 'Vitoria', 'Guarani', 'Ponte Preta', 'Novorizontino', 'Mirassol', 'Avai', 'Chapecoense'],
                'descripcion': 'Segunda division brasileña, local muy fuerte',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'LOCALISTA'
            },
            
            # ============================================================================
            # ARGENTINA
            # ============================================================================
            'Argentina Liga Profesional': {
                'pais': 'Argentina',
                'nivel': 'ALTO',
                'goles_promedio': 2.1,
                'local_ventaja': 62,
                'btts_pct': 42,
                'tarjetas_promedio': 5.8,
                'top_equipos': ['River Plate', 'Boca Juniors', 'Racing', 'Independiente', 'San Lorenzo', 'Estudiantes', 'Velez', 'Talleres', 'Defensa y Justicia', 'Huracan'],
                'descripcion': 'Muy localista, pocos goles, muchas faltas',
                'under_2_5_prob': 68,
                'over_2_5_prob': 32,
                'estilo': 'DEFENSIVO'
            },
            'Argentina Primera Nacional': {
                'pais': 'Argentina',
                'nivel': 'MEDIO',
                'goles_promedio': 2.0,
                'local_ventaja': 60,
                'btts_pct': 40,
                'top_equipos': ['Nueva Chicago', 'Quilmes', 'San Martin', 'Gimnasia Jujuy', 'Almirante Brown', 'Atlanta', 'Temperley', 'Estudiantes BA', 'Ferro', 'Almagro'],
                'descripcion': 'Segunda division argentina, muy defensivo',
                'under_2_5_prob': 70,
                'over_2_5_prob': 30,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # CHILE
            # ============================================================================
            'Chile Primera Division': {
                'pais': 'Chile',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': ['Colo Colo', 'Universidad de Chile', 'Universidad Catolica', 'Palestino', 'Huachipato', 'Cobresal', 'Everton', 'O Higgins', 'Union Espanola'],
                'descripcion': 'Liga competitiva, local fuerte',
                'under_2_5_prob': 52,
                'over_2_5_prob': 48,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # COLOMBIA
            # ============================================================================
            'Colombia Primera A': {
                'pais': 'Colombia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['Atletico Nacional', 'Millonarios', 'Junior', 'Santa Fe', 'America de Cali', 'Deportivo Cali', 'Independiente Medellin', 'Tolima'],
                'descripcion': 'Local muy fuerte, pocos goles de visitante',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'LOCALISTA'
            },
            
            # ============================================================================
            # PERU
            # ============================================================================
            'Peru Primera Division': {
                'pais': 'Peru',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 62,
                'btts_pct': 48,
                'top_equipos': ['Universitario', 'Alianza Lima', 'Sporting Cristal', 'Melgar', 'Cienciano', 'Cusco', 'ADT', 'Atletico Grau'],
                'descripcion': 'Local muy fuerte, altura afecta',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'LOCALISTA'
            },
            
            # ============================================================================
            # ECUADOR
            # ============================================================================
            'Ecuador Primera A': {
                'pais': 'Ecuador',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 65,
                'btts_pct': 52,
                'top_equipos': ['Barcelona SC', 'Emelec', 'LDU Quito', 'Independiente Valle', 'Aucas', 'El Nacional', 'Delfin', 'Orense'],
                'descripcion': 'Local muy fuerte por altura',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'LOCALISTA'
            },
            
            # ============================================================================
            # URUGUAY
            # ============================================================================
            'Uruguay Primera Division': {
                'pais': 'Uruguay',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 50,
                'top_equipos': ['Penarol', 'Nacional', 'Defensor', 'Danubio', 'Liverpool', 'Montevideo Wanderers', 'River Plate', 'Boston River'],
                'descripcion': 'Liga competitiva, clasicos calientes',
                'under_2_5_prob': 52,
                'over_2_5_prob': 48,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # PARAGUAY
            # ============================================================================
            'Paraguay Primera Division': {
                'pais': 'Paraguay',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['Olimpia', 'Cerro Porteno', 'Libertad', 'Guarani', 'Nacional', 'Sportivo Luqueno'],
                'descripcion': 'Local fuerte, pocos goles',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # BOLIVIA
            # ============================================================================
            'Bolivia Primera Division': {
                'pais': 'Bolivia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 70,
                'btts_pct': 58,
                'top_equipos': ['Bolivar', 'The Strongest', 'Always Ready', 'Blooming', 'Oriente Petrolero', 'Wilstermann', 'Real Santa Cruz'],
                'descripcion': 'Altura extrema, locales muy fuertes',
                'under_2_5_prob': 40,
                'over_2_5_prob': 60,
                'estilo': 'LOCALISTA_OFENSIVO'
            },
            
            # ============================================================================
            # ESPANA
            # ============================================================================
            'Spain LaLiga': {
                'pais': 'Espana',
                'nivel': 'ALTO',
                'goles_promedio': 2.5,
                'local_ventaja': 54,
                'btts_pct': 48,
                'top_equipos': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Real Sociedad', 'Athletic Bilbao', 'Betis', 'Villarreal', 'Sevilla', 'Valencia', 'Girona'],
                'descripcion': 'Tactica, menos goles que Premier',
                'under_2_5_prob': 52,
                'over_2_5_prob': 48,
                'estilo': 'TACTICO'
            },
            'Spain Segunda': {
                'pais': 'Espana',
                'nivel': 'MEDIO',
                'goles_promedio': 2.2,
                'local_ventaja': 56,
                'btts_pct': 44,
                'top_equipos': ['Espanyol', 'Levante', 'Sporting Gijon', 'Zaragoza', 'Oviedo', 'Racing', 'Eibar', 'Eldense', 'Cartagena', 'Albacete'],
                'descripcion': 'Segunda division española, pocos goles',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # INGLATERRA
            # ============================================================================
            'England Premier League': {
                'pais': 'Inglaterra',
                'nivel': 'ALTO',
                'goles_promedio': 2.9,
                'local_ventaja': 52,
                'btts_pct': 58,
                'top_equipos': ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Manchester United', 'Tottenham', 'Newcastle', 'Aston Villa', 'West Ham', 'Brighton'],
                'descripcion': 'Liga mas competitiva, cualquiera gana',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'OFENSIVO'
            },
            'England Championship': {
                'pais': 'Inglaterra',
                'nivel': 'ALTO',
                'goles_promedio': 2.7,
                'local_ventaja': 54,
                'btts_pct': 54,
                'top_equipos': ['Leeds', 'Leicester', 'Southampton', 'West Brom', 'Norwich', 'Watford', 'Middlesbrough', 'Coventry', 'Hull', 'Sunderland'],
                'descripcion': 'Segunda inglesa, muy fisica, muchos goles',
                'under_2_5_prob': 45,
                'over_2_5_prob': 55,
                'estilo': 'FISICO'
            },
            
            # ============================================================================
            # ITALIA
            # ============================================================================
            'Italy Serie A': {
                'pais': 'Italia',
                'nivel': 'ALTO',
                'goles_promedio': 2.6,
                'local_ventaja': 52,
                'btts_pct': 52,
                'top_equipos': ['Inter', 'Milan', 'Juventus', 'Napoli', 'Roma', 'Lazio', 'Atalanta', 'Fiorentina', 'Bologna', 'Torino'],
                'descripcion': 'Tactica, algo lenta',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'TACTICO'
            },
            
            # ============================================================================
            # FRANCIA
            # ============================================================================
            'France Ligue 1': {
                'pais': 'Francia',
                'nivel': 'ALTO',
                'goles_promedio': 2.8,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': ['PSG', 'Marseille', 'Monaco', 'Lyon', 'Lens', 'Lille', 'Rennes', 'Nice', 'Reims', 'Strasbourg'],
                'descripcion': 'PSG dominante, resto competitivo',
                'under_2_5_prob': 45,
                'over_2_5_prob': 55,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # ALEMANIA
            # ============================================================================
            'Germany Bundesliga': {
                'pais': 'Alemania',
                'nivel': 'ALTO',
                'goles_promedio': 3.2,
                'local_ventaja': 54,
                'btts_pct': 60,
                'top_equipos': ['Bayern', 'Dortmund', 'Leverkusen', 'Leipzig', 'Stuttgart', 'Frankfurt', 'Gladbach', 'Wolfsburg', 'Hoffenheim', 'Freiburg'],
                'descripcion': 'Muchos goles, partidos abiertos',
                'under_2_5_prob': 35,
                'over_2_5_prob': 65,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # HOLANDA
            # ============================================================================
            'Netherlands Eredivisie': {
                'pais': 'Holanda',
                'nivel': 'MEDIO',
                'goles_promedio': 3.3,
                'local_ventaja': 56,
                'btts_pct': 62,
                'top_equipos': ['Ajax', 'PSV', 'Feyenoord', 'AZ', 'Twente', 'Utrecht', 'Sparta', 'NEC', 'Heerenveen', 'Go Ahead Eagles'],
                'descripcion': 'Muchisimos goles, defensas debiles',
                'under_2_5_prob': 30,
                'over_2_5_prob': 70,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # PORTUGAL
            # ============================================================================
            'Portugal Primeira Liga': {
                'pais': 'Portugal',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 60,
                'btts_pct': 52,
                'top_equipos': ['Benfica', 'Porto', 'Sporting', 'Braga', 'Vitoria', 'Famalicao', 'Arouca', 'Casa Pia', 'Rio Ave', 'Boavista'],
                'descripcion': 'Dominio de los 3 grandes',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'LOCALISTA'
            },
            
            # ============================================================================
            # BELGICA
            # ============================================================================
            'Belgium First Division A': {
                'pais': 'Belgica',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 56,
                'btts_pct': 56,
                'top_equipos': ['Anderlecht', 'Club Brugge', 'Genk', 'Antwerp', 'Gent', 'Union SG', 'Standard', 'Mechelen', 'Cercle Brugge', 'Westerlo'],
                'descripcion': 'Liga belga',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # TURQUIA
            # ============================================================================
            'Turkey Super Lig': {
                'pais': 'Turquia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 60,
                'btts_pct': 56,
                'top_equipos': ['Galatasaray', 'Fenerbahce', 'Besiktas', 'Trabzonspor', 'Basaksehir', 'Sivasspor', 'Konyaspor', 'Kayserispor', 'Antalyaspor', 'Alanyaspor'],
                'descripcion': 'Local muy fuerte, ambiente caliente',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'LOCALISTA'
            },
            
            # ============================================================================
            # COMPETICIONES UEFA
            # ============================================================================
            'UEFA Champions League': {
                'pais': 'Europa',
                'nivel': 'ALTO',
                'goles_promedio': 2.9,
                'local_ventaja': 54,
                'btts_pct': 56,
                'top_equipos': ['Real Madrid', 'Manchester City', 'Bayern', 'PSG', 'Liverpool', 'Inter', 'Barcelona', 'Arsenal', 'Dortmund', 'Atletico', 'Milan', 'Juventus'],
                'descripcion': 'Maxima competicion europea',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'ELITE'
            },
            'UEFA Europa League': {
                'pais': 'Europa',
                'nivel': 'ALTO',
                'goles_promedio': 2.8,
                'local_ventaja': 53,
                'btts_pct': 55,
                'top_equipos': ['Roma', 'Leverkusen', 'Liverpool', 'Villarreal', 'Marseille', 'Benfica', 'Sporting', 'Rangers', 'Ajax', 'Freiburg', 'Rennes', 'Betis'],
                'descripcion': 'Segunda competicion europea',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'ELITE'
            },
            
            # ============================================================================
            # CONMEBOL
            # ============================================================================
            'CONMEBOL Copa Libertadores': {
                'pais': 'Sudamerica',
                'nivel': 'ALTO',
                'goles_promedio': 2.3,
                'local_ventaja': 65,
                'btts_pct': 46,
                'top_equipos': ['Flamengo', 'Palmeiras', 'River', 'Boca', 'Nacional', 'Penarol', 'Colo Colo', 'Olimpia', 'Cerro', 'Racing', 'Independiente', 'Atletico MG'],
                'descripcion': 'Maxima competicion sudamericana',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'INTERNACIONAL'
            },
            'CONMEBOL Copa Sudamericana': {
                'pais': 'Sudamerica',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 62,
                'btts_pct': 48,
                'top_equipos': ['LDU', 'Defensa', 'Corinthians', 'Botafogo', 'Estudiantes', 'San Lorenzo', 'Universidad Catolica', 'Guarani', 'Sportivo', 'Nacional', 'Racing', 'Independiente'],
                'descripcion': 'Segunda competicion sudamericana',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'INTERNACIONAL'
            },
            
            # ============================================================================
            # ASIA
            # ============================================================================
            'AFC Champions League Elite': {
                'pais': 'Asia',
                'nivel': 'ALTO',
                'goles_promedio': 2.6,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': ['Al Hilal', 'Urawa', 'Jeonbuk', 'Pohang', 'Yokohama', 'Bangkok', 'Kawasaki', 'Shandong', 'Wuhan', 'Ventforet', 'Johor', 'BG Pathum'],
                'descripcion': 'Champions asiatica',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'INTERNACIONAL'
            },
            'Japan J League': {
                'pais': 'Japon',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 56,
                'btts_pct': 48,
                'top_equipos': ['Vissel Kobe', 'Yokohama', 'Kawasaki', 'Urawa', 'Nagoya', 'Sanfrecce', 'Kashima', 'Cerezo', 'Avispa', 'Consadole', 'FC Tokyo', 'Kyoto', 'Sagan', 'Shonan', 'Machida', 'Jubilo', 'Kashiwa', 'Gamba', 'Albirex', 'Tokyo Verdy'],
                'descripcion': 'Liga japonesa',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'TACTICO'
            },
            'South Korea K League 1': {
                'pais': 'Corea del Sur',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 58,
                'btts_pct': 46,
                'top_equipos': ['Ulsan', 'Pohang', 'Jeonbuk', 'Gwangju', 'Seoul', 'Incheon', 'Daegu', 'Suwon', 'Daejeon', 'Jeju', 'Gangwon', 'Gimcheon'],
                'descripcion': 'Liga coreana',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            'Saudi Pro League': {
                'pais': 'Arabia Saudi',
                'nivel': 'ALTO',
                'goles_promedio': 2.8,
                'local_ventaja': 58,
                'btts_pct': 56,
                'top_equipos': ['Al Hilal', 'Al Nassr', 'Al Ittihad', 'Al Ahli', 'Al Taawoun', 'Al Fateh', 'Al Shabab', 'Al Raed', 'Al Khaleej', 'Al Riyadh', 'Al Akhdoud', 'Al Hazem', 'Al Taee', 'Damac', 'Abha', 'Al Wehda'],
                'descripcion': 'Liga saudi',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # AFRICA
            # ============================================================================
            'Egypt Premier League': {
                'pais': 'Egipto',
                'nivel': 'BAJO',
                'goles_promedio': 2.1,
                'local_ventaja': 60,
                'btts_pct': 42,
                'top_equipos': ['Al Ahly', 'Zamalek', 'Pyramids', 'Future', 'Ceramica Cleopatra', 'ENPPI', 'Smouha', 'Al Masry', 'National Bank', 'Al Ittihad', 'El Gouna', 'Ismaily', 'Pharco', 'Baladiyat', 'El Dakhleya', 'ZED'],
                'descripcion': 'Liga egipcia, Al Ahly dominante',
                'under_2_5_prob': 65,
                'over_2_5_prob': 35,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # OCEANIA
            # ============================================================================
            'Australia A League': {
                'pais': 'Australia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.9,
                'local_ventaja': 54,
                'btts_pct': 58,
                'top_equipos': ['Melbourne City', 'Sydney', 'Central Coast', 'Western Sydney', 'Adelaide', 'Melbourne Victory', 'Brisbane', 'Perth', 'Newcastle', 'Wellington', 'Western United', 'Macarthur'],
                'descripcion': 'Liga australiana, muchos goles',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # MUNDIAL
            # ============================================================================
            'World Cup 2026': {
                'pais': 'Internacional',
                'nivel': 'ALTO',
                'goles_promedio': 2.6,
                'local_ventaja': 50,
                'btts_pct': 52,
                'top_equipos': [],
                'descripcion': 'Copa del Mundo',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'MUNDIAL'
            },
            
            # ============================================================================
            # DEFAULT
            # ============================================================================
            'default': {
                'pais': 'Desconocido',
                'nivel': 'DESCONOCIDO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Liga sin datos especificos',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'DESCONOCIDO'
            }
        }
    
    def _build_universal_rules(self):
        """Reglas universales que aplican a TODAS las ligas"""
        return [
            {
                'name': 'GOLES_BAJOS_ARGENTINA',
                'condition': lambda liga, local, visit: liga in ['Argentina Liga Profesional', 'Argentina Primera Nacional', 'Argentina Primera C', 'Argentina Primera B Metropolitana'],
                'action': 'under_2_5',
                'base_prob': 68,
                'reason': 'La Liga Argentina tiene pocos goles historicamente'
            },
            {
                'name': 'GOLES_ALTOS_HOLANDA',
                'condition': lambda liga, local, visit: liga in ['Netherlands Eredivisie', 'Netherlands Eerste Divisie'],
                'action': 'over_2_5',
                'base_prob': 68,
                'reason': 'La liga holandesa tiene muchisimos goles'
            },
            {
                'name': 'GOLES_ALTOS_BUNDESLIGA',
                'condition': lambda liga, local, visit: liga in ['Germany Bundesliga', 'Germany Bundesliga 2', 'Germany Bundesliga 3'],
                'action': 'over_2_5',
                'base_prob': 65,
                'reason': 'La Bundesliga es conocida por muchos goles'
            },
            {
                'name': 'LOCAL_FUERTE_BRASIL',
                'condition': lambda liga, local, visit: liga in ['Brazil Serie A', 'Brazil Serie B', 'Brazil Copa do Brasil'] and self._is_top_team(local, liga) and not self._is_top_team(visit, liga),
                'action': 'local_gana',
                'base_prob': 72,
                'reason': 'El equipo local es muy fuerte en casa en Brasil'
            },
            {
                'name': 'LOCAL_FUERTE_ARGENTINA',
                'condition': lambda liga, local, visit: liga in ['Argentina Liga Profesional'] and self._is_top_team(local, liga),
                'action': 'local_no_pierde',
                'base_prob': 75,
                'reason': 'El equipo local rara vez pierde en casa en Argentina'
            },
            {
                'name': 'VISITANTE_TOP_VS_DEBIL',
                'condition': lambda liga, local, visit: not self._is_top_team(local, liga) and self._is_top_team(visit, liga),
                'action': 'visitante_gana',
                'base_prob': 65,
                'reason': 'El equipo visitante es muy superior al local'
            },
            {
                'name': 'BTT_ALTO_EN_LIGA',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('btts_pct', 50) > 55,
                'action': 'btts',
                'base_prob': 60,
                'reason': 'En esta liga es comun que ambos anoten'
            },
            {
                'name': 'LOCAL_MUY_FUERTE',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('local_ventaja', 50) > 60,
                'action': 'local_no_pierde',
                'base_prob': 70,
                'reason': 'En esta liga los locales son muy fuertes'
            },
            {
                'name': 'LIGA_POCOS_GOLES',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('goles_promedio', 2.5) < 2.3,
                'action': 'under_2_5',
                'base_prob': 65,
                'reason': 'Esta liga tiene pocos goles historicamente'
            },
            {
                'name': 'LIGA_MUCHOS_GOLES',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('goles_promedio', 2.5) > 2.8,
                'action': 'over_2_5',
                'base_prob': 62,
                'reason': 'Esta liga tiene muchos goles historicamente'
            }
        ]
    
    def identify_league(self, home_team, away_team):
        """Identifica la liga usando multiples metodos"""
        
        # Buscar en la base de conocimiento
        for liga, data in self.leagues_db.items():
            if home_team in data.get('top_equipos', []) or away_team in data.get('top_equipos', []):
                return liga, data
        
        # Intentar con Football API
        if self.apis['football_api']:
            try:
                headers = {'x-apisports-key': self.apis['football_api']}
                
                # Buscar equipo local
                url = f"https://v3.football.api-sports.io/teams?search={home_team}"
                response = requests.get(url, headers=headers, timeout=3).json()
                
                if response.get('response'):
                    # Obtener liga del equipo
                    team_id = response['response'][0]['team']['id']
                    leagues_url = f"https://v3.football.api-sports.io/leagues?team={team_id}&season=2024"
                    leagues_resp = requests.get(leagues_url, headers=headers, timeout=3).json()
                    
                    if leagues_resp.get('response'):
                        league_name = leagues_resp['response'][0]['league']['name']
                        # Buscar en nuestra base
                        for liga in self.leagues_db:
                            if league_name in liga or liga in league_name:
                                return liga, self.leagues_db[liga]
            except:
                pass
        
        # Por defecto
        return 'default', self.leagues_db['default']
    
    def _is_top_team(self, team, liga):
        """Determina si un equipo es top en su liga"""
        liga_data = self.leagues_db.get(liga, {})
        top_equipos = liga_data.get('top_equipos', [])
        for top in top_equipos:
            if top.lower() in team.lower() or team.lower() in top.lower():
                return True
        return False
    
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
    
    def market_probabilities(self, odds):
        """Convierte odds a probabilidades de mercado sin vig"""
        decimals = [self.american_to_decimal(o) for o in odds[:3]]
        implied = [1/d for d in decimals]
        total = sum(implied)
        return [p/total for p in implied]
    
    def regularize(self, probs, max_change=0.05):
        """Regulariza para evitar probabilidades extremas"""
        probs = np.array(probs)
        probs = np.clip(probs, 0.01, 0.99)
        return (probs / probs.sum()).tolist()
    
    def analyze_match(self, home_team, away_team, odds_data=None):
        """
        Análisis híbrido completo: Mercado + Poisson + ELO + XGBoost
        """
        # Identificar liga
        liga_nombre, liga_data = self.identify_league(home_team, away_team)
        
        # Inicializar probabilidades
        probs_market = [0.4, 0.25, 0.35]  # fallback
        probs_poisson = [0.4, 0.25, 0.35]
        probs_elo = [0.4, 0.25, 0.35]
        probs_xgb = None
        
        # 1. Probabilidad de mercado (si hay odds)
        if odds_data and odds_data.get('all_odds'):
            probs_market = self.market_probabilities(odds_data['all_odds'])
        
        # 2. Modelo Poisson
        goles_liga = liga_data.get('goles_promedio', 2.5)
        local_adv = liga_data.get('local_ventaja', 55) / 100
        
        home_strength = 1.05 if self._is_top_team(home_team, liga_nombre) else 1.0
        away_strength = 1.05 if self._is_top_team(away_team, liga_nombre) else 1.0
        
        home_lambda = (goles_liga / 2) * local_adv * home_strength
        away_lambda = (goles_liga / 2) * (1 - local_adv) * away_strength
        
        mc_probs = self.montecarlo.analyze_match(home_lambda, away_lambda)
        probs_poisson = [mc_probs['home_win'], mc_probs['draw'], mc_probs['away_win']]
        
        # 3. Modelo ELO
        rating_home = self.elo.get_rating(home_team)
        rating_away = self.elo.get_rating(away_team)
        elo_probs_dict = self.elo.get_win_probability(home_team, away_team)
        probs_elo = [elo_probs_dict['home'], elo_probs_dict['draw'], elo_probs_dict['away']]
        
        # 4. Modelo XGBoost (si está entrenado)
        if self.xgb.is_trained:
            # Preparar features (simplificado - necesitarías stats reales)
            home_stats = {
                'avg_goals_for': 1.5, 'avg_goals_against': 1.2,
                'form_recent': 0.6, 'odds_implied_prob': probs_market[0]
            }
            away_stats = {
                'avg_goals_for': 1.3, 'avg_goals_against': 1.4,
                'form_recent': 0.5, 'odds_implied_prob': probs_market[2]
            }
            
            features = self.xgb.prepare_features(
                home_team, away_team,
                rating_home, rating_away,
                home_stats, away_stats,
                liga_data
            )
            
            xgb_pred = self.xgb.predict(features)
            if xgb_pred:
                probs_xgb = [xgb_pred['home'], xgb_pred['draw'], xgb_pred['away']]
        
        # 5. Combinar modelos (híbrido)
        final_probs = np.array(probs_market) * self.weights['market']
        final_probs += np.array(probs_poisson) * self.weights['poisson']
        final_probs += np.array(probs_elo) * self.weights['elo']
        
        if probs_xgb:
            final_probs += np.array(probs_xgb) * self.weights['xgb']
        else:
            # Si no hay XGBoost, redistribuir peso
            remaining = self.weights['xgb']
            final_probs += np.array(probs_market) * (remaining/3)
            final_probs += np.array(probs_poisson) * (remaining/3)
            final_probs += np.array(probs_elo) * (remaining/3)
        
        # Regularizar
        final_probs = self.regularize(final_probs)
        
        # Generar todos los mercados
        markets = [
            {"name": "Gana Local", "prob": final_probs[0], "category": "1X2"},
            {"name": "Empate", "prob": final_probs[1], "category": "1X2"},
            {"name": "Gana Visitante", "prob": final_probs[2], "category": "1X2"},
            {"name": "Over 1.5 goles", "prob": mc_probs['over_1_5'], "category": "Totales"},
            {"name": "Over 2.5 goles", "prob": mc_probs['over_2_5'], "category": "Totales"},
            {"name": "Over 3.5 goles", "prob": mc_probs['over_3_5'], "category": "Totales"},
            {"name": "Over 4.5 goles", "prob": mc_probs['over_4_5'], "category": "Totales"},
            {"name": "Under 2.5 goles", "prob": 1 - mc_probs['over_2_5'], "category": "Totales"},
            {"name": "Ambos anotan (BTTS)", "prob": mc_probs['btts'], "category": "BTTS"},
        ]
        
        # Mejor apuesta (la de mayor probabilidad)
        best_bet = max(markets, key=lambda x: x['prob'])
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'liga': liga_nombre,
            'markets': sorted(markets, key=lambda x: x['prob'], reverse=True),
            'best_bet': best_bet,
            'model_weights': self.weights,
            'probs_by_model': {
                'market': probs_market,
                'poisson': probs_poisson,
                'elo': probs_elo,
                'xgb': probs_xgb
            },
            'final_probs': final_probs.tolist(),
            'mc_stats': {
                'avg_goals': mc_probs['avg_goals'],
                'std_goals': mc_probs['std_goals'],
                'simulations': 50000
            },
            'elo_ratings': {
                'home': rating_home,
                'away': rating_away
            }
        }
