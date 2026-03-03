# modules/team_knowledge.py
import json
import os
import requests
import streamlit as st
from difflib import SequenceMatcher

class TeamKnowledge:
    """
    Base de conocimiento sobre equipos y ligas
    """
    def __init__(self):
        self.leagues_data = self._load_leagues_data()
        self.team_patterns = self._load_team_patterns()
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    
    def _load_leagues_data(self):
        """Carga información de ligas"""
        return {
            'Mexico Liga MX': {
                'nivel': 'ALTO',
                'goles_promedio': 2.7,
                'local_ventaja': 58,
                'btts_pct': 52,
                'top_equipos': ['America', 'Chivas', 'Tigres', 'Monterrey', 'Cruz Azul', 'Pumas', 'Santos', 'Pachuca', 'Toluca', 'Leon'],
                'descripcion': 'Liga mexicana, local fuerte, partidos abiertos'
            },
            'England Premier League': {
                'nivel': 'ALTO',
                'goles_promedio': 2.9,
                'local_ventaja': 52,
                'btts_pct': 55,
                'top_equipos': ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Manchester United', 'Tottenham', 'Newcastle', 'Aston Villa'],
                'descripcion': 'Liga más competitiva, cualquiera gana'
            },
            'Spain LaLiga': {
                'nivel': 'ALTO',
                'goles_promedio': 2.5,
                'local_ventaja': 54,
                'btts_pct': 48,
                'top_equipos': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Real Sociedad', 'Athletic Bilbao'],
                'descripcion': 'Táctica, menos goles que Premier'
            },
            'Germany Bundesliga': {
                'nivel': 'ALTO',
                'goles_promedio': 3.1,
                'local_ventaja': 54,
                'btts_pct': 58,
                'top_equipos': ['Bayern Munich', 'Dortmund', 'Leverkusen', 'RB Leipzig'],
                'descripcion': 'Muchos goles, partidos abiertos'
            },
            'Italy Serie A': {
                'nivel': 'ALTO',
                'goles_promedio': 2.6,
                'local_ventaja': 52,
                'btts_pct': 50,
                'top_equipos': ['Inter', 'Milan', 'Juventus', 'Napoli', 'Roma'],
                'descripcion': 'Táctica, algo lenta'
            },
            'Argentina Liga Profesional': {
                'nivel': 'MEDIO',
                'goles_promedio': 2.1,
                'local_ventaja': 62,
                'btts_pct': 42,
                'top_equipos': ['River Plate', 'Boca Juniors', 'Racing', 'Independiente', 'San Lorenzo'],
                'descripcion': 'Muy localista, pocos goles'
            },
            'Brazil Serie A': {
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 65,
                'btts_pct': 48,
                'top_equipos': ['Flamengo', 'Palmeiras', 'Corinthians', 'Sao Paulo'],
                'descripcion': 'Local muy fuerte, viajes largos'
            },
            'default': {
                'nivel': 'DESCONOCIDO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Liga sin datos específicos'
            }
        }
    
    def _load_team_patterns(self):
        """Patrones de equipos"""
        return {
            'PSG': {'casa': {'goles': 2.8, 'recibe': 0.9, 'victorias': 85}},
            'Real Madrid': {'casa': {'goles': 2.5, 'recibe': 0.8, 'victorias': 88}},
            'Barcelona': {'casa': {'goles': 2.4, 'recibe': 0.9, 'victorias': 82}},
            'Bayern Munich': {'casa': {'goles': 3.0, 'recibe': 0.7, 'victorias': 92}},
            'Manchester City': {'casa': {'goles': 2.7, 'recibe': 0.6, 'victorias': 90}}
        }
    
    def identify_league(self, team_name):
        """Intenta identificar la liga de un equipo"""
        for league, data in self.leagues_data.items():
            if team_name in data.get('top_equipos', []):
                return league, data
        
        if self.football_api_key:
            try:
                headers = {'x-apisports-key': self.football_api_key}
                url = f"https://v3.football.api-sports.io/teams?search={team_name}"
                response = requests.get(url, headers=headers, timeout=3).json()
                
                if response.get('results', 0) > 0:
                    return 'Desconocida', self.leagues_data['default']
            except:
                pass
        
        return 'Desconocida', self.leagues_data['default']
    
    def get_team_pattern(self, team_name):
        """Obtiene patrón de comportamiento de un equipo"""
        for name, pattern in self.team_patterns.items():
            if name.lower() in team_name.lower() or team_name.lower() in name.lower():
                return pattern
        
        return {'casa': {'goles': 1.5, 'recibe': 1.2, 'victorias': 50}}
