#!/usr/bin/env python3
"""
Agregar equipos de todas las ligas europeas principales
"""
import json
import os

print("🌍 AGREGANDO TODAS LAS LIGAS EUROPEAS")
print("=" * 60)

# ============================================
# BÉLGICA - Jupiler Pro League
# ============================================
equipos_belgica = [
    {"id": 569, "name": "Anderlecht", "country": "Belgium"},
    {"id": 570, "name": "Club Brugge", "country": "Belgium"},
    {"id": 571, "name": "Standard Liège", "country": "Belgium"},
    {"id": 572, "name": "Genk", "country": "Belgium"},
    {"id": 573, "name": "Gent", "country": "Belgium"},
    {"id": 574, "name": "Antwerp", "country": "Belgium"},
    {"id": 575, "name": "Charleroi", "country": "Belgium"},
    {"id": 576, "name": "Mechelen", "country": "Belgium"},
    {"id": 577, "name": "Sint-Truiden", "country": "Belgium"},
    {"id": 578, "name": "Cercle Brugge", "country": "Belgium"},
    {"id": 579, "name": "OH Leuven", "country": "Belgium"},
    {"id": 580, "name": "Kortrijk", "country": "Belgium"},
    {"id": 581, "name": "Eupen", "country": "Belgium"},
    {"id": 582, "name": "Westerlo", "country": "Belgium"},
    {"id": 583, "name": "RWDM", "country": "Belgium"},
]

# ============================================
# TURQUÍA - Süper Lig
# ============================================
equipos_turquia = [
    {"id": 611, "name": "Galatasaray", "country": "Turkey"},
    {"id": 612, "name": "Fenerbahçe", "country": "Turkey"},
    {"id": 613, "name": "Beşiktaş", "country": "Turkey"},
    {"id": 614, "name": "Trabzonspor", "country": "Turkey"},
    {"id": 615, "name": "Başakşehir", "country": "Turkey"},
    {"id": 616, "name": "Sivasspor", "country": "Turkey"},
    {"id": 617, "name": "Alanyaspor", "country": "Turkey"},
    {"id": 618, "name": "Konyaspor", "country": "Turkey"},
    {"id": 619, "name": "Kasımpaşa", "country": "Turkey"},
    {"id": 620, "name": "Antalyaspor", "country": "Turkey"},
    {"id": 621, "name": "Gaziantep FK", "country": "Turkey"},
    {"id": 622, "name": "Adana Demirspor", "country": "Turkey"},
    {"id": 623, "name": "Hatayspor", "country": "Turkey"},
    {"id": 624, "name": "Giresunspor", "country": "Turkey"},
    {"id": 625, "name": "Ümraniyespor", "country": "Turkey"},
]

# ============================================
# RUSIA - Premier League
# ============================================
equipos_rusia = [
    {"id": 596, "name": "Zenit", "country": "Russia"},
    {"id": 597, "name": "Spartak Moscow", "country": "Russia"},
    {"id": 598, "name": "CSKA Moscow", "country": "Russia"},
    {"id": 599, "name": "Lokomotiv Moscow", "country": "Russia"},
    {"id": 600, "name": "Krasnodar", "country": "Russia"},
    {"id": 601, "name": "Rostov", "country": "Russia"},
    {"id": 602, "name": "Dynamo Moscow", "country": "Russia"},
    {"id": 603, "name": "Akhmat Grozny", "country": "Russia"},
    {"id": 604, "name": "Krylia Sovetov", "country": "Russia"},
    {"id": 605, "name": "Ural", "country": "Russia"},
    {"id": 606, "name": "Sochi", "country": "Russia"},
    {"id": 607, "name": "Orenburg", "country": "Russia"},
    {"id": 608, "name": "Fakel Voronezh", "country": "Russia"},
    {"id": 609, "name": "Pari Nizhny Novgorod", "country": "Russia"},
    {"id": 610, "name": "Torpedo Moscow", "country": "Russia"},
]

