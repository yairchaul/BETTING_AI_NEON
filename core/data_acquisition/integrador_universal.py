import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# =============================================================================
# INTEGRADOR DE NBA (nba-api)
# =============================================================================
try:
    from nba_api.stats.static import teams, players
    from nba_api.stats.endpoints import teamgamelog, playergamelog, scoreboard
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False

class NBAIntegrator:
    # Obtiene datos REALES de NBA.com
    
    def __init__(self):
        self.cache_teams = {}
        self.cache_stats = {}
        self.available = NBA_API_AVAILABLE
    
    def get_team_id(self, team_name):
        # Obtiene el ID del equipo desde nba-api
        if not self.available:
            return None
        
        all_teams = teams.get_teams()
        for team in all_teams:
            if team_name.lower() in team['full_name'].lower():
                return team['id']
        return None
    
    def get_team_stats(self, team_name, days=30):
        # Obtiene estadísticas reales de un equipo
        if not self.available:
            return self._get_mock_stats(team_name)
        
        cache_key = f"{team_name}_{days}"
        if cache_key in self.cache_stats:
            return self.cache_stats[cache_key]
        
        team_id = self.get_team_id(team_name)
        if not team_id:
            return self._get_mock_stats(team_name)
        
        try:
            # Obtener últimos 10 juegos
            gamelog = teamgamelog.TeamGameLog(team_id=team_id, season='2024-25')
            games = gamelog.get_data_frames()[0].head(10)
            
            if len(games) > 0:
                stats = {
                    'points': round(games['PTS'].mean(), 1),
                    'points_allowed': round(games['OPP_PTS'].mean(), 1),
                    'assists': round(games['AST'].mean(), 1),
                    'rebounds': round(games['REB'].mean(), 1),
                    'fg_pct': round(games['FG_PCT'].mean(), 3),
                    'win_rate': round(len(games[games['WL'] == 'W']) / len(games), 2),
                    'last_10': games['WL'].tolist()[:10]
                }
                self.cache_stats[cache_key] = stats
                return stats
        except Exception as e:
            st.warning(f"Error obteniendo datos NBA: {e}")
        
        return self._get_mock_stats(team_name)
    
    def get_todays_games(self):
        # Obtiene partidos NBA de hoy
        if not self.available:
            return []
        
        try:
            board = scoreboard.Scoreboard()
            games = board.get_data_frames()[0]
            today_games = []
            for _, game in games.iterrows():
                today_games.append({
                    'home_team': game['HOME_TEAM_NAME'],
                    'away_team': game['VISITOR_TEAM_NAME'],
                    'home_score': game['HOME_TEAM_SCORE'],
                    'away_score': game['VISITOR_TEAM_SCORE'],
                    'status': game['GAME_STATUS_TEXT'],
                    'game_time': game['GAME_TIME']
                })
            return today_games
        except Exception as e:
            st.warning(f"Error obteniendo partidos NBA: {e}")
            return []
    
    def _get_mock_stats(self, team_name):
        # Datos de respaldo
        mock_stats = {
            'Lakers': {'points': 115.2, 'points_allowed': 112.8, 'win_rate': 0.65},
            'Celtics': {'points': 118.5, 'points_allowed': 110.2, 'win_rate': 0.75},
            'Warriors': {'points': 116.8, 'points_allowed': 114.5, 'win_rate': 0.60},
            'Nuggets': {'points': 114.5, 'points_allowed': 111.2, 'win_rate': 0.70},
            'Bucks': {'points': 117.2, 'points_allowed': 113.5, 'win_rate': 0.68},
            'Suns': {'points': 115.8, 'points_allowed': 112.5, 'win_rate': 0.62},
        }
        return mock_stats.get(team_name, {'points': 112.0, 'points_allowed': 112.0, 'win_rate': 0.50})

