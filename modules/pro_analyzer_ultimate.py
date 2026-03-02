# modules/pro_analyzer_ultimate.py
import streamlit as st
import requests
import json
import numpy as np
from datetime import datetime
from modules.team_knowledge import TeamKnowledge
from modules.smart_searcher import SmartSearcher

class ProAnalyzerUltimate:
    """
    Analizador profesional con cobertura GLOBAL de ligas
    """
    
    def __init__(self):
        self.knowledge = TeamKnowledge()
        self.searcher = SmartSearcher()
        
        # APIs disponibles
        self.apis = {
            'football_api': st.secrets.get("FOOTBALL_API_KEY", ""),
            'odds_api': st.secrets.get("ODDS_API_KEY", ""),
            'google_cse': {
                'key': st.secrets.get("GOOGLE_API_KEY", ""),
                'cx': st.secrets.get("GOOGLE_CSE_ID", "")
            }
        }
        
        # BASE DE DATOS COMPLETA DE LIGAS (TODAS LAS QUE MENCIONASTE)
        self.leagues_db = self._build_complete_leagues_database()
        
        # Reglas de inferencia profesional (universales)
        self.rules = self._build_universal_rules()
    
    def _build_complete_leagues_database(self):
        """Base de datos completa con TODAS las ligas del mundo"""
        return {
            # ============================================================================
            # MÉXICO Y CENTROAMÉRICA
            # ============================================================================
            'Mexico Liga MX': {
                'pais': 'México',
                'nivel': 'ALTO',
                'goles_promedio': 2.7,
                'local_ventaja': 58,
                'btts_pct': 54,
                'tarjetas_promedio': 5.2,
                'top_equipos': ['América', 'Chivas', 'Tigres', 'Monterrey', 'Cruz Azul', 'Pumas', 'Santos', 'Pachuca', 'Toluca', 'Leon'],
                'descripcion': 'Liga muy competitiva, local fuerte, partidos abiertos',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'OFENSIVO'
            },
            'Mexico Liga de Expansión MX': {
                'pais': 'México',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 55,
                'btts_pct': 48,
                'top_equipos': ['Atlético La Paz', 'Cancún', 'Tepatitlán', 'Venados', 'Correcaminos', 'Alebrijes', 'Cimarrones', 'Dorados', 'Mineros', 'Tapatío'],
                'descripcion': 'Segunda división mexicana, menos goles que Liga MX',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'EQUILIBRADO'
            },
            'Mexico Segunda Division': {
                'pais': 'México',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 52,
                'btts_pct': 44,
                'top_equipos': [],
                'descripcion': 'Tercera división mexicana, pocos datos, partidos cerrados',
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
            # BRASIL (COMPLETO)
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
                'descripcion': 'Segunda división brasileña, local muy fuerte',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'LOCALISTA'
            },
            'Brazil Copa do Brasil': {
                'pais': 'Brasil',
                'nivel': 'ALTO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': [],
                'descripcion': 'Copa brasileña, partidos de eliminación directa',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'ELIMINATORIO'
            },
            'Brazil Campeonato Carioca': {
                'pais': 'Brasil',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['Flamengo', 'Fluminense', 'Vasco', 'Botafogo'],
                'descripcion': 'Campeonato estatal de Río, clásicos calientes',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'LOCALISTA'
            },
            'Brazil Campeonato Gaucho': {
                'pais': 'Brasil',
                'nivel': 'MEDIO',
                'goles_promedio': 2.2,
                'local_ventaja': 62,
                'btts_pct': 44,
                'top_equipos': ['Gremio', 'Internacional', 'Juventude'],
                'descripcion': 'Campeonato estatal de Rio Grande do Sul',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'LOCALISTA'
            },
            'Brazil Campeonato Piauiense': {
                'pais': 'Brasil',
                'nivel': 'BAJO',
                'goles_promedio': 2.0,
                'local_ventaja': 58,
                'btts_pct': 40,
                'top_equipos': ['Altos', 'Parnahyba', 'River-PI'],
                'descripcion': 'Campeonato estatal de Piauí, nivel bajo',
                'under_2_5_prob': 65,
                'over_2_5_prob': 35,
                'estilo': 'DEFENSIVO'
            },
            'Brazil Alagoano Cup': {
                'pais': 'Brasil',
                'nivel': 'BAJO',
                'goles_promedio': 2.1,
                'local_ventaja': 60,
                'btts_pct': 42,
                'top_equipos': ['CRB', 'CSA', 'ASA'],
                'descripcion': 'Campeonato estatal de Alagoas',
                'under_2_5_prob': 62,
                'over_2_5_prob': 38,
                'estilo': 'DEFENSIVO'
            },
            'Brazil U20': {
                'pais': 'Brasil',
                'nivel': 'BAJO',
                'goles_promedio': 2.8,
                'local_ventaja': 50,
                'btts_pct': 60,
                'top_equipos': [],
                'descripcion': 'Fútbol juvenil, muchos goles, defensas débiles',
                'under_2_5_prob': 40,
                'over_2_5_prob': 60,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # ARGENTINA (COMPLETO)
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
                'descripcion': 'Segunda división argentina, muy defensivo',
                'under_2_5_prob': 70,
                'over_2_5_prob': 30,
                'estilo': 'DEFENSIVO'
            },
            'Argentina Primera C': {
                'pais': 'Argentina',
                'nivel': 'BAJO',
                'goles_promedio': 1.9,
                'local_ventaja': 58,
                'btts_pct': 38,
                'top_equipos': ['Dock Sud', 'Midland', 'General Lamadrid', 'Lujan', 'Berazategui', 'Central Cordoba'],
                'descripcion': 'Cuarta división argentina, nivel bajo',
                'under_2_5_prob': 72,
                'over_2_5_prob': 28,
                'estilo': 'DEFENSIVO'
            },
            'Argentina Primera B Metropolitana': {
                'pais': 'Argentina',
                'nivel': 'BAJO',
                'goles_promedio': 2.0,
                'local_ventaja': 59,
                'btts_pct': 39,
                'top_equipos': ['Colegiales', 'Acassuso', 'Cañuelas', 'Deportivo Merlo', 'Flandria', 'Los Andes'],
                'descripcion': 'Tercera división argentina',
                'under_2_5_prob': 69,
                'over_2_5_prob': 31,
                'estilo': 'DEFENSIVO'
            },
            'Argentina Primera Division Reserves': {
                'pais': 'Argentina',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 52,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Liga de reserva, juveniles, más goles',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # CHILE
            # ============================================================================
            'Chile Primera División': {
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
            'Chile Primera B': {
                'pais': 'Chile',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 55,
                'btts_pct': 46,
                'top_equipos': ['Deportes La Serena', 'Deportes Antofagasta', 'Rangers', 'Magallanes', 'San Luis', 'Union San Felipe'],
                'descripcion': 'Segunda división chilena',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
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
            'Colombia Primera B': {
                'pais': 'Colombia',
                'nivel': 'BAJO',
                'goles_promedio': 2.1,
                'local_ventaja': 58,
                'btts_pct': 42,
                'top_equipos': ['Real Cartagena', 'Leones', 'Cucuta', 'Bogota', 'Llaneros', 'Orsomarso'],
                'descripcion': 'Segunda división colombiana',
                'under_2_5_prob': 65,
                'over_2_5_prob': 35,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # PERÚ
            # ============================================================================
            'Perú Primera División': {
                'pais': 'Perú',
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
            'Uruguay Primera División': {
                'pais': 'Uruguay',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 50,
                'top_equipos': ['Penarol', 'Nacional', 'Defensor', 'Danubio', 'Liverpool', 'Montevideo Wanderers', 'River Plate', 'Boston River'],
                'descripcion': 'Liga competitiva, clásicos calientes',
                'under_2_5_prob': 52,
                'over_2_5_prob': 48,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # PARAGUAY
            # ============================================================================
            'Paraguay Primera División': {
                'pais': 'Paraguay',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['Olimpia', 'Cerro Porteño', 'Libertad', 'Guarani', 'Nacional', 'Sportivo Luqueño'],
                'descripcion': 'Local fuerte, pocos goles',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # BOLIVIA
            # ============================================================================
            'Bolivia Primera División': {
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
            # VENEZUELA
            # ============================================================================
            'Venezuela Primera División': {
                'pais': 'Venezuela',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Caracas', 'Deportivo Tachira', 'Monagas', 'Zamora', 'Portuguesa', 'Academia Puerto Cabello'],
                'descripcion': 'Liga en desarrollo',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # COSTA RICA
            # ============================================================================
            'Costa Rica Primera División': {
                'pais': 'Costa Rica',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Saprissa', 'Alajuelense', 'Herediano', 'Cartagines', 'Perez Zeledon', 'Guanacasteca'],
                'descripcion': 'Liga centroamericana',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'EQUILIBRADO'
            },
            'Costa Rica Liga de Ascenso': {
                'pais': 'Costa Rica',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 55,
                'btts_pct': 44,
                'top_equipos': [],
                'descripcion': 'Segunda división costarricense',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # GUATEMALA
            # ============================================================================
            'Guatemala Liga Nacional': {
                'pais': 'Guatemala',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['Municipal', 'Comunicaciones', 'Antigua', 'Xelaju', 'Mixco', 'Coban Imperial'],
                'descripcion': 'Liga guatemalteca',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # HONDURAS
            # ============================================================================
            'Honduras Liga Nacional': {
                'pais': 'Honduras',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Olimpia', 'Motagua', 'Real Espana', 'Marathon', 'Vida', 'Victoria'],
                'descripcion': 'Liga hondureña',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # PANAMÁ
            # ============================================================================
            'Panama Liga Panamena': {
                'pais': 'Panamá',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 56,
                'btts_pct': 46,
                'top_equipos': ['Plaza Amador', 'Tauro', 'San Francisco', 'Sporting San Miguelito', 'Alianza', 'Costa del Este'],
                'descripcion': 'Liga panameña',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # JAMAICA
            # ============================================================================
            'Jamaica Premier League': {
                'pais': 'Jamaica',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 55,
                'btts_pct': 46,
                'top_equipos': ['Portmore', 'Waterhouse', 'Mount Pleasant', 'Harbour View', 'Tivoli', 'Arnett Gardens'],
                'descripcion': 'Liga jamaiquina',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # ESPAÑA
            # ============================================================================
            'Spain LaLiga': {
                'pais': 'España',
                'nivel': 'ALTO',
                'goles_promedio': 2.5,
                'local_ventaja': 54,
                'btts_pct': 48,
                'top_equipos': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Real Sociedad', 'Athletic Bilbao', 'Betis', 'Villarreal', 'Sevilla', 'Valencia', 'Girona'],
                'descripcion': 'Táctica, menos goles que Premier',
                'under_2_5_prob': 52,
                'over_2_5_prob': 48,
                'estilo': 'TACTICO'
            },
            'Spain Segunda': {
                'pais': 'España',
                'nivel': 'MEDIO',
                'goles_promedio': 2.2,
                'local_ventaja': 56,
                'btts_pct': 44,
                'top_equipos': ['Espanyol', 'Levante', 'Sporting Gijon', 'Zaragoza', 'Oviedo', 'Racing', 'Eibar', 'Eldense', 'Cartagena', 'Albacete'],
                'descripcion': 'Segunda división española, pocos goles',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            'Spain Copa Del Rey': {
                'pais': 'España',
                'nivel': 'ALTO',
                'goles_promedio': 2.6,
                'local_ventaja': 52,
                'btts_pct': 52,
                'top_equipos': [],
                'descripcion': 'Copa del Rey, sorpresas posibles',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'ELIMINATORIO'
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
                'descripcion': 'Liga más competitiva, cualquiera gana',
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
                'descripcion': 'Segunda inglesa, muy física, muchos goles',
                'under_2_5_prob': 45,
                'over_2_5_prob': 55,
                'estilo': 'FISICO'
            },
            'England League One': {
                'pais': 'Inglaterra',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': ['Derby', 'Bolton', 'Portsmouth', 'Barnsley', 'Charlton', 'Oxford', 'Blackpool', 'Peterborough', 'Wycombe', 'Lincoln'],
                'descripcion': 'Tercera inglesa, mucha intensidad',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'FISICO'
            },
            'England League Two': {
                'pais': 'Inglaterra',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 56,
                'btts_pct': 50,
                'top_equipos': ['Stockport', 'Mansfield', 'Wrexham', 'Notts County', 'Bradford', 'Gillingham', 'Walsall', 'Harrogate', 'Sutton', 'Crewe'],
                'descripcion': 'Cuarta inglesa',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            'England National League': {
                'pais': 'Inglaterra',
                'nivel': 'BAJO',
                'goles_promedio': 2.6,
                'local_ventaja': 54,
                'btts_pct': 52,
                'top_equipos': ['Chesterfield', 'Barnet', 'Bromley', 'Altrincham', 'Solihull', 'Halifax', 'Gateshead', 'Oldham', 'York', 'Dagenham'],
                'descripcion': 'Quinta inglesa, fútbol directo',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'FISICO'
            },
            'England National League North': {
                'pais': 'Inglaterra',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Sexta inglesa norte',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            'England National League South': {
                'pais': 'Inglaterra',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Sexta inglesa sur',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            'England EFL Cup': {
                'pais': 'Inglaterra',
                'nivel': 'ALTO',
                'goles_promedio': 2.7,
                'local_ventaja': 52,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa de la Liga, equipos rotan',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            'England FA Cup': {
                'pais': 'Inglaterra',
                'nivel': 'ALTO',
                'goles_promedio': 2.8,
                'local_ventaja': 52,
                'btts_pct': 56,
                'top_equipos': [],
                'descripcion': 'FA Cup, sorpresas frecuentes',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'COPA'
            },
            'England EFL Trophy': {
                'pais': 'Inglaterra',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 53,
                'btts_pct': 52,
                'top_equipos': [],
                'descripcion': 'Trofeo EFL, equipos de League One y Two',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'COPA'
            },
            'England Southern League Division One Central': {
                'pais': 'Inglaterra',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 54,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Liga regional inglesa',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # ESCOCIA
            # ============================================================================
            'Scotland Premiership': {
                'pais': 'Escocia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 56,
                'btts_pct': 56,
                'top_equipos': ['Celtic', 'Rangers', 'Aberdeen', 'Hearts', 'Hibs', 'Kilmarnock', 'St Mirren', 'Motherwell', 'Dundee', 'Ross County'],
                'descripcion': 'Dominio de Celtic y Rangers',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            'Scotland Championship': {
                'pais': 'Escocia',
                'nivel': 'BAJO',
                'goles_promedio': 2.6,
                'local_ventaja': 54,
                'btts_pct': 52,
                'top_equipos': ['Dundee United', 'Partick', 'Ayr', 'Raith', 'Inverness', 'Queen Park', 'Arbroath', 'Dunfermline', 'Morton', 'Airdrie'],
                'descripcion': 'Segunda escocesa',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'EQUILIBRADO'
            },
            'Scotland FA Cup': {
                'pais': 'Escocia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 54,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa escocesa',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # IRLANDA
            # ============================================================================
            'Ireland Premier Division': {
                'pais': 'Irlanda',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 56,
                'btts_pct': 50,
                'top_equipos': ['Shamrock Rovers', 'Derry City', 'Dundalk', 'St Patricks', 'Sligo', 'Bohemians', 'Shelbourne', 'Drogheda', 'Cork', 'Galway'],
                'descripcion': 'Liga irlandesa',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            'Ireland First Division': {
                'pais': 'Irlanda',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 55,
                'btts_pct': 48,
                'top_equipos': ['Cobh', 'Wexford', 'Longford', 'Athlone', 'Bray', 'Finn Harps', 'Kerry', 'Treaty United'],
                'descripcion': 'Segunda irlandesa',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # IRLANDA DEL NORTE
            # ============================================================================
            'Northern Ireland Premiership': {
                'pais': 'Irlanda del Norte',
                'nivel': 'BAJO',
                'goles_promedio': 2.6,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': ['Larne', 'Linfield', 'Crusaders', 'Glentoran', 'Cliftonville', 'Coleraine', 'Carrick', 'Ballymena', 'Dungannon', 'Glenavon'],
                'descripcion': 'Liga norirlandesa',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'EQUILIBRADO'
            },
            'Northern Ireland NIFL Development League': {
                'pais': 'Irlanda del Norte',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 53,
                'btts_pct': 48,
                'top_equipos': [],
                'descripcion': 'Liga de desarrollo',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # GALES
            # ============================================================================
            'Wales Premier League': {
                'pais': 'Gales',
                'nivel': 'BAJO',
                'goles_promedio': 2.7,
                'local_ventaja': 54,
                'btts_pct': 54,
                'top_equipos': ['The New Saints', 'Connah Quay', 'Bala', 'Newtown', 'Cardiff MU', 'Barry', 'Caernarfon', 'Aberystwyth', 'Haverfordwest', 'Penybont'],
                'descripcion': 'Liga galesa',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'OFENSIVO'
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
                'descripcion': 'Táctica, algo lenta',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'TACTICO'
            },
            'Italy Serie B': {
                'pais': 'Italia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 54,
                'btts_pct': 46,
                'top_equipos': ['Cremonese', 'Parma', 'Palermo', 'Venezia', 'Como', 'Catanzaro', 'Modena', 'Reggiana', 'Spezia', 'Bari'],
                'descripcion': 'Segunda italiana, pocos goles',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            'Italy Serie C': {
                'pais': 'Italia',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 55,
                'btts_pct': 44,
                'top_equipos': [],
                'descripcion': 'Tercera italiana',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            'Italy Coppa Italia': {
                'pais': 'Italia',
                'nivel': 'ALTO',
                'goles_promedio': 2.7,
                'local_ventaja': 52,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa italiana',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
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
            'France Ligue 2': {
                'pais': 'Francia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 56,
                'btts_pct': 46,
                'top_equipos': ['Bordeaux', 'Saint Etienne', 'Metz', 'Caen', 'Amiens', 'Grenoble', 'Paris FC', 'Sochaux', 'Quevilly', 'Valenciennes'],
                'descripcion': 'Segunda francesa, pocos goles',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            'France Coupe de France': {
                'pais': 'Francia',
                'nivel': 'ALTO',
                'goles_promedio': 2.9,
                'local_ventaja': 53,
                'btts_pct': 58,
                'top_equipos': [],
                'descripcion': 'Copa francesa, sorpresas',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'COPA'
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
            'Germany Bundesliga 2': {
                'pais': 'Alemania',
                'nivel': 'MEDIO',
                'goles_promedio': 2.9,
                'local_ventaja': 53,
                'btts_pct': 58,
                'top_equipos': ['Hamburg', 'Schalke', 'Hertha', 'Fortuna', 'Hannover', 'Kaiserslautern', 'Nurnberg', 'Magdeburg', 'Karlsruhe', 'Paderborn'],
                'descripcion': 'Segunda alemana, muchos goles',
                'under_2_5_prob': 40,
                'over_2_5_prob': 60,
                'estilo': 'OFENSIVO'
            },
            'Germany Bundesliga 3': {
                'pais': 'Alemania',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 54,
                'btts_pct': 56,
                'top_equipos': ['Dynamo Dresden', '1860 Munich', 'Essen', 'Verl', 'Sandhausen', 'Ulm', 'Freiburg II', 'Saarbrucken', 'Aue', 'Ingolstadt'],
                'descripcion': 'Tercera alemana',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            'Germany Regionalliga': {
                'pais': 'Alemania',
                'nivel': 'BAJO',
                'goles_promedio': 2.9,
                'local_ventaja': 55,
                'btts_pct': 58,
                'top_equipos': [],
                'descripcion': 'Ligas regionales alemanas',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
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
                'descripcion': 'Muchísimos goles, defensas débiles',
                'under_2_5_prob': 30,
                'over_2_5_prob': 70,
                'estilo': 'OFENSIVO'
            },
            'Netherlands Eerste Divisie': {
                'pais': 'Holanda',
                'nivel': 'BAJO',
                'goles_promedio': 3.1,
                'local_ventaja': 54,
                'btts_pct': 60,
                'top_equipos': ['Willem II', 'Groningen', 'Roda', 'Den Bosch', 'Cambuur', 'De Graafschap', 'NAC', 'Dordrecht', 'Emmen', 'Telstar'],
                'descripcion': 'Segunda holandesa, muchos goles',
                'under_2_5_prob': 35,
                'over_2_5_prob': 65,
                'estilo': 'OFENSIVO'
            },
            'Netherlands KNVB Cup': {
                'pais': 'Holanda',
                'nivel': 'MEDIO',
                'goles_promedio': 3.2,
                'local_ventaja': 52,
                'btts_pct': 62,
                'top_equipos': [],
                'descripcion': 'Copa holandesa',
                'under_2_5_prob': 33,
                'over_2_5_prob': 67,
                'estilo': 'COPA'
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
            'Portugal Segunda Liga': {
                'pais': 'Portugal',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['AVS', 'Santa Clara', 'Maritimo', 'Nacional', 'Tondela', 'Belenenses', 'Leixoes', 'Feirense', 'Penafiel', 'Torreense'],
                'descripcion': 'Segunda portuguesa',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            'Portugal Championship U23': {
                'pais': 'Portugal',
                'nivel': 'BAJO',
                'goles_promedio': 2.8,
                'local_ventaja': 52,
                'btts_pct': 58,
                'top_equipos': [],
                'descripcion': 'Sub-23 portuguesa, muchos goles',
                'under_2_5_prob': 40,
                'over_2_5_prob': 60,
                'estilo': 'OFENSIVO'
            },
            'Portugal Taça de Portugal': {
                'pais': 'Portugal',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 55,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa portuguesa',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # BÉLGICA
            # ============================================================================
            'Belgium First Division A': {
                'pais': 'Bélgica',
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
            'Belgium First Division B': {
                'pais': 'Bélgica',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 54,
                'btts_pct': 50,
                'top_equipos': ['Beveren', 'Deinze', 'Lommel', 'Oostende', 'Patro Eisden', 'RFC Liege', 'Seraing', 'Francs Borains', 'Jong Genk', 'Zulte Waregem'],
                'descripcion': 'Segunda belga',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # TURQUÍA
            # ============================================================================
            'Turkey Super Lig': {
                'pais': 'Turquía',
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
            'Turkey Cup': {
                'pais': 'Turquía',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 55,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa turca',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # AUSTRIA
            # ============================================================================
            'Austria Bundesliga': {
                'pais': 'Austria',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 58,
                'btts_pct': 56,
                'top_equipos': ['Salzburg', 'Sturm Graz', 'LASK', 'Rapid Wien', 'Austria Wien', 'Wolfsberger', 'Hartberg', 'Altach', 'BW Linz', 'Tirol'],
                'descripcion': 'Salzburg dominante',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            'Austria 2 Liga': {
                'pais': 'Austria',
                'nivel': 'BAJO',
                'goles_promedio': 2.6,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': ['Admira', 'Horn', 'St Polten', 'Floridsdorf', 'Kapfenberg', 'Leoben', 'Liefering', 'Amstetten', 'First Vienna', 'Dornbirn'],
                'descripcion': 'Segunda austriaca',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'EQUILIBRADO'
            },
            'Austria OFB Cup': {
                'pais': 'Austria',
                'nivel': 'MEDIO',
                'goles_promedio': 2.9,
                'local_ventaja': 54,
                'btts_pct': 58,
                'top_equipos': [],
                'descripcion': 'Copa austriaca',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # SUIZA
            # ============================================================================
            'Switzerland Super League': {
                'pais': 'Suiza',
                'nivel': 'MEDIO',
                'goles_promedio': 2.9,
                'local_ventaja': 58,
                'btts_pct': 58,
                'top_equipos': ['Young Boys', 'Servette', 'Lugano', 'Luzern', 'Zurich', 'Basel', 'St Gallen', 'Winterthur', 'Grasshopper', 'Lausanne', 'Yverdon'],
                'descripcion': 'Liga suiza',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # GRECIA
            # ============================================================================
            'Greece Super League': {
                'pais': 'Grecia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['Olympiacos', 'PAOK', 'AEK', 'Panathinaikos', 'Aris', 'Atromitos', 'OFI', 'Panserraikos', 'Volos', 'Lamia', 'Kifisia', 'Kallithea'],
                'descripcion': 'Local fuerte, pocos goles',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            'Greece Cup': {
                'pais': 'Grecia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': [],
                'descripcion': 'Copa griega',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # CROACIA
            # ============================================================================
            'Croatia HNL': {
                'pais': 'Croacia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 60,
                'btts_pct': 50,
                'top_equipos': ['Dinamo Zagreb', 'Hajduk Split', 'Osijek', 'Rijeka', 'Gorica', 'Varazdin', 'Slaven', 'Lokomotiva', 'Istra', 'Rudes'],
                'descripcion': 'Dinamo dominante',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'LOCALISTA'
            },
            'Croatia Cup': {
                'pais': 'Croacia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': [],
                'descripcion': 'Copa croata',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # SERBIA
            # ============================================================================
            'Serbia Super Liga': {
                'pais': 'Serbia',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Estrella Roja', 'Partizan', 'TSC', 'Vojvodina', 'Cukaricki', 'Radnicki', 'Novi Pazar', 'Napredak', 'Spartak', 'Mladost', 'IMT', 'Zeleznicar'],
                'descripcion': 'Dominio de Estrella Roja y Partizan',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # REPÚBLICA CHECA
            # ============================================================================
            'Czech Republic First League': {
                'pais': 'República Checa',
                'nivel': 'BAJO',
                'goles_promedio': 2.6,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': ['Sparta Prague', 'Slavia Prague', 'Viktoria Plzen', 'Banik Ostrava', 'Slovacko', 'Mlada Boleslav', 'Teplice', 'Jablonec', 'Hradec Kralove', 'Karvina', 'Bohemians', 'Pardubice'],
                'descripcion': 'Liga checa',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'EQUILIBRADO'
            },
            'Czech Republic Cup': {
                'pais': 'República Checa',
                'nivel': 'BAJO',
                'goles_promedio': 2.7,
                'local_ventaja': 55,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa checa',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # POLONIA
            # ============================================================================
            'Poland Ekstraklasa': {
                'pais': 'Polonia',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Legia', 'Lech', 'Rakow', 'Pogon', 'Widzew', 'Gornik', 'Zaglebie', 'Cracovia', 'Piast', 'Radomiak', 'Stal', 'Korona', 'LKS', 'Puszcza'],
                'descripcion': 'Liga polaca',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            'Poland Cup': {
                'pais': 'Polonia',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Copa polaca',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # HUNGRÍA
            # ============================================================================
            'Hungary NB1': {
                'pais': 'Hungría',
                'nivel': 'BAJO',
                'goles_promedio': 2.7,
                'local_ventaja': 58,
                'btts_pct': 54,
                'top_equipos': ['Ferencvaros', 'Paks', 'Kecskemet', 'Debrecen', 'Kisvarda', 'Zalaegerszeg', 'Ujpest', 'MTK', 'Diosgyor', 'Mezokovesd', 'Puskas', 'Honved'],
                'descripcion': 'Ferencvaros dominante',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # RUMANÍA
            # ============================================================================
            'Romania Liga 1': {
                'pais': 'Rumanía',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 60,
                'btts_pct': 46,
                'top_equipos': ['FCSB', 'CFR Cluj', 'Universitatea Craiova', 'Farul', 'Sepsi', 'Rapid', 'Petrolul', 'Voluntari', 'UTA', 'Botosani', 'Hermannstadt', 'Otelul', 'Politehnica Iasi', 'Dinamo'],
                'descripcion': 'Liga rumana',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            'Romania Cupa Romaniei': {
                'pais': 'Rumanía',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': [],
                'descripcion': 'Copa rumana',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # BULGARIA
            # ============================================================================
            'Bulgaria First League': {
                'pais': 'Bulgaria',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 60,
                'btts_pct': 44,
                'top_equipos': ['Ludogorets', 'CSKA Sofia', 'Levski', 'Lokomotiv Plovdiv', 'Botev Plovdiv', 'Cherno More', 'Arda', 'Krumovgrad', 'Slavia', 'Beroe', 'Pirin', 'Hebar', 'Etar', 'Lokomotiv Sofia'],
                'descripcion': 'Ludogorets dominante',
                'under_2_5_prob': 62,
                'over_2_5_prob': 38,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # ESLOVAQUIA
            # ============================================================================
            'Slovakia Super Liga': {
                'pais': 'Eslovaquia',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 50,
                'top_equipos': ['Slovan Bratislava', 'Spartak Trnava', 'Zilina', 'DAC', 'Ruzomberok', 'Trencin', 'Podbrezova', 'Zemplin', 'Skalica', 'Kosice', 'Banska Bystrica', 'Komarno'],
                'descripcion': 'Liga eslovaca',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # ESLOVENIA
            # ============================================================================
            'Slovenia Prva Liga': {
                'pais': 'Eslovenia',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Celje', 'Maribor', 'Olimpija', 'Domzale', 'Koper', 'Mura', 'Bravo', 'Radomlje', 'Aluminij', 'Rogaska'],
                'descripcion': 'Liga eslovena',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # DINAMARCA
            # ============================================================================
            'Denmark Superliga': {
                'pais': 'Dinamarca',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': ['FC Copenhagen', 'Midtjylland', 'Brondby', 'AGF', 'Nordsjaelland', 'Silkeborg', 'Randers', 'Viborg', 'Lyngby', 'Odense', 'Vejle', 'Hvidovre'],
                'descripcion': 'Liga danesa',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'EQUILIBRADO'
            },
            'Denmark Division 1': {
                'pais': 'Dinamarca',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 56,
                'btts_pct': 50,
                'top_equipos': ['Sonderjyske', 'Aalborg', 'Horsens', 'Fredericia', 'Koge', 'Helsingor', 'Naestved', 'B93', 'Hillerod', 'Kolding', 'Roskilde', 'FA 2000'],
                'descripcion': 'Segunda danesa',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            'Denmark DBU Pokalen': {
                'pais': 'Dinamarca',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 55,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Copa danesa',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # SUECIA
            # ============================================================================
            'Sweden Allsvenskan': {
                'pais': 'Suecia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.6,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': ['Malmo', 'Djurgarden', 'Hammarby', 'AIK', 'Elfsborg', 'Hacken', 'Kalmar', 'Norrkoping', 'Sirius', 'Varnamo', 'Mjallby', 'GAIS', 'Brommapojkarna', 'Halmstad', 'Goteborg', 'Vasteras'],
                'descripcion': 'Liga sueca',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # NORUEGA
            # ============================================================================
            'Norway Eliteserien': {
                'pais': 'Noruega',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 60,
                'btts_pct': 56,
                'top_equipos': ['Bodo/Glimt', 'Molde', 'Brann', 'Viking', 'Lillestrom', 'Rosenborg', 'Odd', 'HamKam', 'Sarpsborg', 'Stromsgodset', 'Kristiansund', 'Tromso', 'Haugesund', 'Fredrikstad', 'KFUM', 'Sandefjord'],
                'descripcion': 'Liga noruega',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            
            # ============================================================================
            # FINLANDIA
            # ============================================================================
            'Finland Veikkausliiga': {
                'pais': 'Finlandia',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 50,
                'top_equipos': ['HJK', 'KuPS', 'SJK', 'Ilves', 'VPS', 'Haka', 'Inter Turku', 'Lahti', 'Mariehamn', 'Gnistan', 'Ekenas', 'AC Oulu'],
                'descripcion': 'Liga finlandesa',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # ISLANDIA
            # ============================================================================
            'Iceland League Cup': {
                'pais': 'Islandia',
                'nivel': 'BAJO',
                'goles_promedio': 2.7,
                'local_ventaja': 55,
                'btts_pct': 54,
                'top_equipos': ['Vikingur', 'Breiðablik', 'Valur', 'KA', 'Stjarnan', 'Fram', 'FH', 'KR', 'Vestri', 'IA', 'Leiknir', 'Fylkir'],
                'descripcion': 'Copa islandesa',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'COPA'
            },
            
            # ============================================================================
            # UCRANIA
            # ============================================================================
            'Ukraine Premier League': {
                'pais': 'Ucrania',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 58,
                'btts_pct': 48,
                'top_equipos': ['Shakhtar', 'Dynamo Kyiv', 'Dnipro', 'Kryvbas', 'Polissya', 'Rukh', 'Vorskla', 'Kolos', 'LNZ', 'Olexandriya', 'Zorya', 'Obolon', 'Veres', 'Karpaty', 'Ingulets', 'Chornomorets'],
                'descripcion': 'Liga ucraniana',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # RUSIA
            # ============================================================================
            'Russia Premier League': {
                'pais': 'Rusia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 60,
                'btts_pct': 48,
                'top_equipos': ['Zenit', 'Krasnodar', 'Dinamo Moscow', 'CSKA', 'Lokomotiv', 'Spartak', 'Rostov', 'Rubin', 'Krylia', 'Akhmat', 'Fakel', 'Orenburg', 'Pari NN', 'Ural', 'KhIMKI', 'Baltika'],
                'descripcion': 'Liga rusa',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
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
                'descripcion': 'Champions asiática',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'INTERNACIONAL'
            },
            'China Super League': {
                'pais': 'China',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 58,
                'btts_pct': 50,
                'top_equipos': ['Shanghai Port', 'Shandong', 'Beijing', 'Chengdu', 'Zhejiang', 'Wuhan', 'Tianjin', 'Henan', 'Changchun', 'Meizhou', 'Qingdao', 'Nantong', 'Shenzhen', 'Cangzhou'],
                'descripcion': 'Superliga china',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            'Japan J League': {
                'pais': 'Japón',
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
            'South Korea K League 2': {
                'pais': 'Corea del Sur',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 56,
                'btts_pct': 44,
                'top_equipos': ['Anyang', 'Bucheon', 'Chungnam', 'Seoul E', 'Busan', 'Cheonan', 'Gyeongnam', 'Jeonnam', 'Seongnam', 'Suwon', 'Ansan', 'Cheongju', 'Gimpo', 'Hwaseong'],
                'descripcion': 'Segunda coreana',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            'Saudi Pro League': {
                'pais': 'Arabia Saudí',
                'nivel': 'ALTO',
                'goles_promedio': 2.8,
                'local_ventaja': 58,
                'btts_pct': 56,
                'top_equipos': ['Al Hilal', 'Al Nassr', 'Al Ittihad', 'Al Ahli', 'Al Taawoun', 'Al Fateh', 'Al Shabab', 'Al Raed', 'Al Khaleej', 'Al Riyadh', 'Al Akhdoud', 'Al Hazem', 'Al Taee', 'Damac', 'Abha', 'Al Wehda'],
                'descripcion': 'Liga saudí',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            'Saudi Division 1': {
                'pais': 'Arabia Saudí',
                'nivel': 'BAJO',
                'goles_promedio': 2.4,
                'local_ventaja': 56,
                'btts_pct': 48,
                'top_equipos': ['Al Qadisiyah', 'Al Orubah', 'Al Kholood', 'Al Arabi', 'Al Jabalain', 'Al Batin', 'Al Faisaly', 'Al Jandal', 'Al Najma', 'Al Taraji', 'Al Zulfi', 'Ohod', 'Al Adalah', 'Al Bukayriyah'],
                'descripcion': 'Segunda saudí',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'DEFENSIVO'
            },
            'Qatar Stars League': {
                'pais': 'Qatar',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 56,
                'btts_pct': 54,
                'top_equipos': ['Al Sadd', 'Al Duhail', 'Al Arabi', 'Al Wakrah', 'Al Gharafa', 'Umm Salal', 'Al Rayyan', 'Qatar SC', 'Al Shamal', 'Al Ahli', 'Al Markhiya', 'Muaither'],
                'descripcion': 'Liga catarí',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'OFENSIVO'
            },
            'UAE Pro League': {
                'pais': 'Emiratos Árabes',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 56,
                'btts_pct': 56,
                'top_equipos': ['Al Ain', 'Al Wahda', 'Al Nasr', 'Sharjah', 'Shabab Al Ahli', 'Al Jazira', 'Al Bataeh', 'Ajman', 'Al Ittihad', 'Baniyas', 'Kalba', 'Emirates', 'Hatta', 'Khor Fakkan'],
                'descripcion': 'Liga emiratí',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'OFENSIVO'
            },
            'Iran Pro League': {
                'pais': 'Irán',
                'nivel': 'BAJO',
                'goles_promedio': 2.0,
                'local_ventaja': 62,
                'btts_pct': 38,
                'top_equipos': ['Persepolis', 'Esteghlal', 'Sepahan', 'Tractor', 'Gol Gohar', 'Foolad', 'Malavan', 'Zob Ahan', 'Aluminium', 'Havadar', 'Shams Azar', 'Sanat Naft', 'Nassaji', 'Paykan', 'Esteghlal Khuzestan', 'Fajr Sepasi'],
                'descripcion': 'Liga iraní, muy defensiva',
                'under_2_5_prob': 70,
                'over_2_5_prob': 30,
                'estilo': 'DEFENSIVO'
            },
            'Iraq Stars League': {
                'pais': 'Irak',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 58,
                'btts_pct': 44,
                'top_equipos': ['Al Quwa', 'Al Shorta', 'Al Zawraa', 'Al Talaba', 'Naft', 'Erbil', 'Duhok', 'Al Karkh', 'Al Naft', 'Al Hudood', 'Al Kahrabaa', 'Al Minaa'],
                'descripcion': 'Liga iraquí',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            'Jordan Pro League': {
                'pais': 'Jordania',
                'nivel': 'BAJO',
                'goles_promedio': 2.3,
                'local_ventaja': 58,
                'btts_pct': 46,
                'top_equipos': ['Al Wehdat', 'Al Faisaly', 'Al Hussein', 'Al Salt', 'Ma'an', 'Al Ramtha', 'Sahab', 'Al Ahli', 'Al Jazeera', 'Shabab Al Ordon', 'Moghayer Al Sarhan', 'Al Aqaba'],
                'descripcion': 'Liga jordana',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'DEFENSIVO'
            },
            'Indonesia Liga 1': {
                'pais': 'Indonesia',
                'nivel': 'BAJO',
                'goles_promedio': 2.5,
                'local_ventaja': 60,
                'btts_pct': 50,
                'top_equipos': ['Bali United', 'Persib', 'PSM', 'Borneo', 'Persija', 'Madura', 'Dewa United', 'RANS', 'Arema', 'Persis', 'Barito', 'Persebaya', 'PSIS', 'Persita', 'PSS', 'Persikabo'],
                'descripcion': 'Liga indonesia',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'EQUILIBRADO'
            },
            
            # ============================================================================
            # ÁFRICA
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
            'South Africa Premier League': {
                'pais': 'Sudáfrica',
                'nivel': 'BAJO',
                'goles_promedio': 2.2,
                'local_ventaja': 58,
                'btts_pct': 44,
                'top_equipos': ['Mamelodi Sundowns', 'Orlando Pirates', 'Kaizer Chiefs', 'Stellenbosch', 'SuperSport', 'Sekhukhune', 'Cape Town', 'Richards Bay', 'AmaZulu', 'Royal AM', 'Chippa', 'Polokwane', 'Moroka', 'Golden Arrows', 'TS Galaxy', 'Cape Town Spurs'],
                'descripcion': 'Liga sudafricana',
                'under_2_5_prob': 60,
                'over_2_5_prob': 40,
                'estilo': 'DEFENSIVO'
            },
            
            # ============================================================================
            # OCEANÍA
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
            # COMPETICIONES INTERNACIONALES
            # ============================================================================
            'UEFA Champions League': {
                'pais': 'Europa',
                'nivel': 'ALTO',
                'goles_promedio': 2.9,
                'local_ventaja': 54,
                'btts_pct': 56,
                'top_equipos': ['Real Madrid', 'Manchester City', 'Bayern', 'PSG', 'Liverpool', 'Inter', 'Barcelona', 'Arsenal', 'Dortmund', 'Atletico', 'Milan', 'Juventus'],
                'descripcion': 'Máxima competición europea',
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
                'descripcion': 'Segunda competición europea',
                'under_2_5_prob': 44,
                'over_2_5_prob': 56,
                'estilo': 'ELITE'
            },
            'UEFA Europa Conference League': {
                'pais': 'Europa',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 54,
                'btts_pct': 54,
                'top_equipos': ['Fiorentina', 'Club Brugge', 'Aston Villa', 'Fenerbahce', 'PAOK', 'Lille', 'Maccabi', 'Gent', 'Molde', 'Bodo/Glimt', 'Legia', 'Eintracht'],
                'descripcion': 'Tercera competición europea',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'ELITE'
            },
            'CONMEBOL Copa Libertadores': {
                'pais': 'Sudamérica',
                'nivel': 'ALTO',
                'goles_promedio': 2.3,
                'local_ventaja': 65,
                'btts_pct': 46,
                'top_equipos': ['Flamengo', 'Palmeiras', 'River', 'Boca', 'Nacional', 'Penarol', 'Colo Colo', 'Olimpia', 'Cerro', 'Racing', 'Independiente', 'Atletico MG'],
                'descripcion': 'Máxima competición sudamericana',
                'under_2_5_prob': 58,
                'over_2_5_prob': 42,
                'estilo': 'INTERNACIONAL'
            },
            'CONMEBOL Copa Sudamericana': {
                'pais': 'Sudamérica',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 62,
                'btts_pct': 48,
                'top_equipos': ['LDU', 'Defensa', 'Corinthians', 'Botafogo', 'Estudiantes', 'San Lorenzo', 'Universidad Catolica', 'Guaraní', 'Sportivo', 'Nacional', 'Racing', 'Independiente'],
                'descripcion': 'Segunda competición sudamericana',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'INTERNACIONAL'
            },
            'CONMEBOL/UEFA Cup of Champions Finalissima': {
                'pais': 'Internacional',
                'nivel': 'ALTO',
                'goles_promedio': 2.5,
                'local_ventaja': 50,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Final entre campeones de Europa y Sudamérica',
                'under_2_5_prob': 50,
                'over_2_5_prob': 50,
                'estilo': 'FINAL'
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
            'World Cup 2026 Qualification Europe': {
                'pais': 'Europa',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 55,
                'btts_pct': 54,
                'top_equipos': [],
                'descripcion': 'Clasificatorios europeos',
                'under_2_5_prob': 46,
                'over_2_5_prob': 54,
                'estilo': 'CLASIFICATORIO'
            },
            'World Cup 2026 Int Conf Playoff': {
                'pais': 'Internacional',
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 52,
                'btts_pct': 48,
                'top_equipos': [],
                'descripcion': 'Playoff intercontinental',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45,
                'estilo': 'ELIMINATORIO'
            },
            
            # ============================================================================
            # FÚTBOL FEMENINO
            # ============================================================================
            'Women International AFC Asian Cup': {
                'pais': 'Asia',
                'nivel': 'MEDIO',
                'goles_promedio': 2.8,
                'local_ventaja': 52,
                'btts_pct': 58,
                'top_equipos': [],
                'descripcion': 'Copa Asiática femenina',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58,
                'estilo': 'FEMENINO'
            },
            'Women International Friendly': {
                'pais': 'Internacional',
                'nivel': 'MEDIO',
                'goles_promedio': 2.5,
                'local_ventaja': 50,
                'btts_pct': 52,
                'top_equipos': [],
                'descripcion': 'Amistosos femeninos',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52,
                'estilo': 'FEMENINO'
            },
            'Women World Cup Qualification': {
                'pais': 'Internacional',
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 52,
                'btts_pct': 55,
                'top_equipos': [],
                'descripcion': 'Clasificación Mundial femenino',
                'under_2_5_prob': 45,
                'over_2_5_prob': 55,
                'estilo': 'FEMENINO'
            },
            
            # ============================================================================
            # LIGAS RESERVA Y JUVENILES
            # ============================================================================
            'Reserve League Generic': {
                'pais': 'Varios',
                'nivel': 'BAJO',
                'goles_promedio': 2.8,
                'local_ventaja': 52,
                'btts_pct': 60,
                'top_equipos': [],
                'descripcion': 'Ligas de reserva, muchos goles',
                'under_2_5_prob': 40,
                'over_2_5_prob': 60,
                'estilo': 'JUVENIL'
            },
            
            # ============================================================================
            # DEFAULT (cuando no se puede identificar)
            # ============================================================================
            'default': {
                'pais': 'Desconocido',
                'nivel': 'DESCONOCIDO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Liga sin datos específicos',
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
                'reason': 'La Liga Argentina tiene pocos goles históricamente'
            },
            {
                'name': 'GOLES_BAJOS_IRAN',
                'condition': lambda liga, local, visit: liga == 'Iran Pro League',
                'action': 'under_2_5',
                'base_prob': 70,
                'reason': 'La liga iraní es extremadamente defensiva'
            },
            {
                'name': 'GOLES_ALTOS_HOLANDA',
                'condition': lambda liga, local, visit: liga in ['Netherlands Eredivisie', 'Netherlands Eerste Divisie'],
                'action': 'over_2_5',
                'base_prob': 68,
                'reason': 'La liga holandesa tiene muchísimos goles'
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
                'reason': f'{local} es muy fuerte en casa en Brasil'
            },
            {
                'name': 'LOCAL_FUERTE_ARGENTINA',
                'condition': lambda liga, local, visit: liga in ['Argentina Liga Profesional'] and self._is_top_team(local, liga),
                'action': 'local_no_pierde',
                'base_prob': 75,
                'reason': f'{local} rara vez pierde en casa en Argentina'
            },
            {
                'name': 'VISITANTE_TOP_VS_DEBIL',
                'condition': lambda liga, local, visit: not self._is_top_team(local, liga) and self._is_top_team(visit, liga),
                'action': 'visitante_gana',
                'base_prob': 65,
                'reason': f'{visit} es muy superior a {local}'
            },
            {
                'name': 'BTT_ALTO_EN_LIGA',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('btts_pct', 50) > 55,
                'action': 'btts',
                'base_prob': 60,
                'reason': f'En {liga} es común que ambos anoten'
            },
            {
                'name': 'LOCAL_MUY_FUERTE',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('local_ventaja', 50) > 60,
                'action': 'local_no_pierde',
                'base_prob': 70,
                'reason': f'En {liga} los locales son muy fuertes'
            },
            {
                'name': 'LIGA_POCOS_GOLES',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('goles_promedio', 2.5) < 2.3,
                'action': 'under_2_5',
                'base_prob': 65,
                'reason': f'{liga} tiene pocos goles históricamente'
            },
            {
                'name': 'LIGA_MUCHOS_GOLES',
                'condition': lambda liga, local, visit: self.leagues_db.get(liga, {}).get('goles_promedio', 2.5) > 2.8,
                'action': 'over_2_5',
                'base_prob': 62,
                'reason': f'{liga} tiene muchos goles históricamente'
            },
            {
                'name': 'TOP_CASA_VS_DEBIL',
                'condition': lambda liga, local, visit: self._is_top_team(local, liga) and self._is_bottom_team(visit, liga),
                'action': 'local_gana_y_over',
                'base_prob': 60,
                'reason': f'{local} suele golear en casa a los débiles'
            }
        ]
    
    def identify_league(self, home_team, away_team):
        """Identifica la liga usando múltiples métodos"""
        
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
    
    def _is_bottom_team(self, team, liga):
        """Determina si un equipo es débil (por ahora, inversa de top)"""
        return not self._is_top_team(team, liga)
    
    def analyze_match(self, home_team, away_team, odds_data=None):
        """
        Análisis profesional completo
        """
        # Identificar liga
        liga_nombre, liga_data = self.identify_league(home_team, away_team)
        
        # Aplicar reglas
        reglas_aplicadas = []
        for rule in self.rules:
            try:
                if rule['condition'](liga_nombre, home_team, away_team):
                    reglas_aplicadas.append(rule)
            except:
                pass
        
        # Determinar mejor apuesta
        best_bet = self._determine_best_bet(reglas_aplicadas, liga_data)
        
        # Generar mercados
        markets = self._generate_markets(liga_data, best_bet)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'liga': liga_nombre,
            'liga_data': liga_data,
            'markets': markets,
            'best_bet': best_bet,
            'reglas_aplicadas': [r['name'] for r in reglas_aplicadas]
        }
    
    def _determine_best_bet(self, reglas, liga_data):
        """Determina la mejor apuesta basada en reglas"""
        if not reglas:
            return {
                'market': 'Over 1.5 goles',
                'probability': 0.70,
                'confidence': 'BAJA',
                'reason': 'Sin datos específicos, apuesta conservadora'
            }
        
        from collections import Counter
        acciones = [r['action'] for r in reglas]
        mas_comun = Counter(acciones).most_common(1)[0][0]
        
        # Encontrar regla con mayor probabilidad
        mejor_regla = max(
            [r for r in reglas if r['action'] == mas_comun],
            key=lambda x: x.get('base_prob', 50)
        )
        
        # Ajustar según liga
        prob_ajustada = mejor_regla['base_prob']
        if mas_comun == 'over_2_5':
            prob_ajustada = liga_data.get('over_2_5_prob', prob_ajustada)
        elif mas_comun == 'under_2_5':
            prob_ajustada = liga_data.get('under_2_5_prob', prob_ajustada)
        
        market_map = {
            'local_gana': 'Gana Local',
            'visitante_gana': 'Gana Visitante',
            'local_no_pierde': 'Local o Empate (1X)',
            'btts': 'Ambos anotan (BTTS)',
            'over_2_5': 'Over 2.5 goles',
            'under_2_5': 'Under 2.5 goles',
            'local_gana_y_over': 'Gana Local + Over 2.5'
        }
        
        return {
            'market': market_map.get(mas_comun, 'Over 1.5 goles'),
            'probability': prob_ajustada / 100,
            'confidence': 'ALTA' if prob_ajustada > 65 else 'MEDIA' if prob_ajustada > 55 else 'BAJA',
            'reason': mejor_regla['reason']
        }
    
    def _generate_markets(self, liga_data, best_bet):
        """Genera mercados basados en datos de liga"""
        markets = [
            {'name': 'Gana Local', 'prob': 0.40, 'category': '1X2'},
            {'name': 'Empate', 'prob': 0.25, 'category': '1X2'},
            {'name': 'Gana Visitante', 'prob': 0.35, 'category': '1X2'},
            {'name': 'Over 1.5 goles', 'prob': 1 - (liga_data.get('under_2_5_prob', 50) / 100 * 0.6), 'category': 'Totales'},
            {'name': 'Over 2.5 goles', 'prob': liga_data.get('over_2_5_prob', 50) / 100, 'category': 'Totales'},
            {'name': 'Under 2.5 goles', 'prob': liga_data.get('under_2_5_prob', 50) / 100, 'category': 'Totales'},
            {'name': 'Ambos anotan (BTTS)', 'prob': liga_data.get('btts_pct', 50) / 100, 'category': 'BTTS'},
            {'name': 'Over 0.5 goles (1T)', 'prob': min(0.85, liga_data.get('goles_promedio', 2.5) / 3 * 1.2), 'category': 'Primer Tiempo'},
        ]
        return sorted(markets, key=lambda x: x['prob'], reverse=True)
