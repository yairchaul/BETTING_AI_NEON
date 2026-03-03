# modules/data_collector.py
import requests
import streamlit as st

class DataCollector:
    """
    Recolecta datos históricos de partidos para entrenar el modelo ML
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    
    def get_historical_matches(self, league_id, season='2024', limit=500):
        """
        Obtiene partidos históricos de una liga
        """
        if not self.api_key:
            st.warning("No hay API key configurada")
            return []
        
        headers = {'x-apisports-key': self.api_key}
        matches = []
        
        try:
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
            response = requests.get(url, headers=headers, timeout=10).json()
            
            for fixture in response.get('response', [])[:limit]:
                match = {
                    'fixture_id': fixture['fixture']['id'],
                    'date': fixture['fixture']['date'],
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'home_goals': fixture['goals']['home'] or 0,
                    'away_goals': fixture['goals']['away'] or 0,
                    'resultado': self._get_resultado(
                        fixture['goals']['home'] or 0,
                        fixture['goals']['away'] or 0
                    )
                }
                matches.append(match)
            
            return matches
            
        except Exception as e:
            st.error(f"Error recolectando datos: {e}")
            return []
    
    def _get_resultado(self, home_goals, away_goals):
        """Determina el resultado del partido (0: local, 1: empate, 2: visitante)"""
        if home_goals > away_goals:
            return 0
        elif home_goals == away_goals:
            return 1
        else:
            return 2
    
    def get_league_id(self, league_name):
        """Obtiene el ID de una liga por su nombre"""
        if not self.api_key:
            return None
        
        headers = {'x-apisports-key': self.api_key}
        
        try:
            url = f"https://v3.football.api-sports.io/leagues?search={league_name}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                return response['response'][0]['league']['id']
        except:
            pass
        
        return None