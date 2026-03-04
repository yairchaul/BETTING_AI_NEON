# test_partido_hoy_real.py
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? BUSCANDO PARTIDO REAL DE HOY")
print("=" * 70)

odds_api = OddsAPIIntegrator()

# Probar con un partido que S? existe hoy
partidos_hoy = [
    ("Rayo Vallecano", "Oviedo"),
    ("Panathinaikos", "OFI Crete"),
    ("1. FC Saarbr?cken", "Wehen Wiesbaden"),
    ("Alemannia Aachen", "Schweinfurt"),
]

for local, visitante in partidos_hoy:
    print(f"\n?? Buscando: {local} vs {visitante}")
    odds = odds_api.get_live_odds(local, visitante)
    
    if odds:
        print(f"   ? ENCONTRADO!")
        print(f"   ?? Local: {odds['cuota_local']}")
        print(f"   ?? Empate: {odds['cuota_empate']}")
        print(f"   ?? Visitante: {odds['cuota_visitante']}")
        print(f"   ?? Liga: {odds.get('liga', 'N/A')}")
    else:
        print(f"   ? No encontrado")
