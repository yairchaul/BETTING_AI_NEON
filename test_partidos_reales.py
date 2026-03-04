# test_partidos_reales.py
from modules.odds_api_integrator import OddsAPIIntegrator
import datetime

print("?? BUSCANDO PARTIDOS CON ODDS REALES")
print("=" * 50)

odds_api = OddsAPIIntegrator()

# Probar conexi?n
success, msg = odds_api.test_connection()
print(msg)

if success:
    print("\n?? Buscando partidos de hoy...")
    
    # Probar con diferentes ligas y equipos
    busquedas = [
        ("Barcelona", "Real Madrid"),
        ("Liverpool", "Manchester City"),
        ("Bayern", "Dortmund"),
        ("PSG", "Marseille"),
        ("Juventus", "Milan"),
        ("America", "Chivas"),
        ("Cruz Azul", "Pumas"),
        ("Tigres", "Monterrey")
    ]
    
    encontrados = 0
    for local, visitante in busquedas:
        print(f"\n?? {local} vs {visitante}:")
        odds = odds_api.get_live_odds(local, visitante)
        
        if odds:
            encontrados += 1
            print(f"   ? ENCONTRADO!")
            print(f"   ?? Liga: {odds.get('liga', 'N/A')}")
            print(f"   ?? Fecha: {odds.get('fecha', 'N/A')}")
            print(f"   ?? Cuotas: {odds['cuota_local']} | {odds['cuota_empate']} | {odds['cuota_visitante']}")
            print(f"   ?? Implied Prob: {round(1/odds['cuota_local']*100,1)}% | {round(1/odds['cuota_empate']*100,1)}% | {round(1/odds['cuota_visitante']*100,1)}%")
        else:
            print("   ? Sin odds ahora")
    
    print(f"\n?? Total encontrados: {encontrados} de {len(busquedas)}")
