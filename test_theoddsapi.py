# test_theoddsapi.py
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "98ccdb7d4c28042caa8bc8fe7ff6cc62"

print("?? PROBANDO THEODDSAPI")
print("=" * 60)

# TheOddsAPI usa v4
url = "https://api.theoddsapi.com/v4/sports"
params = {
    "apiKey": API_KEY,
    "regions": "uk",  # uk, us, eu, au
    "markets": "h2h"  # head to head (1X2)
}

print(f"?? Consultando: {url}")
print(f"?? Par?metros: {params}")

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"?? Status Code: {response.status_code}")
    
    if response.status_code == 200:
        sports = response.json()
        print(f"? Conexi?n exitosa! Deportes disponibles: {len(sports)}")
        for sport in sports[:5]:
            print(f"   - {sport.get('title')} ({sport.get('key')})")
            
        # Buscar partidos de f?tbol
        print("\n?? Buscando partidos de f?tbol...")
        football_url = "https://api.theoddsapi.com/v4/sports/soccer/odds"
        football_params = {
            "apiKey": API_KEY,
            "regions": "uk",
            "markets": "h2h",
            "oddsFormat": "american"
        }
        football_response = requests.get(football_url, params=football_params, timeout=10)
        
        if football_response.status_code == 200:
            matches = football_response.json()
            print(f"? Encontrados {len(matches)} partidos")
            for match in matches[:5]:
                print(f"\n   ?? {match.get('home_team')} vs {match.get('away_team')}")
                print(f"   ?? {match.get('commence_time')}")
        else:
            print(f"? Error en f?tbol: {football_response.status_code}")
            
    else:
        print(f"? Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"? Error de conexi?n: {e}")

print("=" * 60)