# ============================================
# SUIZA - Super League
# ============================================
equipos_suiza = [
    {"id": 701, "name": "Young Boys", "country": "Switzerland"},
    {"id": 702, "name": "Basel", "country": "Switzerland"},
    {"id": 703, "name": "Servette", "country": "Switzerland"},
    {"id": 704, "name": "Lugano", "country": "Switzerland"},
    {"id": 705, "name": "Luzern", "country": "Switzerland"},
    {"id": 706, "name": "St. Gallen", "country": "Switzerland"},
    {"id": 707, "name": "Winterthur", "country": "Switzerland"},
    {"id": 708, "name": "Grasshopper", "country": "Switzerland"},
    {"id": 709, "name": "Sion", "country": "Switzerland"},
    {"id": 710, "name": "Zürich", "country": "Switzerland"},
]

# ============================================
# AUSTRIA - Bundesliga
# ============================================
equipos_austria = [
    {"id": 801, "name": "Red Bull Salzburg", "country": "Austria"},
    {"id": 802, "name": "Sturm Graz", "country": "Austria"},
    {"id": 803, "name": "LASK", "country": "Austria"},
    {"id": 804, "name": "Rapid Vienna", "country": "Austria"},
    {"id": 805, "name": "Austria Vienna", "country": "Austria"},
    {"id": 806, "name": "Wolfsberger AC", "country": "Austria"},
    {"id": 807, "name": "Hartberg", "country": "Austria"},
    {"id": 808, "name": "Klagenfurt", "country": "Austria"},
    {"id": 809, "name": "Ried", "country": "Austria"},
    {"id": 810, "name": "Altach", "country": "Austria"},
]

# ============================================
# ESCOCIA - Premiership
# ============================================
equipos_escocia = [
    {"id": 901, "name": "Celtic", "country": "Scotland"},
    {"id": 902, "name": "Rangers", "country": "Scotland"},
    {"id": 903, "name": "Aberdeen", "country": "Scotland"},
    {"id": 904, "name": "Hearts", "country": "Scotland"},
    {"id": 905, "name": "Hibernian", "country": "Scotland"},
    {"id": 906, "name": "St. Mirren", "country": "Scotland"},
    {"id": 907, "name": "Motherwell", "country": "Scotland"},
    {"id": 908, "name": "Livingston", "country": "Scotland"},
    {"id": 909, "name": "Kilmarnock", "country": "Scotland"},
    {"id": 910, "name": "St. Johnstone", "country": "Scotland"},
    {"id": 911, "name": "Ross County", "country": "Scotland"},
    {"id": 912, "name": "Dundee United", "country": "Scotland"},
]

# ============================================
# DINAMARCA - Superliga
# ============================================
equipos_dinamarca = [
    {"id": 1001, "name": "FC Copenhagen", "country": "Denmark"},
    {"id": 1002, "name": "Midtjylland", "country": "Denmark"},
    {"id": 1003, "name": "Brøndby", "country": "Denmark"},
    {"id": 1004, "name": "Aarhus", "country": "Denmark"},
    {"id": 1005, "name": "Nordsjælland", "country": "Denmark"},
    {"id": 1006, "name": "Randers", "country": "Denmark"},
    {"id": 1007, "name": "Silkeborg", "country": "Denmark"},
    {"id": 1008, "name": "Viborg", "country": "Denmark"},
    {"id": 1009, "name": "Lyngby", "country": "Denmark"},
    {"id": 1010, "name": "Odense", "country": "Denmark"},
]

# ============================================
# SUECIA - Allsvenskan
# ============================================
equipos_suecia = [
    {"id": 1101, "name": "Malmö FF", "country": "Sweden"},
    {"id": 1102, "name": "AIK", "country": "Sweden"},
    {"id": 1103, "name": "Djurgården", "country": "Sweden"},
    {"id": 1104, "name": "Hammarby", "country": "Sweden"},
    {"id": 1105, "name": "IFK Göteborg", "country": "Sweden"},
    {"id": 1106, "name": "Elfsborg", "country": "Sweden"},
    {"id": 1107, "name": "Norrköping", "country": "Sweden"},
    {"id": 1108, "name": "Häcken", "country": "Sweden"},
    {"id": 1109, "name": "Sirius", "country": "Sweden"},
    {"id": 1110, "name": "Varberg", "country": "Sweden"},
]

