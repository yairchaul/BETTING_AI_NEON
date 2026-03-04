# test_sistema_completo.py
"""
Prueba completa del sistema con traductor y odds API
"""
from modules.team_translator import TeamTranslator
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? PRUEBA DEL SISTEMA COMPLETO")
print("=" * 70)

# Inicializar componentes
translator = TeamTranslator()
odds_api = OddsAPIIntegrator()

# Probar conexi?n API
success, msg = odds_api.test_connection()
print(f"\n?? API: {msg}")

# Lista de equipos a probar (simulando capturas de pantalla)
test_cases = [
    ("Am?rica", "Chivas"),           # M?xico
    ("Boca", "River"),                # Argentina
    ("Flamengo", "Corinthians"),      # Brasil
    ("Colo Colo", "Universidad de Chile"),  # Chile
    ("Nacional", "Millonarios"),      # Colombia
    ("Universitario", "Alianza"),     # Per?
    ("Pe?arol", "Nacional"),          # Uruguay
    ("Olimpia", "Cerro Porte?o"),     # Paraguay
    ("Barcelona SC", "Emelec"),       # Ecuador
    ("Inter Miami", "LA Galaxy"),      # EE.UU.
]

print("\n?? PROBANDO TRADUCCIONES:")
print("-" * 70)

for local, visitante in test_cases:
    # Traducir nombres
    local_api = translator.translate(local)
    visitante_api = translator.translate(visitante)
    
    print(f"\n?? Original: {local:20} vs {visitante:20}")
    print(f"   Traducido: {local_api:25} vs {visitante_api:25}")
    
    # Buscar odds (si hay partidos hoy)
    odds = odds_api.get_live_odds(local_api, visitante_api)
    if odds:
        print(f"   ? Odds encontrados: {odds['cuota_local']} | {odds['cuota_empate']} | {odds['cuota_visitante']}")
    else:
        print(f"   ? No hay partidos hoy (es normal)")

print("\n" + "=" * 70)
print("? Sistema listo para integrar con pro_analyzer_ultimate.py")
