# test_con_traductor.py
from modules.odds_api_integrator import OddsAPIIntegrator
from modules.team_translator import TeamTranslator

print("?? PROBANDO CON TRADUCTOR DE EQUIPOS")
print("=" * 70)

odds_api = OddsAPIIntegrator()
translator = TeamTranslator()

# Probar con los partidos que queremos
partidos = [
    ("Lanus", "Boca Juniors"),
    ("Lanus", "Deportivo Riestra"),
    ("Newells Old Boys", "Platense"),
    ("CA Tigre BA", "Velez Sarsfield BA"),
    ("Independiente", "Union Santa Fe"),
]

print("\n?? PARTIDOS A BUSCAR:")
for local, visitante in partidos:
    local_api = translator.translate(local)
    visitante_api = translator.translate(visitante)
    print(f"\n?? Original: {local} vs {visitante}")
    print(f"   Traducido: {local_api} vs {visitante_api}")
    
    # Buscar en la API
    odds = odds_api.get_live_odds(local_api, visitante_api)
    
    if odds:
        print(f"   ? ENCONTRADO!")
        print(f"   ?? Local: {odds['cuota_local']}")
        print(f"   ?? Empate: {odds['cuota_empate']}")
        print(f"   ?? Visitante: {odds['cuota_visitante']}")
    else:
        print(f"   ? No encontrado en la API")

print("\n" + "=" * 70)
