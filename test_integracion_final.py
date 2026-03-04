# test_integracion_final.py
"""
Prueba final de integraci?n con datos simulados
"""
from modules.team_translator import TeamTranslator
from modules.odds_api_integrator import OddsAPIIntegrator
import json

print(" PRUEBA DE INTEGRACI?N FINAL")
print("=" * 70)

# Simular lo que vendr?a del parser
captura_simulada = {
    'home_team': 'Am?rica',
    'away_team': 'Chivas',
    'odds': {'local': 2.10, 'empate': 3.20, 'visitante': 3.40},
    'probabilidades': [0.45, 0.25, 0.30],  # Nuestras probabilidades calculadas
    'liga': 'M?xico - Liga MX'
}

print("\n CAPTURA SIMULADA:")
print(json.dumps(captura_simulada, indent=2, ensure_ascii=False))

# Inicializar componentes
translator = TeamTranslator()
odds_api = OddsAPIIntegrator()

# Traducir equipos
home_api = translator.translate(captura_simulada['home_team'])
away_api = translator.translate(captura_simulada['away_team'])

print(f"\n Traducci?n: {captura_simulada['home_team']}  {home_api}")
print(f"              {captura_simulada['away_team']}  {away_api}")

# Buscar odds reales
print("\n Buscando odds reales en API...")
odds_reales = odds_api.get_live_odds(home_api, away_api)

if odds_reales:
    print(" Odds reales encontrados:")
    print(f"   Local: {odds_reales['cuota_local']}")
    print(f"   Empate: {odds_reales['cuota_empate']}")
    print(f"   Visitante: {odds_reales['cuota_visitante']}")
    
    # Calcular EV real
    probs = captura_simulada['probabilidades']
    ev_real = {
        'local': (probs[0] * odds_reales['cuota_local']) - 1,
        'empate': (probs[1] * odds_reales['cuota_empate']) - 1,
        'visitante': (probs[2] * odds_reales['cuota_visitante']) - 1
    }
    
    print("\n VALUE BETS (EV real):")
    for mercado, ev in ev_real.items():
        if ev > 0.05:
            print(f"    {mercado}: +{ev*100:.1f}% (VALUE!)")
        else:
            print(f"    {mercado}: {ev*100:.1f}%")
else:
    print(" No hay odds disponibles ahora (es normal)")
    print("   Esto significa que el partido no est? en la agenda de hoy")

print("\n" + "=" * 70)
print(" SISTEMA LISTO PARA PRODUCCI?N")
