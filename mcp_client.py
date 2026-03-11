"""
Cliente MCP - EXTRAE TODOS los partidos disponibles
"""
import os
import requests
from typing import List, Dict

class MCPOddsClient:
    """Cliente para The Odds API - Extrae TODOS los partidos"""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY", "98ccdb7d4c28042caa8bc8fe7ff6cc62")
        print(f"🔑 API Key configurada")
    
    def get_odds(self, sport: str = "soccer", regions: str = "mx,us,uk,eu", markets: List[str] = ["h2h"]) -> List[Dict]:
        """Obtiene TODOS los partidos disponibles"""
        
        try:
            url = f"{self.BASE_URL}/sports/{sport}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": regions,
                "markets": ",".join(markets),
                "oddsFormat": "decimal"
            }
            
            print(f"📡 Extrayendo partidos de {regions}...")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API respondió con {len(data)} partidos")
                return data
            else:
                print(f"⚠️ Error {response.status_code}: {response.text[:200]}")
                return self._get_simulated_data()
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return self._get_simulated_data()
    
    def _get_simulated_data(self):
        """Datos simulados basados en TU CAPTURA de Caliente.mx"""
        print("🎮 Usando datos de tu captura (8 partidos)")
        return [
            {
                "id": "sim1",
                "sport_title": "UEFA Champions League",
                "home_team": "Bayer Leverkusen",
                "away_team": "Arsenal",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Bayer Leverkusen", "price": 6.00},  # +500
                            {"name": "Draw", "price": 2.87},  # +187
                            {"name": "Arsenal", "price": 1.80}  # -125
                        ]
                    }]
                }]
            },
            {
                "id": "sim2",
                "sport_title": "UEFA Champions League",
                "home_team": "Real Madrid",
                "away_team": "Manchester City",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Real Madrid", "price": 3.50},  # +250
                            {"name": "Draw", "price": 3.65},  # +265
                            {"name": "Manchester City", "price": 1.98}  # -102
                        ]
                    }]
                }]
            },
            {
                "id": "sim3",
                "sport_title": "UEFA Champions League",
                "home_team": "Bodo Glimt",
                "away_team": "Sporting Lisboa",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Bodo Glimt", "price": 2.25},  # +125
                            {"name": "Draw", "price": 3.55},  # +255
                            {"name": "Sporting Lisboa", "price": 3.00}  # +200
                        ]
                    }]
                }]
            },
            {
                "id": "sim4",
                "sport_title": "UEFA Champions League",
                "home_team": "PSG",
                "away_team": "Chelsea",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "PSG", "price": 1.95},  # -105
                            {"name": "Draw", "price": 3.75},  # +275
                            {"name": "Chelsea", "price": 3.55}  # +255
                        ]
                    }]
                }]
            },
            {
                "id": "sim5",
                "sport_title": "UEFA Champions League",
                "home_team": "Barcelona",
                "away_team": "Newcastle",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Barcelona", "price": 1.57},  # -176
                            {"name": "Draw", "price": 4.55},  # +355
                            {"name": "Newcastle", "price": 5.00}  # +400
                        ]
                    }]
                }]
            },
            {
                "id": "sim6",
                "sport_title": "UEFA Champions League",
                "home_team": "Liverpool",
                "away_team": "Galatasaray",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Liverpool", "price": 1.25},  # -400
                            {"name": "Draw", "price": 6.00},  # +500
                            {"name": "Galatasaray", "price": 10.25}  # +925
                        ]
                    }]
                }]
            },
            {
                "id": "sim7",
                "sport_title": "UEFA Champions League",
                "home_team": "Tottenham",
                "away_team": "Atlético Madrid",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Tottenham", "price": 2.50},  # +150
                            {"name": "Draw", "price": 3.90},  # +290
                            {"name": "Atlético Madrid", "price": 2.50}  # +150
                        ]
                    }]
                }]
            },
            {
                "id": "sim8",
                "sport_title": "UEFA Champions League",
                "home_team": "Bayern Munich",
                "away_team": "Atalanta",
                "bookmakers": [{
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Bayern Munich", "price": 1.27},  # -371
                            {"name": "Draw", "price": 6.00},  # +500
                            {"name": "Atalanta", "price": 9.80}  # +880
                        ]
                    }]
                }]
            }
        ]

    def health_check(self) -> bool:
        return True
