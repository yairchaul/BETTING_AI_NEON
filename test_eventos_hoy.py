# test_eventos_hoy.py - VERSI?N CORREGIDA
from modules.odds_api_integrator import OddsAPIIntegrator
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("?? BUSCANDO EVENTOS DE HOY EN ESPA?A")
print("=" * 60)

# Usar la URL correcta y par?metro de autenticaci?n correcto
API_KEY = "98ccdb7d4c28042caa8bc8fe7ff6cc62"
BASE_URL = "https://api.odds-api.io/v3"

try:
    # Buscar eventos de f?tbol en Espa?a
    url = f"{BASE_URL}/events"
    params = {
        "api_token": API_KEY,  # CAMBIO CLAVE: api_token en lugar de apiKey
        "sport": "football",
        "country": "ES",  # C?digo de pa?s ISO para Espa?a
        "status": "pending,live"
    }
    
    print(f"?? Consultando: {url}")
    print(f"?? Par?metros: {params}")
    response = requests.get(url, params=params, verify=False)
    
    print(f"?? Status Code: {response.status_code}")
    
    if response.status_code == 200:
        eventos = response.json()
        print(f"? Encontrados {len(eventos)} eventos")
        
        if eventos:
            print("\n?? EVENTOS DISPONIBLES:")
            print("-" * 60)
            for i, evento in enumerate(eventos[:10]):
                home = evento.get('home', 'N/A')
                away = evento.get('away', 'N/A')
                league = evento.get('league', {}).get('name', 'N/A')
                date = evento.get('date', 'N/A')
                event_id = evento.get('id', 'N/A')
                
                print(f"{i+1}. {home} vs {away}")
                print(f"   ?? Liga: {league}")
                print(f"   ?? Fecha: {date}")
                print(f"   ?? ID: {event_id}")
                
                # Intentar obtener odds para este evento
                print(f"   ?? Buscando odds...")
                odds_url = f"{BASE_URL}/odds"
                odds_params = {
                    "api_token": API_KEY,
                    "eventId": event_id,
                    "bookmakers": "Bet365"
                }
                odds_response = requests.get(odds_url, params=odds_params, verify=False)
                if odds_response.status_code == 200:
                    odds_data = odds_response.json()
                    print(f"   ? Odds encontrados")
                else:
                    print(f"   ? Sin odds disponibles")
                print()
        else:
            print("? No hay eventos programados hoy en Espa?a")
            
            # Verificar deportes disponibles
            print("\n?? Verificando deportes disponibles...")
            sports_url = f"{BASE_URL}/sports"
            sports_response = requests.get(sports_url, params={"api_token": API_KEY}, verify=False)
            if sports_response.status_code == 200:
                sports = sports_response.json()
                print(f"? Deportes disponibles: {len(sports)}")
                for sport in sports[:5]:
                    print(f"   - {sport.get('name')} ({sport.get('slug')})")
    else:
        print(f"? Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"? Error: {e}")

print("=" * 60)