# =============================================================================
# INTEGRADOR DE UFC (FightMatrix via PolyData)
# =============================================================================
class UFCIntegrator:
    # Obtiene datos REALES de peleadores usando la alianza PolyData + FightMatrix 
    
    def __init__(self):
        self.base_url = "https://api.polydata.co/fightmatrix"
        self.cache_fighters = {}
    
    def get_fighter_stats(self, fighter_name):
        # Obtiene estadísticas REALES de un peleador desde FightMatrix 
        cache_key = fighter_name.lower().replace(' ', '_')
        if cache_key in self.cache_fighters:
            return self.cache_fighters[cache_key]
        
        # Por ahora usamos datos simulados hasta tener la API
        # En producción, haríamos: 
        # response = requests.get(f"{self.base_url}/fighter/{fighter_name}")
        # return response.json()
        
        stats = self._get_mock_fighter_stats(fighter_name)
        self.cache_fighters[cache_key] = stats
        return stats
    
    def _get_mock_fighter_stats(self, fighter_name):
        # Datos de respaldo basados en peleadores reales 
        mock_data = {
            'Jon Jones': {'win_rate': 0.96, 'ko_rate': 0.37, 'sub_rate': 0.26, 'reach': 215, 'age': 37},
            'Stipe Miocic': {'win_rate': 0.83, 'ko_rate': 0.60, 'sub_rate': 0.05, 'reach': 203, 'age': 42},
            'Islam Makhachev': {'win_rate': 0.96, 'ko_rate': 0.15, 'sub_rate': 0.46, 'reach': 179, 'age': 33},
            'Alex Pereira': {'win_rate': 0.83, 'ko_rate': 0.67, 'sub_rate': 0.00, 'reach': 203, 'age': 37},
            'Piera Rodriguez': {'win_rate': 0.85, 'ko_rate': 0.18, 'sub_rate': 0.18, 'reach': 170, 'age': 28},
            'Sam Hughes': {'win_rate': 0.65, 'ko_rate': 0.09, 'sub_rate': 0.09, 'reach': 168, 'age': 30},
            'Josh Emmett': {'win_rate': 0.76, 'ko_rate': 0.48, 'sub_rate': 0.04, 'reach': 178, 'age': 39},
            'Kevin Vallejos': {'win_rate': 0.94, 'ko_rate': 0.59, 'sub_rate': 0.06, 'reach': 182, 'age': 23},
        }
        
        # Buscar por nombre parcial
        for name, stats in mock_data.items():
            if name.lower() in fighter_name.lower() or fighter_name.lower() in name.lower():
                return stats
        
        # Datos por defecto
        return {'win_rate': 0.7, 'ko_rate': 0.4, 'sub_rate': 0.2, 'reach': 180, 'age': 30}

# =============================================================================
# INTEGRADOR DE FÚTBOL (Football-Data.org)
# =============================================================================
class FootballIntegrator:
    # Obtiene datos REALES de fútbol desde Football-Data.org
    
    def __init__(self):
        self.api_key = st.secrets.get('FOOTBALL_API_KEY', '')
        self.base_url = "https://api.football-data.org/v4"
        self.cache_teams = {}
        
        # Mapeo de ligas a códigos
        self.league_codes = {
            'Premier League': 'PL',
            'La Liga': 'PD',
            'Bundesliga': 'BL1',
            'Serie A': 'SA',
            'Ligue 1': 'FL1',
            'Eredivisie': 'NL',
            'Primeira Liga': 'PPL',
            'Champions League': 'CL',
            'Liga MX': 'MEX',
        }
    
    def get_team_stats(self, team_name, competition):
        # Obtiene estadísticas de un equipo (simulado por ahora)
        # En producción usaríamos la API de Football-Data.org
        power_base = {
            'Manchester City': {'attack': 2.4, 'defense': 0.8},
            'Liverpool': {'attack': 2.2, 'defense': 0.9},
            'Arsenal': {'attack': 2.1, 'defense': 0.9},
            'Real Madrid': {'attack': 2.3, 'defense': 0.8},
            'Barcelona': {'attack': 2.2, 'defense': 0.9},
            'Bayern': {'attack': 2.5, 'defense': 0.7},
            'PSG': {'attack': 2.3, 'defense': 0.8},
            'Atlético': {'attack': 1.8, 'defense': 1.0},
            'Tottenham': {'attack': 1.9, 'defense': 1.1},
            'Chelsea': {'attack': 2.0, 'defense': 0.9},
            'Newcastle': {'attack': 1.8, 'defense': 1.0},
            'Atalanta': {'attack': 2.1, 'defense': 1.1},
            'Bayer': {'attack': 2.0, 'defense': 0.9},
            'Galatasaray': {'attack': 1.9, 'defense': 1.0},
            'Sporting': {'attack': 1.8, 'defense': 1.0},
            'Benfica': {'attack': 2.0, 'defense': 0.9},
        }
        
        for name, stats in power_base.items():
            if name.lower() in team_name.lower():
                return stats
        
        return {'attack': 1.7, 'defense': 1.1}
