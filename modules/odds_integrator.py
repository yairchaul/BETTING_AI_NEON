# modules/odds_integrator.py
import requests
import streamlit as st
import time

class OddsIntegrator:
    def __init__(self):
        self.api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.base_url = "https://v3.football.api-sports.io"
        self.cache = {}
        self.max_retries = 3
    
    def get_fixture_id(self, home_team, away_team, league=None):
        """Busca fixture ID con reintentos y búsqueda flexible"""
        cache_key = f"{home_team}_{away_team}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        for attempt in range(self.max_retries):
            try:
                headers = {'x-apisports-key': self.api_key}
                
                # Estrategia 1: Búsqueda exacta
                url = f"{self.base_url}/fixtures?search={home_team} {away_team}&season=2024"
                response = requests.get(url, headers=headers, timeout=5).json()
                
                if response.get('results', 0) > 0:
                    for fixture in response['response']:
                        teams = fixture['teams']
                        if (home_team.lower() in teams['home']['name'].lower() and 
                            away_team.lower() in teams['away']['name'].lower()):
                            fixture_id = fixture['fixture']['id']
                            self.cache[cache_key] = fixture_id
                            return fixture_id
                
                # Estrategia 2: Búsqueda por fecha (próximos 7 días)
                time.sleep(1)  # Evitar rate limiting
                url = f"{self.base_url}/fixtures?date={self._get_next_dates()[attempt]}&season=2024"
                response = requests.get(url, headers=headers, timeout=5).json()
                
                for fixture in response.get('response', []):
                    teams = fixture['teams']
                    if (home_team.lower() in teams['home']['name'].lower() and 
                        away_team.lower() in teams['away']['name'].lower()):
                        fixture_id = fixture['fixture']['id']
                        self.cache[cache_key] = fixture_id
                        return fixture_id
                        
            except Exception as e:
                if attempt == self.max_retries - 1:
                    st.warning(f"No se pudo encontrar fixture para {home_team} vs {away_team}")
                time.sleep(2)
        
        return None
    
    def get_best_odds(self, fixture_id):
        """Obtiene las mejores odds con manejo de errores"""
        if not fixture_id:
            return None
        
        for attempt in range(self.max_retries):
            try:
                headers = {'x-apisports-key': self.api_key}
                url = f"{self.base_url}/odds?fixture={fixture_id}&bookmaker=all"
                response = requests.get(url, headers=headers, timeout=5).json()
                
                if response.get('results', 0) > 0:
                    odds_data = response['response'][0]
                    
                    best_odds = {
                        'home': {'value': 0, 'bookmaker': ''},
                        'draw': {'value': 0, 'bookmaker': ''},
                        'away': {'value': 0, 'bookmaker': ''}
                    }
                    
                    for bookmaker in odds_data['bookmakers']:
                        for bet in bookmaker['bets']:
                            if bet['name'] == 'Match Winner':
                                for value in bet['values']:
                                    if value['value'] == 'Home':
                                        if float(value['odd']) > best_odds['home']['value']:
                                            best_odds['home'] = {
                                                'value': float(value['odd']),
                                                'bookmaker': bookmaker['name']
                                            }
                                    elif value['value'] == 'Draw':
                                        if float(value['odd']) > best_odds['draw']['value']:
                                            best_odds['draw'] = {
                                                'value': float(value['odd']),
                                                'bookmaker': bookmaker['name']
                                            }
                                    elif value['value'] == 'Away':
                                        if float(value['odd']) > best_odds['away']['value']:
                                            best_odds['away'] = {
                                                'value': float(value['odd']),
                                                'bookmaker': bookmaker['name']
                                            }
                    
                    return best_odds
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    st.warning(f"Error obteniendo odds: {e}")
                time.sleep(2)
        
        return None
    
    def _get_next_dates(self):
        """Genera fechas para búsqueda"""
        from datetime import datetime, timedelta
        dates = []
        for i in range(7):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
        return dates