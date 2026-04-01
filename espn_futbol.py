# -*- coding: utf-8 -*-
"""
ESPN FÚTBOL - Scraper que usa API de ESPN para obtener todas las ligas
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPN_FUTBOL:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        self._ligas_cache = None

    def get_available_leagues(self):
        """Obtiene todas las ligas desde la API de ESPN"""
        if self._ligas_cache is not None:
            return self._ligas_cache
        
        logger.info("🔍 Obteniendo ligas desde API ESPN...")
        
        # API de ESPN para ligas de fútbol
        api_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/leagues"
        
        try:
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                ligas = []
                
                for league in data.get('leagues', []):
                    league_name = league.get('name') or league.get('displayName')
                    if league_name:
                        ligas.append(league_name)
                
                if ligas:
                    logger.info(f"✅ {len(ligas)} ligas obtenidas de API ESPN")
                    self._ligas_cache = ligas
                    return ligas
                    
        except Exception as e:
            logger.error(f"Error obteniendo ligas de API: {e}")
        
        # Fallback: ligas más populares (solo si la API falla)
        logger.warning("⚠️ API falló, usando ligas populares como fallback")
        ligas_fallback = [
            "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
            "Liga MX", "MLS", "Eredivisie", "Primeira Liga", "Scottish Premiership"
        ]
        self._ligas_cache = ligas_fallback
        return ligas_fallback

    def get_games(self, liga_nombre):
        """Obtiene los partidos de una liga específica"""
        logger.info(f"🔍 Obteniendo partidos de {liga_nombre}...")
        
        # Buscar ID de la liga por nombre
        league_id = self._buscar_id_liga(liga_nombre)
        if not league_id:
            logger.warning(f"No se encontró ID para {liga_nombre}")
            return []
        
        # API de ESPN para partidos
        api_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/scoreboard"
        
        try:
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                partidos = []
                
                events = data.get('events', [])
                for event in events:
                    competitions = event.get('competitions', [])
                    for comp in competitions:
                        competitors = comp.get('competitors', [])
                        if len(competitors) >= 2:
                            local = competitors[0].get('team', {}).get('displayName', '')
                            visitante = competitors[1].get('team', {}).get('displayName', '')
                            
                            # Extraer marcador si existe
                            scores = comp.get('scores', [])
                            if len(scores) >= 2:
                                local_score = scores[0].get('value')
                                visitante_score = scores[1].get('value')
                            else:
                                local_score = None
                                visitante_score = None
                            
                            partidos.append({
                                'home': local,
                                'away': visitante,
                                'home_score': local_score,
                                'away_score': visitante_score,
                                'liga': liga_nombre,
                                'status': 'programado' if not local_score else 'finalizado'
                            })
                
                logger.info(f"✅ {len(partidos)} partidos obtenidos para {liga_nombre}")
                return partidos
                
        except Exception as e:
            logger.error(f"Error obteniendo partidos: {e}")
        
        return []

    def _buscar_id_liga(self, nombre_liga):
        """Busca el ID de una liga por su nombre"""
        # Mapeo de nombres a IDs (fallback rápido)
        mapeo = {
            "Premier League": "eng.1",
            "La Liga": "esp.1",
            "Serie A": "ita.1",
            "Bundesliga": "ger.1",
            "Ligue 1": "fra.1",
            "Liga MX": "mex.1",
            "MLS": "usa.1",
        }
        
        if nombre_liga in mapeo:
            return mapeo[nombre_liga]
        
        # Si no está en el mapeo, buscar en la lista de ligas
        for liga in self.get_available_leagues():
            if liga == nombre_liga:
                # Intentar derivar ID del nombre
                partes = nombre_liga.lower().replace(' ', '_')
                return partes[:10]
        
        return None
