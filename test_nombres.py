# test_nombres_alternativos.py
from modules.odds_api_integrator import OddsAPIIntegrator

odds_api = OddsAPIIntegrator()

# Probar diferentes combinaciones de nombres
busquedas = [
    ("Real Sociedad", "Athletic Bilbao"),
    ("Real Sociedad", "Athletic Club"),
    ("Real Sociedad", "Bilbao"),
    ("Sociedad", "Athletic"),
    ("Real Sociedad San Sebastian", "Athletic Bilbao"),
]

print("?? PROBANDO DIFERENTES NOMBRES DE EQUIPOS")
print("=" * 50)

for local, visitante in busquedas:
    print(f"\n?? {local} vs {visitante}:")
    odds = odds_api.get_live_odds(local, visitante)
    if odds:
        print(f"   ? ENCONTRADO!")
        print(f"   Cuotas: {odds['cuota_local']} | {odds['cuota_empate']} | {odds['cuota_visitante']}")
        break
    else:
        print("   ? No encontrado")
