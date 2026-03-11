"""
Verificador automático de resultados de partidos
Usa ESPN API gratuita para verificar resultados reales
"""
import requests
from datetime import datetime, timedelta

class ResultVerifier:
    """Verifica resultados de partidos automáticamente"""
    
    def __init__(self):
        self.espn_api = "https://site.api.espn.com/apis/site/v2/sports"
    
    def verificar_futbol(self, equipo_local, equipo_visitante, fecha=None):
        """Verifica resultado de partido de fútbol"""
        if fecha is None:
            fecha = datetime.now().strftime('%Y%m%d')
        
        try:
            url = f"{self.espn_api}/soccer/futbol/scoreboard"
            params = {'dates': fecha}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for event in data.get('events', []):
                    nombre = event.get('name', '')
                    if equipo_local in nombre and equipo_visitante in nombre:
                        return self._parsear_resultado_futbol(event)
        except:
            pass
        
        return None
    
    def verificar_nba(self, equipo_local, equipo_visitante, fecha=None):
        """Verifica resultado de partido NBA"""
        if fecha is None:
            fecha = datetime.now().strftime('%Y%m%d')
        
        try:
            url = f"{self.espn_api}/basketball/nba/scoreboard"
            params = {'dates': fecha}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for event in data.get('events', []):
                    nombre = event.get('name', '')
                    if equipo_local in nombre and equipo_visitante in nombre:
                        return self._parsear_resultado_nba(event)
        except:
            pass
        
        return None
    
    def _parsear_resultado_futbol(self, event):
        """Parsea resultado de fútbol de ESPN"""
        try:
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            competitors = competitions[0].get('competitors', [])
            if len(competitors) < 2:
                return None
            
            local = competitors[0]
            visitante = competitors[1]
            
            score_local = int(local.get('score', 0))
            score_visit = int(visitante.get('score', 0))
            
            if score_local > score_visit:
                ganador = local.get('team', {}).get('name', '')
                resultado = 'local'
            elif score_visit > score_local:
                ganador = visitante.get('team', {}).get('name', '')
                resultado = 'visitante'
            else:
                ganador = 'Empate'
                resultado = 'empate'
            
            return {
                'ganador': ganador,
                'resultado': resultado,
                'marcador': f"{score_local}-{score_visit}",
                'local': score_local,
                'visitante': score_visit,
                'total_goles': score_local + score_visit
            }
        except:
            return None
    
    def _parsear_resultado_nba(self, event):
        """Parsea resultado de NBA de ESPN"""
        try:
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            competitors = competitions[0].get('competitors', [])
            if len(competitors) < 2:
                return None
            
            local = competitors[0]
            visitante = competitors[1]
            
            score_local = int(local.get('score', 0))
            score_visit = int(visitante.get('score', 0))
            
            if score_local > score_visit:
                ganador = local.get('team', {}).get('displayName', '')
                resultado = 'local'
            else:
                ganador = visitante.get('team', {}).get('displayName', '')
                resultado = 'visitante'
            
            return {
                'ganador': ganador,
                'resultado': resultado,
                'marcador': f"{score_local}-{score_visit}",
                'local': score_local,
                'visitante': score_visit,
                'total_puntos': score_local + score_visit
            }
        except:
            return None
