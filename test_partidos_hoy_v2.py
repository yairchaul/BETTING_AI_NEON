# test_partidos_hoy_v2.py
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("?? BUSCANDO PARTIDOS CON LA ESTRUCTURA CORRECTA")
print("=" * 70)

API_KEY = "98ccdb7d4c28042caa8bc8fe7ff6cc62"

# Seg?n la documentaci?n de The Odds API, la URL correcta es:
# https://api.the-odds-api.com/v4/sports/{sport}/odds
# https://api.the-odds-api.com/v4/sports/{sport}/scores

BASE_URL = "https://api.the-odds-api.com/v4"

try:
    # Primero, obtener lista de deportes disponibles
    sports_url = f"{BASE_URL}/sports"
    sports_params = {
        "apiKey": API_KEY
    }
    
    print("?? Consultando deportes disponibles...")
    sports_response = requests.get(sports_url, params=sports_params, timeout=10)
    
    if sports_response.status_code == 200:
        sports = sports_response.json()
        print(f"? Deportes disponibles: {len(sports)}")
        
        # Buscar el deporte de f?tbol (soccer)
        soccer_key = None
        for sport in sports:
            if 'soccer' in sport.get('key', '').lower():
                soccer_key = sport.get('key')
                print(f"? Deporte encontrado: {sport.get('title')} ({sport.get('key')})")
                break
        
        if soccer_key:
            # Obtener odds para partidos de f?tbol
            odds_url = f"{BASE_URL}/sports/{soccer_key}/odds"
            odds_params = {
                "apiKey": API_KEY,
                "regions": "uk",  # uk, us, eu, au
                "markets": "h2h",  # head to head
                "oddsFormat": "decimal"
            }
            
            print(f"\n?? Buscando partidos con odds...")
            odds_response = requests.get(odds_url, params=odds_params, timeout=10)
            
            if odds_response.status_code == 200:
                partidos = odds_response.json()
                print(f"? Partidos encontrados: {len(partidos)}")
                
                if partidos:
                    print("\n?? PARTIDOS CON ODDS DISPONIBLES:")
                    print("-" * 70)
                    
                    for i, partido in enumerate(partidos[:10]):  # Mostrar primeros 10
                        home = partido.get('home_team', 'N/A')
                        away = partido.get('away_team', 'N/A')
                        commence_time = partido.get('commence_time', 'N/A')
                        bookmakers = partido.get('bookmakers', [])
                        
                        print(f"\n{i+1}. {home} vs {away}")
                        print(f"   ?? {commence_time}")
                        
                        # Mostrar odds de los primeros bookmakers
                        for bookmaker in bookmakers[:2]:
                            title = bookmaker.get('title', 'Unknown')
                            markets = bookmaker.get('markets', [])
                            for market in markets:
                                if market.get('key') == 'h2h':
                                    outcomes = market.get('outcomes', [])
                                    odds_str = []
                                    for outcome in outcomes:
                                        odds_str.append(f"{outcome.get('name')}: {outcome.get('price')}")
                                    print(f"   ?? {title}: {', '.join(odds_str)}")
                else:
                    print("? No hay partidos con odds disponibles ahora")
            else:
                print(f"? Error al obtener odds: {odds_response.status_code}")
                print(f"   Respuesta: {odds_response.text}")
    else:
        print(f"? Error al obtener deportes: {sports_response.status_code}")
        print(f"   Respuesta: {sports_response.text}")
        
except Exception as e:
    print(f"? Error de conexi?n: {e}")

print("\n" + "=" * 70)
