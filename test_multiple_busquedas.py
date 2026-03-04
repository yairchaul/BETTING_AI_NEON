# test_multiple_busquedas.py
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? B?SQUEDA M?LTIPLE")
print("=" * 70)

odds_api = OddsAPIIntegrator()

# Diferentes deportes a probar
deportes = ["soccer", "football", "soccer_argentina"]

# Diferentes regiones
regiones = ["uk", "us", "eu", "au"]

for deporte in deportes:
    for region in regiones:
        print(f"\n?? Probando: deporte={deporte}, regi?n={region}")
        eventos = odds_api.get_upcoming_events(sport_key=deporte, regions=region)
        print(f"   ? Encontrados: {len(eventos)} eventos")
        
        if eventos:
            for evento in eventos[:3]:  # Mostrar primeros 3
                home = evento.get('home_team', 'N/A')
                away = evento.get('away_team', 'N/A')
                print(f"      - {home} vs {away}")
            break
    if eventos:
        break

print("\n" + "=" * 70)
