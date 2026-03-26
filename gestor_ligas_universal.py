"""
GESTOR UNIVERSAL DE LIGAS - Versión corregida
"""
import requests
import json
from espn_league_codes import ESPNLeagueCodes

class GestorLigasUniversal:
    def __init__(self):
        self.cache = {}
        # Usar el método obtener_todas() en lugar de CODIGOS_CONFIRMADOS
        self.ligas_disponibles = ESPNLeagueCodes.obtener_todas()
    
    def obtener_partidos(self, nombre_liga):
        """Obtiene partidos de una liga específica"""
        if nombre_liga in self.cache:
            return self.cache[nombre_liga]
        
        codigo = ESPNLeagueCodes.obtener_codigo(nombre_liga)
        if not codigo:
            return []
        
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{codigo}/scoreboard"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            partidos = []
            
            for event in data.get('events', []):
                comp = event.get('competitions', [{}])[0]
                competitors = comp.get('competitors', [])
                if len(competitors) >= 2:
                    partido = {
                        'local': competitors[0].get('team', {}).get('displayName', 'Local'),
                        'visitante': competitors[1].get('team', {}).get('displayName', 'Visitante'),
                        'liga': nombre_liga,
                        'fecha': event.get('date', '')
                    }
                    partidos.append(partido)
            
            self.cache[nombre_liga] = partidos
            return partidos
            
        except Exception as e:
            print(f"Error cargando {nombre_liga}: {e}")
            return []
    
    def obtener_estadisticas_equipo(self, equipo, liga):
        """Obtiene estadísticas de un equipo"""
        return {
            'nombre': equipo,
            'liga': liga,
            'form_goles': [1, 1, 2, 1, 1],
            'victorias': 2,
            'derrotas': 2,
            'empates': 1
        }
    
    def limpiar_cache(self):
        """Limpia el caché de partidos"""
        self.cache = {}
