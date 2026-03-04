# test_ligas_hoy.py
from modules.odds_api_integrator import OddsAPIIntegrator

print("?? VERIFICANDO LIGAS DISPONIBLES HOY")
print("=" * 70)

odds_api = OddsAPIIntegrator()

# Obtener todos los eventos
eventos = odds_api.get_upcoming_events()

if eventos:
    # Crear un diccionario de ligas/pa?ses
    ligas = {}
    
    for evento in eventos:
        home = evento.get('home_team', '')
        away = evento.get('away_team', '')
        
        # Intentar identificar el pa?s por los equipos
        pais = "Desconocido"
        if any(team in ["Panathinaikos", "OFI Crete", "PAOK"] for team in [home, away]):
            pais = "???? Grecia"
        elif any(team in ["Saarbr?cken", "Wehen", "Aachen", "Ingolstadt", "Duisburg", "Havelse", "Rostock", "Essen", "Mannheim"] for team in [home, away]):
            pais = "???? Alemania"
        elif any(team in ["Rayo Vallecano", "Oviedo"] for team in [home, away]):
            pais = "???? Espa?a"
        elif any(team in ["Carrarese", "Catanzaro"] for team in [home, away]):
            pais = "???? Italia"
        
        if pais not in ligas:
            ligas[pais] = []
        ligas[pais].append(f"{home} vs {away}")
    
    # Mostrar resultados
    print(f"\n?? LIGAS CON PARTIDOS HOY ({len(eventos)} partidos total):")
    print("-" * 70)
    
    for pais, partidos in ligas.items():
        print(f"\n{pais}: {len(partidos)} partidos")
        for partido in partidos[:3]:  # Mostrar primeros 3
            print(f"   ? {partido}")
        if len(partidos) > 3:
            print(f"   ... y {len(partidos)-3} m?s")
else:
    print("? No hay eventos hoy")

print("\n" + "=" * 70)
