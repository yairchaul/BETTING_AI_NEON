# modules/smart_searcher.py
import requests
import unicodedata
import re
from difflib import SequenceMatcher
import streamlit as st
from groq import Groq

class SmartSearcher:
    def __init__(self):
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
        self.google_cse_id = st.secrets.get("GOOGLE_CSE_ID", "")
        self.odds_api_key = st.secrets.get("ODDS_API_KEY", "")
        self.groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "")) if st.secrets.get("GROQ_API_KEY") else None
        self.cache = {}
    
    def find_team(self, team_name, context=None):
        """Busca equipo con múltiples estrategias, incluyendo Groq como respaldo"""
        
        # Intentar con métodos tradicionales
        team = self._find_team_traditional(team_name)
        if team:
            return team
        
        # Si no encuentra, usar Groq para interpretar el nombre
        if self.groq_client:
            team = self._find_team_with_groq(team_name, context)
            if team:
                return team
        
        return None
    
    def _find_team_traditional(self, team_name):
        """Métodos tradicionales de búsqueda"""
        cache_key = f"trad_{team_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Intentar con Football API
        team = self._search_football_api(team_name)
        if team:
            self.cache[cache_key] = team
            return team
        
        # Intentar con Google CSE
        team = self._search_google_cse(team_name)
        if team:
            self.cache[cache_key] = team
            return team
        
        self.cache[cache_key] = None
        return None
    
    def _find_team_with_groq(self, team_name, context):
        """Usa Groq para interpretar nombres corruptos del OCR"""
        try:
            prompt = f"""
            El texto OCR extrajo este posible nombre de equipo: "{team_name}"
            Contexto adicional: {context if context else 'Sin contexto'}
            
            ¿Cuál es el nombre REAL de este equipo de fútbol?
            Responde SOLO con el nombre correcto, nada más.
            Si no estás seguro, responde "DESCONOCIDO".
            """
            
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            corrected_name = response.choices[0].message.content.strip()
            
            if corrected_name != "DESCONOCIDO":
                # Buscar el nombre corregido en la API
                return self._search_football_api(corrected_name)
            
        except Exception as e:
            st.warning(f"Groq no pudo interpretar {team_name}: {e}")
        
        return None
    
    def _search_football_api(self, team_name):
        """Busca en API-Football"""
        if not self.football_api_key:
            return None
        
        try:
            headers = {'x-apisports-key': self.football_api_key}
            url = f"https://v3.football.api-sports.io/teams?search={team_name}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                # Encontrar el mejor match por similitud
                best_match = None
                best_score = 0
                
                for item in response['response']:
                    team = item['team']
                    score = self._similarity(team_name, team['name'])
                    if score > best_score and score > 0.6:
                        best_score = score
                        best_match = team
                
                return best_match
        except:
            pass
        return None
    
    def _search_google_cse(self, team_name):
        """Busca en Google Custom Search"""
        if not self.google_api_key or not self.google_cse_id:
            return None
        
        try:
            query = f"{team_name} football team"
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={self.google_cse_id}&key={self.google_api_key}"
            response = requests.get(url, timeout=5).json()
            
            # Extraer posibles nombres de los snippets
            for item in response.get('items', [])[:3]:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                
                # Buscar patrones de nombres de equipos
                teams = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', title + " " + snippet)
                for team in teams:
                    if len(team) > 3 and self._similarity(team_name, team) > 0.5:
                        return {'name': team, 'source': 'google_cse'}
        except:
            pass
        return None
    
    def _similarity(self, a, b):
        """Calcula similitud entre strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()