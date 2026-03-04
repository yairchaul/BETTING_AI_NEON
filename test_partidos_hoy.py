# test_partidos_hoy.py
from modules.odds_api_integrator import OddsAPIIntegrator
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("?? BUSCANDO TODOS LOS PARTIDOS DISPONIBLES HOY")
print("=" * 70)

API_KEY = "98ccdb7d4c28042caa8bc8fe7ff6cc62"
BASE_URL = "https://api.odds-api.io/v3"

try:
    # Obtener eventos de f?tbol
    url = f"{BASE_URL}/events"
    params = {
        "apiKey": API_KEY,
        "sport": "football",
        "status": "pending,live"
    }
    
    print("?? Consultando eventos de f?tbol...")
    response = requests.get(url, params=params, verify=False, timeout=10)
    
    if response.status_code == 200:
        eventos = response.json()
        print(f"? Total eventos encontrados: {len(eventos)}")
        
        if eventos:
            print("\n?? PARTIDOS DISPONIBLES HOY:")
            print("-" * 70)
            
            # Agrupar por liga
            ligas = {}
            for evento in eventos:
                liga = evento.get('league', {}).get('name', 'Sin liga')
                if liga not in ligas:
                    ligas[liga] = []
                ligas[liga].append(evento)
            
            # Mostrar por liga
            for liga, partidos in ligas.items():
                print(f"\n?? {liga.upper()}: {len(partidos)} partidos")
                print("-" * 50)
                
                for i, partido in enumerate(partidos[:5]):  # Mostrar primeros 5 de cada liga
                    home = partido.get('home', 'N/A')
                    away = partido.get('away', 'N/A')
                    fecha = partido.get('date', 'N/A')
                    print(f"   {i+1}. {home} vs {away}")
                    print(f"      ?? {fecha}")
                    
                    # Intentar obtener odds
                    odds_url = f"{BASE_URL}/odds"
                    odds_params = {
                        "apiKey": API_KEY,
                        "eventId": partido.get('id')
                    }
                    odds_response = requests.get(odds_url, params=odds_params, verify=False, timeout=5)
                    if odds_response.status_code == 200:
                        print(f"      ? Odds disponibles")
                    else:
                        print(f"      ? Sin odds a?n")
        else:
            print("? No hay eventos programados hoy")
    else:
        print(f"? Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"? Error: {e}")

print("\n" + "=" * 70)
