# modules/smart_searcher.py
import requests
import unicodedata
import re
from difflib import SequenceMatcher
import streamlit as st
import time

class SmartSearcher:
    def __init__(self):
        """Inicializa con todas las APIs disponibles en secrets"""
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
        self.google_cse_id = st.secrets.get("GOOGLE_CSE_ID", "")
        self.odds_api_key = st.secrets.get("ODDS_API_KEY", "")
        self.cache = {}  # Cache para no repetir búsquedas
        
    def normalize_name(self, name):
        """Normalización ultra-agresiva para matching"""
        if not name:
            return ""
        
        # Guardar original para debug
        original = name
        
        # Minúsculas y sin acentos
        name = name.lower().strip()
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Eliminar caracteres especiales y números
        name = re.sub(r'[^a-z\s]', '', name)
        
        # Diccionario de reemplazos comunes para ligas españolas
        replacements = {
            # Real Madrid variations
            'real madrid': 'real madrid',
            'r madrid': 'real madrid',
            'real m': 'real madrid',
            'realmadrid': 'real madrid',
            'real madrid cf': 'real madrid',
            
            # Atlético Madrid variations
            'atletico madrid': 'atletico madrid',
            'at madrid': 'atletico madrid',
            'atleti': 'atletico madrid',
            'atletico': 'atletico madrid',
            'atlético madrid': 'atletico madrid',
            
            # Barcelona variations
            'barcelona': 'barcelona',
            'barça': 'barcelona',
            'fc barcelona': 'barcelona',
            'barca': 'barcelona',
            
            # Rayo Vallecano
            'rayo vallecano': 'rayo vallecano',
            'rayo': 'rayo vallecano',
            'ra yo': 'rayo vallecano',
            
            # Celta de Vigo
            'celta de vigo': 'celta vigo',
            'celta': 'celta vigo',
            'vigo': 'celta vigo',
            
            # Osasuna
            'osasuna': 'osasuna',
            'ossa': 'osasuna',
            
            # Levante
            'levante': 'levante',
            
            # Getafe
            'getafe': 'getafe',
            
            # Girona
            'girona': 'girona',
            
            # Mallorca
            'mallorca': 'rcd mallorca',
            'rcd mallorca': 'rcd mallorca',
            
            # Real Oviedo
            'real oviedo': 'real oviedo',
            'oviedo': 'real oviedo',
        }
        
        # Aplicar reemplazos exactos primero
        for key, value in replacements.items():
            if key in name:
                return value
        
        # Si no hay reemplazo exacto, eliminar palabras comunes
        common_words = ['fc', 'cf', 'sc', 'ac', 'cd', 'ud', 'sd', 'club', 'deportivo', 
                       'real', 'united', 'city', 'athletic', 'sporting', 'racing',
                       'sociedad', 'cultural', 'team']
        for word in common_words:
            name = name.replace(word, '')
        
        # Eliminar espacios y devolver
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def similarity_score(self, a, b):
        """Calcula similitud entre dos nombres"""
        n1 = self.normalize_name(a)
        n2 = self.normalize_name(b)
        
        if not n1 or not n2:
            return 0
        
        # Similitud de secuencia
        ratio = SequenceMatcher(None, n1, n2).ratio()
        
        # Bonus si uno contiene al otro
        if n1 in n2 or n2 in n1:
            ratio += 0.15
        
        # Bonus por palabras clave
        words1 = set(n1.split())
        words2 = set(n2.split())
        common_words = words1.intersection(words2)
        if common_words:
            ratio += 0.05 * len(common_words)
        
        return min(ratio, 1.0)
    
    def search_football_api(self, team_name):
        """Búsqueda en API-Football"""
        if not self.football_api_key:
            return None
        
        cache_key = f"football_{team_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {'x-apisports-key': self.football_api_key}
            
            # Estrategia 1: Búsqueda exacta
            url = f"https://v3.football.api-sports.io/teams?search={team_name}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            best_match = None
            best_score = 0
            
            if response.get('results', 0) > 0:
                for item in response['response']:
                    team = item['team']
                    score = self.similarity_score(team_name, team['name'])
                    if score > best_score:
                        best_score = score
                        best_match = team
            
            if best_score > 0.7:  # Umbral más bajo
                self.cache[cache_key] = best_match
                return best_match
            
            # Estrategia 2: Búsqueda por liga (LaLiga)
            leagues_url = "https://v3.football.api-sports.io/leagues?country=Spain&season=2024"
            leagues_resp = requests.get(leagues_url, headers=headers, timeout=5).json()
            
            for league in leagues_resp.get('response', []):
                league_id = league['league']['id']
                teams_url = f"https://v3.football.api-sports.io/teams?league={league_id}&season=2024"
                teams_resp = requests.get(teams_url, headers=headers, timeout=5).json()
                
                for item in teams_resp.get('response', []):
                    team = item['team']
                    score = self.similarity_score(team_name, team['name'])
                    if score > best_score and score > 0.6:
                        best_score = score
                        best_match = team
            
            if best_score > 0.6:
                self.cache[cache_key] = best_match
                return best_match
            
        except Exception as e:
            print(f"Error en Football API: {e}")
        
        self.cache[cache_key] = None
        return None
    
    def search_google_cse(self, team_name):
        """Búsqueda en Google Custom Search para encontrar IDs"""
        if not self.google_api_key or not self.google_cse_id:
            return None
        
        cache_key = f"google_{team_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Búsqueda específica para API-Sports
            query = f"{team_name} football team api-sports id"
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={self.google_cse_id}&key={self.google_api_key}"
            response = requests.get(url, timeout=5).json()
            
            # Buscar IDs en los resultados
            import json
            for item in response.get('items', []):
                snippet = item.get('snippet', '')
                # Buscar patrones de ID (números de 4-6 dígitos)
                ids = re.findall(r'\b\d{4,6}\b', snippet)
                if ids:
                    # Intentar verificar el ID con la Football API
                    if self.football_api_key:
                        headers = {'x-apisports-key': self.football_api_key}
                        verify_url = f"https://v3.football.api-sports.io/teams?id={ids[0]}"
                        verify_resp = requests.get(verify_url, headers=headers, timeout=5).json()
                        
                        if verify_resp.get('results', 0) > 0:
                            team = verify_resp['response'][0]['team']
                            self.cache[cache_key] = team
                            return team
            
            # Si no encuentra ID, buscar nombre en resultados
            for item in response.get('items', []):
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                full_text = title + " " + snippet
                
                # Buscar nombres de equipos conocidos
                known_teams = ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla']
                for known in known_teams:
                    if known.lower() in full_text.lower():
                        # Intentar búsqueda en Football API con ese nombre
                        return self.search_football_api(known)
                        
        except Exception as e:
            print(f"Error en Google CSE: {e}")
        
        self.cache[cache_key] = None
        return None
    
    def search_odds_api(self, team_name):
        """Búsqueda en Odds API para obtener referencias"""
        if not self.odds_api_key:
            return None
        
        cache_key = f"odds_{team_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Obtener próximos eventos
            url = f"https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/odds/?apiKey={self.odds_api_key}&regions=us&markets=h2h"
            response = requests.get(url, timeout=5).json()
            
            best_match = None
            best_score = 0
            
            for event in response:
                home = event.get('home_team', '')
                away = event.get('away_team', '')
                
                for team in [home, away]:
                    score = self.similarity_score(team_name, team)
                    if score > best_score and score > 0.6:
                        best_score = score
                        best_match = {
                            'id': f"odds_{event['id']}",
                            'name': team,
                            'source': 'odds_api'
                        }
            
            if best_match:
                self.cache[cache_key] = best_match
                return best_match
                
        except Exception as e:
            print(f"Error en Odds API: {e}")
        
        self.cache[cache_key] = None
        return None
    
    def find_team(self, team_name):
        """Busca equipo usando TODAS las APIs disponibles con estrategias múltiples"""
        
        # Intentar con Football API primero (la más confiable)
        team = self.search_football_api(team_name)
        if team:
            return team
        
        # Intentar con Google CSE
        team = self.search_google_cse(team_name)
        if team:
            return team
        
        # Intentar con Odds API
        team = self.search_odds_api(team_name)
        if team:
            return team
        
        # Último recurso: lista hardcodeada de equipos españoles
        spain_teams = {
            'real madrid': {'id': 541, 'name': 'Real Madrid'},
            'barcelona': {'id': 529, 'name': 'Barcelona'},
            'atletico madrid': {'id': 530, 'name': 'Atletico Madrid'},
            'atlético madrid': {'id': 530, 'name': 'Atletico Madrid'},
            'sevilla': {'id': 536, 'name': 'Sevilla'},
            'real betis': {'id': 537, 'name': 'Real Betis'},
            'real sociedad': {'id': 548, 'name': 'Real Sociedad'},
            'athletic bilbao': {'id': 531, 'name': 'Athletic Bilbao'},
            'valencia': {'id': 532, 'name': 'Valencia'},
            'villareal': {'id': 533, 'name': 'Villarreal'},
            'osasuna': {'id': 727, 'name': 'Osasuna'},
            'celta vigo': {'id': 538, 'name': 'Celta Vigo'},
            'rayo vallecano': {'id': 728, 'name': 'Rayo Vallecano'},
            'getafe': {'id': 546, 'name': 'Getafe'},
            'girona': {'id': 547, 'name': 'Girona'},
            'mallorca': {'id': 798, 'name': 'RCD Mallorca'},
            'levante': {'id': 539, 'name': 'Levante'},
            'real oviedo': {'id': 1040, 'name': 'Real Oviedo'},
        }
        
        normalized = self.normalize_name(team_name)
        for key, value in spain_teams.items():
            if key in normalized or normalized in key:
                return value
        
        return None
    
    def get_last_5_matches(self, team_id):
        """Obtiene los últimos 5 partidos de un equipo"""
        if not self.football_api_key or not team_id:
            return None
        
        cache_key = f"matches_{team_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {'x-apisports-key': self.football_api_key}
            url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            matches = []
            for game in response.get('response', []):
                is_home = game['teams']['home']['id'] == team_id
                
                # Obtener goles (manejar None)
                goals_home = game['goals']['home'] if game['goals']['home'] is not None else 0
                goals_away = game['goals']['away'] if game['goals']['away'] is not None else 0
                
                match = {
                    'date': game['fixture']['date'][:10],
                    'home': game['teams']['home']['name'],
                    'away': game['teams']['away']['name'],
                    'goals_home': goals_home,
                    'goals_away': goals_away,
                    'result': 'G' if (is_home and goals_home > goals_away) or 
                                    (not is_home and goals_away > goals_home) else
                             'E' if goals_home == goals_away else 'P'
                }
                matches.append(match)
            
            self.cache[cache_key] = matches
            return matches
        except Exception as e:
            print(f"Error obteniendo matches: {e}")
            return None
