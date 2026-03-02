import requests
import unicodedata
import re
from difflib import SequenceMatcher

class TeamMatcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = {}
    
    def normalize(self, name):
        """Normaliza nombres para comparación"""
        name = unicodedata.normalize('NFKD', name.lower())
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        name = re.sub(r'[^a-z0-9]', '', name)
        return name
    
    def similarity(self, a, b):
        """Calcula similitud entre dos nombres"""
        return SequenceMatcher(None, self.normalize(a), self.normalize(b)).ratio()
    
    def find_team(self, team_name, league_hint=None):
        """Busca equipo en API-Sports"""
        cache_key = f"{team_name}_{league_hint}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.api_key:
            return None
        
        try:
            headers = {'x-apisports-key': self.api_key}
            
            # Búsqueda directa
            url = f"https://v3.football.api-sports.io/teams?search={team_name}"
            response = requests.get(url, headers=headers).json()
            
            if response.get('results', 0) > 0:
                team = response['response'][0]['team']
                self.cache[cache_key] = team
                return team
            
            # Búsqueda por liga si hay hint
            if league_hint:
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
                        if score > best_score and score > 0.6:
                            best_score = score
                            best_match = team
                    
                    if best_match:
                        self.cache[cache_key] = best_match
                        return best_match
        except:
            pass
        
        self.cache[cache_key] = None
        return None
