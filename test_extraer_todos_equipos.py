# test_extraer_todos_equipos.py
from modules.odds_api_integrator import OddsAPIIntegrator
import json
from collections import Counter

print("?? EXTRACCI?N COMPLETA DE EQUIPOS DE LA API")
print("=" * 80)

odds_api = OddsAPIIntegrator()

# Probar conexi?n
success, msg = odds_api.test_connection()
print(msg)

if success:
    print("\n?? Obteniendo todos los eventos disponibles...")
    
    # Obtener eventos de diferentes regiones para maximizar cobertura
    todas_regiones = ["uk", "us", "eu", "au"]
    todos_los_equipos = set()
    equipos_por_liga = {}
    eventos_por_pais = {}
    
    for region in todas_regiones:
        print(f"\n?? Probando regi?n: {region}")
        eventos = odds_api.get_upcoming_events(regions=region)
        print(f"   ? Encontrados {len(eventos)} eventos")
        
        for evento in eventos:
            home = evento.get('home_team', '')
            away = evento.get('away_team', '')
            
            if home and away:
                todos_los_equipos.add(home)
                todos_los_equipos.add(away)
                
                # Intentar identificar el pa?s
                pais = "Desconocido"
                if any(p in home or p in away for p in ["Panathinaikos", "OFI", "PAOK", "AEK", "Olympiacos"]):
                    pais = "Grecia"
                elif any(p in home or p in away for p in ["Bayern", "Dortmund", "Leipzig", "Leverkusen", "Schalke", "Stuttgart", "Hamburg", "Hannover", "N?rnberg", "D?sseldorf", "Bochum", "Mainz", "Augsburg", "Hoffenheim", "Freiburg", "M?nchengladbach", "Wolfsburg", "Bremen", "K?ln", "Paderborn", "Darmstadt", "Heidenheim", "Kiel", "Saarbr?cken", "Aachen", "Ingolstadt", "Duisburg", "Havelse", "Rostock", "Essen", "Mannheim", "Wehen", "Wiesbaden", "Schweinfurt", "Ulm", "Verl", "Munster", "Sandhausen", "Zwickau", "Meppen", "Oldenburg", "Lotte", "Kickers", "Stuttgart II", "Bayern II", "Dortmund II"]):
                    pais = "Alemania"
                elif any(p in home or p in away for p in ["Barcelona", "Madrid", "Atletico", "Valencia", "Sevilla", "Betis", "Sociedad", "Athletic", "Villarreal", "Celta", "Vigo", "Girona", "Mallorca", "Las Palmas", "Alaves", "Getafe", "Osasuna", "Rayo", "Vallecano", "Oviedo", "Sporting", "Zaragoza", "Leganes", "Eibar", "Elche", "Tenerife", "Albacete", "Cartagena", "Burgos", "Huesca", "Mirandes", "Amorebieta", "Racing", "Santander", "Ferrol", "Alcorcon", "Cornella", "Ibiza", "Linares", "Melilla", "Ceuta", "Recreativo", "Cordoba", "Algeciras", "Linares", "Badajoz", "Cacereno", "Talavera"]):
                    pais = "Espa?a"
                elif any(p in home or p in away for p in ["Juventus", "Milan", "Inter", "Roma", "Lazio", "Napoli", "Atalanta", "Fiorentina", "Torino", "Bologna", "Udinese", "Sampdoria", "Genoa", "Cagliari", "Lecce", "Salernitana", "Spezia", "Cremonese", "Monza", "Empoli", "Sassuolo", "Verona", "Venezia", "Parma", "Palermo", "Bari", "Catanzaro", "Carrarese", "Pisa", "Como", "Modena", "Reggiana", "Cittadella", "Sudtirol", "Ascoli", "Ternana", "Frosinone", "Pordenone", "Vicenza", "Padova", "Triestina", "Rimini", "Ancona", "Cesena", "Perugia", "Arezzo", "Gubbio", "Pescara", "Virtus", "Entella", "Olbia", "Potenza", "Foggia", "Catania", "Messina", "Crotone"]):
                    pais = "Italia"
                elif any(p in home or p in away for p in ["Liverpool", "Manchester", "Chelsea", "Arsenal", "Tottenham", "Newcastle", "Leicester", "Everton", "West Ham", "Aston Villa", "Leeds", "Wolves", "Southampton", "Crystal Palace", "Brighton", "Burnley", "Watford", "Norwich", "Brentford", "Fulham", "Bournemouth", "Nottingham", "Blackburn", "Sheffield", "Middlesbrough", "West Brom", "Stoke", "Derby", "Hull", "Cardiff", "Swansea", "Reading", "QPR", "Millwall", "Preston", "Coventry", "Bristol", "Birmingham", "Blackpool", "Rotherham", "Wycombe", "Accrington", "Burton", "Cambridge", "Cheltenham", "Colchester", "Crawley", "Crewe", "Doncaster", "Fleetwood", "Gillingham", "Harrogate", "Hartlepool", "Leyton", "Mansfield", "Newport", "Northampton", "Oldham", "Port Vale", "Rochdale", "Salford", "Scunthorpe", "Stevenage", "Sutton", "Tranmere", "Walsall"]):
                    pais = "Inglaterra"
                elif any(p in home or p in away for p in ["Boca", "River", "Racing", "Independiente", "San Lorenzo", "Lanus", "Velez", "Tigre", "Platense", "Newells", "Old Boys", "Argentinos", "Rosario", "Central", "Banfield", "Gimnasia", "La Plata", "Estudiantes", "Huracan", "Talleres", "Cordoba", "Colon", "Santa Fe", "Union", "Atletico Tucuman", "Aldosivi", "Sarmiento", "Junin", "Defensa", "Justicia", "Godoy Cruz", "Barracas", "Central", "Arsenal", "Patronato"]):
                    pais = "Argentina"
                elif any(p in home or p in away for p in ["PSG", "Marseille", "Lyon", "Monaco", "Lille", "Nice", "Rennes", "Lens", "Montpellier", "Nantes", "Strasbourg", "Angers", "Auxerre", "Brest", "Clermont", "Lorient", "Reims", "Toulouse", "Troyes", "Ajaccio", "Amiens", "Annecy", "Bastia", "Bordeaux", "Caen", "Dijon", "Grenoble", "Guingamp", "Laval", "Le Havre", "Metz", "Nancy", "Niort", "Paris FC", "Pau", "Quevilly", "Rodez", "Saint-Etienne", "Sochaux", "Valenciennes"]):
                    pais = "Francia"
                
                # Guardar por pa?s
                if pais not in eventos_por_pais:
                    eventos_por_pais[pais] = []
                eventos_por_pais[pais].append(f"{home} vs {away}")
                
                # Guardar por liga (aproximada)
                liga = f"{pais} - {region}"
                if liga not in equipos_por_liga:
                    equipos_por_liga[liga] = set()
                equipos_por_liga[liga].add(home)
                equipos_por_liga[liga].add(away)
    
    # Mostrar resultados
    print("\n" + "=" * 80)
    print(f"?? TOTAL DE EQUIPOS ?NICOS ENCONTRADOS: {len(todos_los_equipos)}")
    print("=" * 80)
    
    # Mostrar equipos por pa?s
    print("\n?? DISTRIBUCI?N POR PA?S:")
    print("-" * 60)
    for pais, eventos in sorted(eventos_por_pais.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{pais}: {len(eventos)} eventos")
        # Mostrar algunos ejemplos
        for evento in eventos[:3]:
            print(f"   ? {evento}")
        if len(eventos) > 3:
            print(f"   ... y {len(eventos)-3} m?s")
    
    # Mostrar todos los equipos en formato para el traductor
    print("\n" + "=" * 80)
    print("?? LISTA COMPLETA DE EQUIPOS PARA EL TRADUCTOR:")
    print("=" * 80)
    
    # Ordenar alfab?ticamente
    equipos_ordenados = sorted(todos_los_equipos)
    
    # Crear un diccionario de traducci?n base
    print("\n# Traducciones generadas autom?ticamente:\n")
    for equipo in equipos_ordenados:
        # Crear versiones normalizadas del nombre
        nombre_lower = equipo.lower()
        palabras = nombre_lower.split()
        
        # Versi?n sin acentos (aproximada)
        sin_acentos = (nombre_lower.replace('?', 'u').replace('?', 'o').replace('?', 'a')
                      .replace('?', 'ss').replace('?', 'e').replace('?', 'a')
                      .replace('?', 'i').replace('?', 'o').replace('?', 'u'))
        
        print(f'# "{nombre_lower}" -> "{equipo}"')
        print(f'# "{sin_acentos}" -> "{equipo}"')
        for palabra in palabras:
            if len(palabra) > 3:  # Ignorar palabras muy cortas
                print(f'# "{palabra}" -> "{equipo}"')
        print()
    
    # Guardar en archivo para referencia
    with open('equipos_api.txt', 'w', encoding='utf-8') as f:
        f.write("EQUIPOS ENCONTRADOS EN THE ODDS API\n")
        f.write("=" * 50 + "\n\n")
        for equipo in equipos_ordenados:
            f.write(f"{equipo}\n")
    
    print(f"\n?? Lista guardada en 'equipos_api.txt' ({len(equipos_ordenados)} equipos)")
    
else:
    print("? No se pudo conectar a la API")

print("\n" + "=" * 80)
