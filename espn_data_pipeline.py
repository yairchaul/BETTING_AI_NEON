"""
ESPN DATA PIPELINE - Extracción COMPLETA de cuotas (CORREGIDO)
"""
import requests
import json
import streamlit as st
from datetime import datetime

class ESPNDataPipeline:
    def __init__(self):
        self.base_url = "https://site.web.api.espn.com/apis/site/v2/sports"
        self.ligas_codigos = {
            "México - Liga MX": "mex.1",
            "UEFA - Champions League": "uefa.champions",
            "La Liga": "esp.1",
            "Inglaterra - Premier League": "eng.1",
            "Bundesliga 1": "ger.1",
            "Serie A": "ita.1",
            "Ligue 1": "fra.1",
            "Holanda - Eredivisie": "ned.1",
            "Portugal - Primeira Liga": "por.1",
            "México - Liga de Expansión MX": "mex.2"
        }
    
    def get_nba_games_with_odds(self):
        """Obtiene partidos NBA con TODAS las cuotas"""
        try:
            fecha = datetime.now().strftime("%Y%m%d")
            url = f"{self.base_url}/basketball/nba/scoreboard?dates={fecha}&limit=100"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                partidos = []
                
                for event in data.get('events', []):
                    competition = event['competitions'][0]
                    competitors = competition['competitors']
                    
                    if len(competitors) >= 2:
                        home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                        away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                        
                        # ============================================
                        # EXTRACCIÓN CORREGIDA DE ODDS
                        # ============================================
                        odds_data = {
                            'moneyline': {'local': 'N/A', 'visitante': 'N/A'},
                            'spread': {'valor': 0, 'local_odds': 'N/A', 'visitante_odds': 'N/A'},
                            'totales': {'linea': 0, 'over_odds': 'N/A', 'under_odds': 'N/A'}
                        }
                        
                        if 'odds' in competition and competition['odds']:
                            odds = competition['odds'][0]
                            
                            # 1. MONEYLINE - Acceder a la estructura anidada correcta
                            if 'moneyline' in odds:
                                ml_data = odds['moneyline']
                                if 'home' in ml_data and 'close' in ml_data['home'] and 'odds' in ml_data['home']['close']:
                                    odds_data['moneyline']['local'] = ml_data['home']['close']['odds']
                                if 'away' in ml_data and 'close' in ml_data['away'] and 'odds' in ml_data['away']['close']:
                                    odds_data['moneyline']['visitante'] = ml_data['away']['close']['odds']
                            
                            # 2. SPREAD - Extraer el valor
                            if 'pointSpread' in odds:
                                spread_data = odds['pointSpread']
                                if 'away' in spread_data and 'close' in spread_data['away'] and 'line' in spread_data['away']['close']:
                                    line_str = spread_data['away']['close']['line']
                                    try:
                                        odds_data['spread']['valor'] = float(line_str)
                                    except:
                                        odds_data['spread']['valor'] = 0
                                
                                # Odds del spread
                                if 'away' in spread_data and 'close' in spread_data['away'] and 'odds' in spread_data['away']['close']:
                                    odds_data['spread']['visitante_odds'] = spread_data['away']['close']['odds']
                                if 'home' in spread_data and 'close' in spread_data['home'] and 'odds' in spread_data['home']['close']:
                                    odds_data['spread']['local_odds'] = spread_data['home']['close']['odds']
                            
                            # 3. TOTALES
                            if 'total' in odds:
                                total_data = odds['total']
                                if 'over' in total_data and 'close' in total_data['over'] and 'line' in total_data['over']['close']:
                                    line_str = total_data['over']['close']['line']
                                    try:
                                        # Remover 'o' o 'u' del inicio
                                        odds_data['totales']['linea'] = float(line_str[1:]) if line_str.startswith(('o', 'u')) else 0
                                    except:
                                        odds_data['totales']['linea'] = 0
                                
                                if 'over' in total_data and 'close' in total_data['over'] and 'odds' in total_data['over']['close']:
                                    odds_data['totales']['over_odds'] = total_data['over']['close']['odds']
                                if 'under' in total_data and 'close' in total_data['under'] and 'odds' in total_data['under']['close']:
                                    odds_data['totales']['under_odds'] = total_data['under']['close']['odds']
                        
                        partidos.append({
                            'id': event.get('id'),
                            'local': home['team']['displayName'],
                            'visitante': away['team']['displayName'],
                            'fecha': event.get('date', '')[:10],
                            'hora': competition.get('date', '')[-8:] if competition.get('date') else '',
                            'estado': competition.get('status', {}).get('type', 'scheduled'),
                            'records': {
                                'local': home.get('records', [{}])[0].get('summary', '0-0') if home.get('records') else '0-0',
                                'visitante': away.get('records', [{}])[0].get('summary', '0-0') if away.get('records') else '0-0'
                            },
                            'odds': odds_data
                        })
                return partidos
        except Exception as e:
            st.error(f"Error obteniendo NBA: {e}")
            return []

    def get_soccer_games_today(self, liga_nombre):
        """Obtiene partidos de fútbol para una liga"""
        codigo = self.ligas_codigos.get(liga_nombre)
        if not codigo:
            return []
        
        try:
            url = f"{self.base_url}/soccer/{codigo}/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                partidos = []
                
                for event in data.get('events', []):
                    competition = event['competitions'][0]
                    competitors = competition['competitors']
                    
                    if len(competitors) >= 2:
                        home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                        away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                        
                        partidos.append({
                            'id': event.get('id'),
                            'liga': liga_nombre,
                            'local': home['team']['displayName'],
                            'visitante': away['team']['displayName'],
                            'fecha': event.get('date', '')[:10]
                        })
                return partidos
        except:
            return []

    def get_ufc_events(self):
        """Obtiene eventos UFC"""
        try:
            url = f"{self.base_url}/mma/ufc/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                combates = []
                
                for event in data.get('events', []):
                    event_name = event.get('name', 'UFC Event')
                    event_date = event.get('date', '')[:10]
                    
                    for competition in event.get('competitions', []):
                        competitors = competition.get('competitors', [])
                        
                        if len(competitors) >= 2:
                            p1 = competitors[0]
                            p2 = competitors[1]
                            
                            combates.append({
                                'id': event.get('id'),
                                'evento': event_name,
                                'fecha': event_date,
                                'peleador1': {
                                    'nombre': p1['athlete']['displayName'],
                                    'record': p1.get('record', '0-0-0')
                                },
                                'peleador2': {
                                    'nombre': p2['athlete']['displayName'],
                                    'record': p2.get('record', '0-0-0')
                                }
                            })
                return combates
        except:
            return []
