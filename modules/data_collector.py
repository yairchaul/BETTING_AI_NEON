# modules/data_collector.py
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

class DataCollector:
    """
    Recolecta datos históricos de partidos para entrenar el modelo ML
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.base_url = "https://v3.football.api-sports.io"
        self.cache = {}
    
    def get_league_id(self, league_name):
        """Obtiene el ID de una liga por su nombre"""
        if not self.api_key:
            return None
        
        headers = {'x-apisports-key': self.api_key}
        
        try:
            url = f"{self.base_url}/leagues?search={league_name}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                return response['response'][0]['league']['id']
        except Exception as e:
            st.error(f"Error buscando liga: {e}")
        
        return None
    
    def get_seasons(self):
        """Obtiene temporadas disponibles"""
        return ['2024', '2023', '2022', '2021', '2020']
    
    def get_historical_matches(self, league_id, season='2024', limit=1000):
        """
        Obtiene partidos históricos de una liga
        """
        if not self.api_key:
            st.warning("No hay API key configurada")
            return []
        
        cache_key = f"{league_id}_{season}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        headers = {'x-apisports-key': self.api_key}
        all_matches = []
        
        try:
            # Obtener fixtures de la temporada
            url = f"{self.base_url}/fixtures?league={league_id}&season={season}"
            response = requests.get(url, headers=headers, timeout=10).json()
            
            fixtures = response.get('response', [])
            total = len(fixtures)
            
            # Barra de progreso (si estamos en Streamlit)
            if st._is_running:
                progress_bar = st.progress(0)
            
            for i, fixture in enumerate(fixtures[:limit]):
                # Actualizar progreso
                if st._is_running and i % 10 == 0:
                    progress_bar.progress(min(i/limit, 1.0))
                
                # Datos básicos del partido
                match = {
                    'fixture_id': fixture['fixture']['id'],
                    'date': fixture['fixture']['date'][:10],
                    'timestamp': fixture['fixture']['timestamp'],
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'home_goals': fixture['goals']['home'] or 0,
                    'away_goals': fixture['goals']['away'] or 0,
                    'resultado': self._get_resultado(
                        fixture['goals']['home'] or 0,
                        fixture['goals']['away'] or 0
                    )
                }
                
                # Intentar obtener odds históricas
                match['odds'] = self._get_match_odds(match['fixture_id'])
                
                all_matches.append(match)
                
                # Pequeña pausa para no sobrecargar la API
                time.sleep(0.1)
            
            self.cache[cache_key] = all_matches
            return all_matches
            
        except Exception as e:
            st.error(f"Error recolectando datos: {e}")
            return []
    
    def _get_match_odds(self, fixture_id):
        """Obtiene odds históricas del partido"""
        if not self.api_key:
            return None
        
        headers = {'x-apisports-key': self.api_key}
        
        try:
            url = f"{self.base_url}/odds?fixture={fixture_id}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                odds_data = response['response'][0]
                best_odds = {
                    'home': None,
                    'draw': None,
                    'away': None
                }
                
                for bookmaker in odds_data['bookmakers']:
                    for bet in bookmaker['bets']:
                        if bet['name'] == 'Match Winner':
                            for value in bet['values']:
                                if value['value'] == 'Home':
                                    if not best_odds['home'] or float(value['odd']) > best_odds['home']:
                                        best_odds['home'] = float(value['odd'])
                                elif value['value'] == 'Draw':
                                    if not best_odds['draw'] or float(value['odd']) > best_odds['draw']:
                                        best_odds['draw'] = float(value['odd'])
                                elif value['value'] == 'Away':
                                    if not best_odds['away'] or float(value['odd']) > best_odds['away']:
                                        best_odds['away'] = float(value['odd'])
                
                return best_odds
        except:
            pass
        
        return None
    
    def _get_resultado(self, home_goals, away_goals):
        """Determina el resultado del partido (0: local, 1: empate, 2: visitante)"""
        if home_goals > away_goals:
            return 0
        elif home_goals == away_goals:
            return 1
        else:
            return 2
    
    def prepare_training_data(self, matches):
        """
        Prepara los datos para entrenar XGBoost
        """
        X = []
        y = []
        
        for match in matches:
            # Características básicas
            features = [
                match['home_goals'],  # goles local (histórico)
                match['away_goals'],  # goles visitante (histórico)
                match.get('odds', {}).get('home', 2.0),  # odds local
                match.get('odds', {}).get('draw', 3.0),  # odds empate
                match.get('odds', {}).get('away', 3.5),  # odds visitante
                # Más características se pueden añadir
            ]
            
            X.append(features)
            y.append(match['resultado'])
        
        return X, y
    
    def get_league_stats(self, league_id, season='2024'):
        """
        Obtiene estadísticas generales de la liga
        """
        if not self.api_key:
            return {}
        
        headers = {'x-apisports-key': self.api_key}
        
        try:
            # Obtener estadísticas de la liga
            url = f"{self.base_url}/leagues/statistics?league={league_id}&season={season}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('response'):
                stats = response['response']
                return {
                    'total_goals': stats.get('goals', {}).get('total', 0),
                    'avg_goals': stats.get('goals', {}).get('average', 0),
                    'home_wins': stats.get('wins', {}).get('home', 0),
                    'away_wins': stats.get('wins', {}).get('away', 0),
                    'draws': stats.get('draws', {}).get('total', 0)
                }
        except:
            pass
        
        return {}
    
    def download_all_leagues(self, leagues_list, seasons=['2024'], max_per_league=500):
        """
        Descarga datos de múltiples ligas
        """
        all_data = []
        
        for league_name in leagues_list:
            st.write(f"📥 Procesando: {league_name}")
            league_id = self.get_league_id(league_name)
            
            if league_id:
                for season in seasons:
                    matches = self.get_historical_matches(league_id, season, max_per_league)
                    for match in matches:
                        match['league'] = league_name
                        match['season'] = season
                    all_data.extend(matches)
                    
                    st.write(f"  ✅ {len(matches)} partidos de {season}")
            
            time.sleep(1)  # Pausa entre ligas
        
        return all_data
