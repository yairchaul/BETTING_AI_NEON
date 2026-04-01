# -*- coding: utf-8 -*-
"""
ESPN FÚTBOL - Módulo exclusivo para fútbol con gestor universal
"""

import logging
import requests
import json

logger = logging.getLogger(__name__)

class GestorLigasUniversal:
    """Gestor de ligas que obtiene datos desde API de ESPN"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        self._ligas_cache = None
    
    def obtener_ligas(self):
        """Obtiene todas las ligas desde API de ESPN"""
        if self._ligas_cache:
            return self._ligas_cache
        
        try:
            api_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/leagues"
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                ligas = []
                for league in data.get('leagues', []):
                    name = league.get('name') or league.get('displayName')
                    if name:
                        ligas.append(name)
                
                if ligas:
                    self._ligas_cache = ligas
                    return ligas
        except Exception as e:
            logger.error(f"Error obteniendo ligas: {e}")
        
        # Fallback: ligas populares
        self._ligas_cache = [
            "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
            "Liga MX", "MLS", "Eredivisie", "Primeira Liga", "Scottish Premiership",
            "Russian Premier League", "Turkish Super Lig", "Belgian Pro League",
            "Swiss Super League", "Austrian Bundesliga", "Greek Super League",
            "Czech First League", "Croatian First League", "Danish Superliga",
            "Norwegian Eliteserien", "Swedish Allsvenskan", "Polish Ekstraklasa"
        ]
        return self._ligas_cache
    
    def obtener_partidos(self, liga_nombre):
        """Obtiene partidos de una liga específica"""
        # Mapeo de ligas a IDs
        ligas_ids = {
            "Premier League": "eng.1",
            "La Liga": "esp.1",
            "Serie A": "ita.1",
            "Bundesliga": "ger.1",
            "Ligue 1": "fra.1",
            "Liga MX": "mex.1",
            "MLS": "usa.1",
            "Eredivisie": "ned.1",
            "Primeira Liga": "por.1",
            "Scottish Premiership": "sco.1",
        }
        
        league_id = ligas_ids.get(liga_nombre)
        if not league_id:
            return []
        
        try:
            api_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/scoreboard"
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                partidos = []
                
                for event in data.get('events', []):
                    for comp in event.get('competitions', []):
                        competitors = comp.get('competitors', [])
                        if len(competitors) >= 2:
                            local = competitors[0].get('team', {}).get('displayName', '')
                            visitante = competitors[1].get('team', {}).get('displayName', '')
                            
                            partidos.append({
                                'home': local,
                                'away': visitante,
                                'liga': liga_nombre,
                                'status': 'programado'
                            })
                
                return partidos
        except Exception as e:
            logger.error(f"Error obteniendo partidos: {e}")
        
        return []


class ESPN_FUTBOL:
    def __init__(self):
        self.gestor = GestorLigasUniversal()
    
    def get_available_leagues(self):
        """Retorna todas las ligas disponibles"""
        return self.gestor.obtener_ligas()
    
    def get_games(self, liga):
        """Obtiene partidos de una liga específica"""
        return self.gestor.obtener_partidos(liga)
