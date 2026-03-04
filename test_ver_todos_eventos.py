# test_ver_todos_eventos.py
from modules.odds_api_integrator import OddsAPIIntegrator
import json

print("?? VER TODOS LOS EVENTOS DISPONIBLES HOY")
print("=" * 70)

odds_api = OddsAPIIntegrator()

# Probar conexi?n
success, msg = odds_api.test_connection()
print(msg)

if success:
    print("\n?? Obteniendo todos los eventos de f?tbol...")
    
    # Obtener eventos sin filtrar
    eventos = odds_api.get_upcoming_events()
    
    print(f"? Total eventos encontrados: {len(eventos)}")
    
    if eventos:
        print("\n?? LISTA COMPLETA DE EVENTOS:")
        print("-" * 70)
        
        for i, evento in enumerate(eventos, 1):
            home = evento.get('home_team', 'N/A')
            away = evento.get('away_team', 'N/A')
            commence = evento.get('commence_time', 'N/A')
            
            # Obtener odds si existen
            bookmakers = evento.get('bookmakers', [])
            odds_info = []
            for bookmaker in bookmakers[:2]:  # Mostrar primeros 2 bookmakers
                title = bookmaker.get('title', 'Unknown')
                markets = bookmaker.get('markets', [])
                for market in markets:
                    if market.get('key') == 'h2h':
                        outcomes = market.get('outcomes', [])
                        odds_str = ' | '.join([f"{o.get('name')}: {o.get('price')}" for o in outcomes])
                        odds_info.append(f"{title}: {odds_str}")
            
            print(f"\n{i}. {home} vs {away}")
            print(f"   ?? {commence}")
            if odds_info:
                for info in odds_info[:2]:  # Mostrar solo 2 l?neas de odds
                    print(f"   ?? {info}")
            else:
                print(f"   ? Sin odds disponibles")
    else:
        print("? No se encontraron eventos")
        
        # Verificar si podemos obtener deportes
        print("\n?? Verificando deportes disponibles...")
        sports = odds_api.get_sports()
        print(f"? Deportes disponibles: {len(sports)}")
        for sport in sports[:5]:
            print(f"   - {sport.get('title')} ({sport.get('key')})")
else:
    print("? No se pudo conectar a la API")

print("\n" + "=" * 70)
