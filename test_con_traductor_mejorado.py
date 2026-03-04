# test_con_traductor_mejorado.py
from modules.odds_api_integrator import OddsAPIIntegrator
from modules.team_translator import TeamTranslator

print("?? PROBANDO TRADUCTOR MEJORADO")
print("=" * 70)

odds_api = OddsAPIIntegrator()
translator = TeamTranslator()

# Probar con nombres que podr?an aparecer en capturas
test_cases = [
    ("Saarbr?cken", "Wehen Wiesbaden"),
    ("Hamburgo", "Rostock"),
    ("PAOK Sal?nica", "Kifisia"),
    ("Rayo Vallecano", "Oviedo"),
    ("Catanzaro", "Carrarese"),
    ("Mannheim", "Essen"),
    ("Brighton", "Arsenal"),
    ("Young Boys", "Luzern"),
]

for local, visitante in test_cases:
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
        print(f"   ? No encontrado en la API (puede no haber odds hoy)")
