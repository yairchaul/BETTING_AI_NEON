# test_partido_real.py
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? BUSCANDO PARTIDO REAL: Real Sociedad vs Athletic Bilbao")
print("=" * 60)

odds_api = OddsAPIIntegrator()

# Probar conexi?n
success, msg = odds_api.test_connection()
print(msg)

if success:
    print("\n?? Buscando odds en vivo...")
    
    # Buscar el partido
    odds = odds_api.get_live_odds("Real Sociedad", "Athletic Bilbao")
    
    if odds:
        print("\n? PARTIDO ENCONTRADO!")
        print(f"?? Liga: {odds.get('liga', 'N/A')}")
        print(f"?? Fecha: {odds.get('fecha', 'N/A')}")
        print(f"?? Local: Real Sociedad @ {odds['cuota_local']}")
        print(f"?? Empate: @ {odds['cuota_empate']}")
        print(f"?? Visitante: Athletic @ {odds['cuota_visitante']}")
        print(f"?? Implied Prob: {round(1/odds['cuota_local']*100,1)}% | {round(1/odds['cuota_empate']*100,1)}% | {round(1/odds['cuota_visitante']*100,1)}%")
        
        # Comparar con tus odds
        print("\n?? COMPARACI?N CON TUS ODDS:")
        print(f"Tus odds: +140 ({round(100/140+1,2)}), +230 ({round(100/230+1,2)}), +194 ({round(100/194+1,2)})")
        print(f"Reales:   {odds['cuota_local']} | {odds['cuota_empate']} | {odds['cuota_visitante']}")
        
        # Calcular value bets potenciales
        print("\n?? VALUE BETS POTENCIALES:")
        tus_probs = [1/(100/140+1), 1/(100/230+1), 1/(100/194+1)]
        mercados = ['Local', 'Empate', 'Visitante']
        odds_reales = [odds['cuota_local'], odds['cuota_empate'], odds['cuota_visitante']]
        
        for i, mercado in enumerate(mercados):
            ev = (tus_probs[i] * odds_reales[i]) - 1
            if ev > 0:
                print(f"? {mercado}: EV = {round(ev*100,1)}% positivo!")
            else:
                print(f"? {mercado}: EV = {round(ev*100,1)}%")
    else:
        print("\n? No se encontr? el partido en la API")
        print("Posibles razones:")
        print("- El partido no est? en la cobertura de la API")
        print("- Los nombres de equipos no coinciden exactamente")
        print("- La API requiere nombres en ingl?s: 'Real Sociedad' vs 'Athletic Bilbao'")
