# modules/team_matcher.py
import requests
import unicodedata
import re
from difflib import SequenceMatcher

class TeamMatcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = {}
    
    def normalize(self, name):
        """Normalización avanzada para matching"""
        # Convertir a minúsculas
        name = name.lower().strip()
        
        # Quitar acentos
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Quitar caracteres especiales
        name = re.sub(r'[^a-z0-9\s]', '', name)
        
        # Quitar palabras comunes
        common_words = ['fc', 'cf', 'sc', 'ac', 'us', 'as', 'cd', 'real', 
                       'united', 'city', 'athletic', 'deportivo', 'club', 
                       'team', 'de', 'del', 'la', 'el', 'los', 'las',
                       'and', '&', 'vs', 'v']
        for word in common_words:
            name = re.sub(r'\b' + word + r'\b', '', name)
        
        # Quitar espacios múltiples
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def similarity(self, a, b):
        """Calcula similitud con múltiples estrategias"""
        n1 = self.normalize(a)
        n2 = self.normalize(b)
        
        # Similitud de secuencia
        ratio = SequenceMatcher(None, n1, n2).ratio()
        
        # Bonus si una cadena contiene a la otra
        if n1 in n2 or n2 in n1:
            ratio += 0.1
            
        return min(ratio, 1.0)
    
    def find_team(self, team_name, league_hint=None):
        """Busca equipo con estrategias múltiples"""
        cache_key = f"{team_name}_{league_hint}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.api_key:
            return None
        
        try:
            headers = {'x-apisports-key': self.api_key}
            
            # Estrategia 1: Búsqueda exacta
            search_name = requests.utils.quote(team_name)
            url = f"https://v3.football.api-sports.io/teams?search={search_name}"
            response = requests.get(url, headers=headers).json()
            
            if response.get('results', 0) > 0:
                # Verificar similitud
                best_match = None
                best_score = 0
                
                for item in response['response']:
                    team = item['team']
                    score = self.similarity(team_name, team['name'])
                    if score > best_score and score > 0.5:
                        best_score = score
                        best_match = team
                
                if best_match:
                    self.cache[cache_key] = best_match
                    return best_match
            
            # Estrategia 2: Si hay liga, buscar en esa liga
            if league_hint and league_hint != "Detectada de imagen":
                league_norm = self.normalize(league_hint)
                league_url = f"https://v3.football.api-sports.io/leagues?search={league_norm}"
                league_resp = requests.get(league_url, headers=headers).json()
                
                if league_resp.get('results', 0) > 0:
                    league_id = league_resp['response'][0]['league']['id']
                    teams_url = f"https://v3.football.api-sports.io/teams?league={league_id}&season=2024"
                    teams_resp = requests.get(teams_url, headers=headers).json()
                    
                    best_match = None
                    best_score = 0
                    
                    for item in teams_resp.get('response', []):
                        team = item['team']
                        score = self.similarity(team_name, team['name'])
                        if score > best_score and score > 0.4:
                            best_score = score
                            best_match = team
                    
                    if best_match:
                        self.cache[cache_key] = best_match
                        return best_match
            
            # Estrategia 3: Búsqueda por palabra más significativa
            words = team_name.split()
            for word in words:
                if len(word) > 3:
                    url = f"https://v3.football.api-sports.io/teams?search={word}"
                    response = requests.get(url, headers=headers).json()
                    
                    if response.get('results', 0) > 0:
                        for item in response['response']:
                            team = item['team']
                            score = self.similarity(team_name, team['name'])
                            if score > 0.6:
                                self.cache[cache_key] = team
                                return team
            
        except Exception as e:
            print(f"Error buscando equipo: {e}")
        
        self.cache[cache_key] = None
        return None