# ============================================
# NORUEGA - Eliteserien
# ============================================
equipos_noruega = [
    {"id": 1201, "name": "Molde", "country": "Norway"},
    {"id": 1202, "name": "Bodø/Glimt", "country": "Norway"},
    {"id": 1203, "name": "Rosenborg", "country": "Norway"},
    {"id": 1204, "name": "Viking", "country": "Norway"},
    {"id": 1205, "name": "Lillestrøm", "country": "Norway"},
    {"id": 1206, "name": "Brann", "country": "Norway"},
    {"id": 1207, "name": "Vålerenga", "country": "Norway"},
    {"id": 1208, "name": "Sarpsborg", "country": "Norway"},
    {"id": 1209, "name": "Strømsgodset", "country": "Norway"},
    {"id": 1210, "name": "Odd", "country": "Norway"},
]

# Agrupar todos los equipos por país
paises = [
    ("🇧🇪 Bélgica", equipos_belgica),
    ("🇹🇷 Turquía", equipos_turquia),
    ("🇷🇺 Rusia", equipos_rusia),
    ("🇨🇭 Suiza", equipos_suiza),
    ("🇦🇹 Austria", equipos_austria),
    ("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", equipos_escocia),
    ("🇩🇰 Dinamarca", equipos_dinamarca),
    ("🇸🇪 Suecia", equipos_suecia),
    ("🇳🇴 Noruega", equipos_noruega),
]

# Cargar base de datos actual
db_file = 'data/teams_database.json'
with open(db_file, 'r') as f:
    db = json.load(f)

# Verificar estructura
if isinstance(db, list):
    print("📋 Base actual es lista, convirtiendo a diccionario...")
    new_db = {
        "total_teams": len(db),
        "indexes": {"by_name": {}},
        "teams": {}
    }
    for team in db:
        if isinstance(team, dict) and 'id' in team:
            team_id = str(team['id'])
            new_db['teams'][team_id] = team
            new_db['indexes']['by_name'][team['name'].lower()] = team_id
    db = new_db

# Función para agregar equipos
def agregar_equipos(equipos, pais_nombre):
    agregados = 0
    existentes = 0
    
    for equipo in equipos:
        equipo_id = str(equipo['id'])
        equipo_nombre = equipo['name']
        
        if equipo_id in db.get('teams', {}):
            print(f"   ⏭️  {equipo_nombre} ya existe")
            existentes += 1
            continue
        
        if 'teams' not in db:
            db['teams'] = {}
        db['teams'][equipo_id] = equipo
        
        if 'indexes' not in db:
            db['indexes'] = {'by_name': {}}
        if 'by_name' not in db['indexes']:
            db['indexes']['by_name'] = {}
        
        nombre_lower = equipo_nombre.lower()
        db['indexes']['by_name'][nombre_lower] = equipo_id
        
        if ' ' in nombre_lower:
            db['indexes']['by_name'][nombre_lower.replace(' ', '')] = equipo_id
        
        # Variantes comunes
        if equipo_nombre == "Red Bull Salzburg":
            db['indexes']['by_name']['salzburg'] = equipo_id
        elif equipo_nombre == "FC Copenhagen":
            db['indexes']['by_name']['copenhagen'] = equipo_id
            db['indexes']['by_name']['københavn'] = equipo_id
        
        print(f"   ✅ Agregado: {equipo_nombre}")
        agregados += 1
    
    return agregados, existentes

# Procesar cada país
total_agregados = 0
total_existentes = 0

for bandera, equipos in paises:
    print(f"\n{bandera}:")
    agregados, existentes = agregar_equipos(equipos, bandera)
    total_agregados += agregados
    total_existentes += existentes
    print(f"   → +{agregados} nuevos (ya existían: {existentes})")

# Actualizar total_teams
db['total_teams'] = len(db.get('teams', {}))

# Guardar cambios
with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)

print("\n" + "=" * 60)
print("📊 RESUMEN FINAL:")
print(f"   Total equipos agregados: {total_agregados}")
print(f"   Total equipos ya existentes: {total_existentes}")
print(f"   Total equipos ahora: {db['total_teams']}")
print(f"   Total índices: {len(db.get('indexes', {}).get('by_name', {}))}")
