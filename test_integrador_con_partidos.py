# test_integrador_con_partidos.py
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? PROBANDO INTEGRADOR CON PARTIDOS REALES")
print("=" * 60)

odds_api = OddsAPIIntegrator()

# Probar con el primer partido de la lista
partidos = [
    ("Lanus", "Boca Juniors"),
    ("Lanus", "Deportivo Riestra"),
    ("Newells Old Boys", "Platense"),
    ("CA Tigre BA", "Velez Sarsfield BA"),
    ("Independiente", "Union Santa Fe"),
]

for local, visitante in partidos:
    print(f"\n?? Buscando: {local} vs {visitante}")
    odds = odds_api.get_live_odds(local, visitante)
    
    if odds:
        print(f"   ? ENCONTRADO!")
        print(f"   ?? Local: {odds.get('cuota_local', 'N/A')}")
        print(f"   ?? Empate: {odds.get('cuota_empate', 'N/A')}")
        print(f"   ?? Visitante: {odds.get('cuota_visitante', 'N/A')}")
    else:
        print(f"   ? No encontrado en la API")
        
        # Mostrar qu? eventos hay disponibles hoy
        print(f"   ?? Buscando eventos disponibles...")
        eventos = odds_api.get_events_today(country="Argentina")
        for evento in eventos[:3]:
            print(f"      - {evento.get('home')} vs {evento.get('away')}")
