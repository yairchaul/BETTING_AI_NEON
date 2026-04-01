# -*- coding: utf-8 -*-
"""
GESTOR UNIVERSAL DE LIGAS - Versión unificada con datos dinámicos
Obtiene ligas y partidos desde API de ESPN
"""

import requests
import json
import logging
from espn_league_codes import ESPNLeagueCodes

logger = logging.getLogger(__name__)

class GestorLigasUniversal:
    def __init__(self):
        self.cache = {}
        self.ligas_disponibles = None
        self._cargar_ligas_desde_api()
    
    def _cargar_ligas_desde_api(self):
        """Carga ligas dinámicamente desde API de ESPN"""
        try:
            # Usar el método obtener_todas() de ESPNLeagueCodes
            self.ligas_disponibles = ESPNLeagueCodes.obtener_todas()
            logger.info(f"✅ {len(self.ligas_disponibles)} ligas cargadas desde API")
        except Exception as e:
            logger.error(f"Error cargando ligas: {e}")
            # Fallback: ligas populares
            self.ligas_disponibles = [
                "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
                "Liga MX", "MLS", "Eredivisie", "Primeira Liga", "Scottish Premiership",
                "A-League", "J1 League", "K League 1", "Saudi Pro League",
                "Argentine Liga Profesional", "Brazilian Serie A", "Chilean Primera Division"
            ]
    
    def obtener_ligas(self):
        """Retorna lista de todas las ligas disponibles"""
        return self.ligas_disponibles if self.ligas_disponibles else []
    
    def obtener_partidos(self, nombre_liga):
        """Obtiene partidos de una liga específica desde API de ESPN"""
        if nombre_liga in self.cache:
            return self.cache[nombre_liga]
        
        codigo = ESPNLeagueCodes.obtener_codigo(nombre_liga)
        if not codigo:
            logger.warning(f"No se encontró código para {nombre_liga}")
            return []
        
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{codigo}/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Error {response.status_code} para {nombre_liga}")
                return []
            
            data = response.json()
            partidos = []
            
            for event in data.get('events', []):
                comp = event.get('competitions', [{}])[0]
                competitors = comp.get('competitors', [])
                
                if len(competitors) >= 2:
                    local_data = competitors[0].get('team', {})
                    visitante_data = competitors[1].get('team', {})
                    
                    partido = {
                        'local': local_data.get('displayName', 'Local'),
                        'visitante': visitante_data.get('displayName', 'Visitante'),
                        'liga': nombre_liga,
                        'fecha': event.get('date', ''),
                        'status': 'programado'
                    }
                    
                    # Extraer marcador si existe
                    scores = comp.get('scores', [])
                    if len(scores) >= 2:
                        partido['goles_local'] = scores[0].get('value')
                        partido['goles_visitante'] = scores[1].get('value')
                        partido['status'] = 'finalizado'
                    
                    partidos.append(partido)
            
            self.cache[nombre_liga] = partidos
            logger.info(f"✅ {len(partidos)} partidos para {nombre_liga}")
            return partidos
            
        except Exception as e:
            logger.error(f"Error cargando {nombre_liga}: {e}")
            return []
    
    def obtener_estadisticas_equipo(self, equipo, liga):
        """Obtiene estadísticas de un equipo desde historial"""
        try:
            import sqlite3
            conn = sqlite3.connect('data/betting_stats.db')
            c = conn.cursor()
            c.execute('''
                SELECT puntos_favor, puntos_contra, fecha 
                FROM historial_equipos 
                WHERE nombre_equipo = ? AND deporte = 'futbol'
                ORDER BY fecha DESC LIMIT 5
            ''', (equipo,))
            rows = c.fetchall()
            conn.close()
            
            if rows and len(rows) >= 3:
                goles = [r[0] for r in rows]
                return {
                    'goles_favor': [r[0] for r in rows],
                    'goles_contra': [r[1] for r in rows],
                    'promedio': sum(goles) / len(goles),
                    'partidos': len(rows)
                }
        except:
            pass
        
        # Datos mock basados en nombre (transitorio)
        equipos_fuertes = ["Manchester", "Liverpool", "Arsenal", "Chelsea", "Barcelona", 
                          "Real Madrid", "Bayern", "PSG", "Juventus", "Milan", "Inter"]
        
        if any(fuerte in equipo for fuerte in equipos_fuertes):
            return {
                'goles_favor': [3, 2, 4, 1, 3],
                'goles_contra': [1, 1, 2, 1, 0],
                'promedio': 2.6,
                'partidos': 5
            }
        else:
            return {
                'goles_favor': [1, 0, 1, 1, 0],
                'goles_contra': [2, 1, 2, 1, 2],
                'promedio': 0.8,
                'partidos': 5
            }
    
    def limpiar_cache(self):
        """Limpia el caché de partidos"""
        self.cache = {}
