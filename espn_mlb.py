# -*- coding: utf-8 -*-
"""
ESPN MLB - Scraper corregido con la estructura real de ESPN MLB
Basado en inspección de https://www.espn.com.mx/beisbol/mlb/resultados/_/fecha/20260326
"""

import requests
from datetime import datetime

class ESPN_MLB_Mejorado:
    def __init__(self):
        self.api_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    
    def get_games(self):
        """Obtiene partidos MLB con odds reales"""
        hoy = datetime.now().strftime("%Y%m%d")
        params = {"dates": hoy}
        
        try:
            r = requests.get(self.api_url, params=params, timeout=12)
            data = r.json()
            
            partidos = []
            for event in data.get("events", []):
                comp = event.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue
                
                # Identificar local y visitante
                local_team = None
                visit_team = None
                for c in competitors:
                    if c.get("homeAway") == "home":
                        local_team = c.get("team", {}).get("displayName", "")
                    else:
                        visit_team = c.get("team", {}).get("displayName", "")
                
                # Si no se identificó por homeAway, usar orden
                if not local_team:
                    local_team = competitors[0].get("team", {}).get("displayName", "")
                    visit_team = competitors[1].get("team", {}).get("displayName", "")
                
                # Odds reales (DraftKings)
                odds_data = comp.get("odds", [{}])[0] if comp.get("odds") else {}
                
                ou = odds_data.get("total", {}).get("overUnder", 8.5)
                ml_local = odds_data.get("moneyline", {}).get("home", {}).get("close", {}).get("odds", "N/A")
                ml_visit = odds_data.get("moneyline", {}).get("away", {}).get("close", {}).get("odds", "N/A")
                rl_local = odds_data.get("pointSpread", {}).get("home", {}).get("close", {}).get("line", "N/A")
                
                partido = {
                    'local': local_team,
                    'visitante': visit_team,
                    'fecha': hoy,
                    'hora': event.get("date", "")[-5:],
                    'odds': {
                        'over_under': float(ou) if isinstance(ou, (int, float)) else 8.5,
                        'moneyline': {'local': ml_local, 'visitante': ml_visit},
                        'runline': {'local': rl_local, 'visitante': str(rl_local).replace("+", "") if rl_local != "N/A" else "N/A"}
                    },
                    'records': {
                        'local': '0-0',
                        'visitante': '0-0'
                    }
                }
                partidos.append(partido)
            
            print(f"⚾ MLB: {len(partidos)} partidos con odds")
            return partidos
            
        except Exception as e:
            print(f"Error API MLB: {e}")
            return []
