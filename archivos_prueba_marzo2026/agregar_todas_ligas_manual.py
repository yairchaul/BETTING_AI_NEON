#!/usr/bin/env python3
"""
Agregar todas las ligas europeas manualmente a la base de datos
"""
import json
import os
from pathlib import Path

print("🌍 AGREGANDO TODAS LAS LIGAS EUROPEAS MANUALMENTE")
print("=" * 70)

# ============================================
# INGLATERRA - Premier League
# ============================================
equipos_inglaterra = [
    {"id": 33, "name": "Manchester United", "country": "England"},
    {"id": 34, "name": "Newcastle", "country": "England"},
    {"id": 35, "name": "Bournemouth", "country": "England"},
    {"id": 36, "name": "Fulham", "country": "England"},
    {"id": 37, "name": "Huddersfield", "country": "England"},
    {"id": 38, "name": "Watford", "country": "England"},
    {"id": 39, "name": "Wolves", "country": "England"},
    {"id": 40, "name": "Liverpool", "country": "England"},
    {"id": 41, "name": "Southampton", "country": "England"},
    {"id": 42, "name": "Arsenal", "country": "England"},
    {"id": 43, "name": "Burnley", "country": "England"},
    {"id": 44, "name": "Everton", "country": "England"},
    {"id": 45, "name": "Leicester", "country": "England"},
    {"id": 46, "name": "Tottenham", "country": "England"},
    {"id": 47, "name": "Tottenham", "country": "England"},  # Duplicado? 
    {"id": 48, "name": "West Ham", "country": "England"},
    {"id": 49, "name": "Chelsea", "country": "England"},
    {"id": 50, "name": "Manchester City", "country": "England"},
    {"id": 51, "name": "Brighton", "country": "England"},
    {"id": 52, "name": "Crystal Palace", "country": "England"},
    {"id": 53, "name": "Aston Villa", "country": "England"},
    {"id": 54, "name": "Nottingham Forest", "country": "England"},
    {"id": 55, "name": "Brentford", "country": "England"},
    {"id": 56, "name": "Ipswich", "country": "England"},
    {"id": 57, "name": "Leeds", "country": "England"},
    {"id": 58, "name": "Sheffield United", "country": "England"},
    {"id": 59, "name": "West Bromwich", "country": "England"},
    {"id": 60, "name": "Stoke City", "country": "England"},
]

# ============================================
# ESPAÑA - LaLiga
# ============================================
equipos_espana = [
    {"id": 529, "name": "Barcelona", "country": "Spain"},
    {"id": 541, "name": "Real Madrid", "country": "Spain"},
    {"id": 530, "name": "Atletico Madrid", "country": "Spain"},
    {"id": 531, "name": "Athletic Bilbao", "country": "Spain"},
    {"id": 532, "name": "Valencia", "country": "Spain"},
    {"id": 533, "name": "Sevilla", "country": "Spain"},
    {"id": 534, "name": "Real Betis", "country": "Spain"},
    {"id": 535, "name": "Villarreal", "country": "Spain"},
    {"id": 536, "name": "Real Sociedad", "country": "Spain"},
    {"id": 537, "name": "Espanyol", "country": "Spain"},
    {"id": 538, "name": "Getafe", "country": "Spain"},
    {"id": 539, "name": "Celta Vigo", "country": "Spain"},
    {"id": 540, "name": "Granada", "country": "Spain"},
    {"id": 542, "name": "Osasuna", "country": "Spain"},
    {"id": 543, "name": "Alaves", "country": "Spain"},
    {"id": 544, "name": "Cadiz", "country": "Spain"},
    {"id": 545, "name": "Elche", "country": "Spain"},
    {"id": 546, "name": "Mallorca", "country": "Spain"},
    {"id": 547, "name": "Rayo Vallecano", "country": "Spain"},
    {"id": 548, "name": "Girona", "country": "Spain"},
    {"id": 549, "name": "Las Palmas", "country": "Spain"},
    {"id": 550, "name": "Almeria", "country": "Spain"},
]

# ============================================
# HOLANDA - Eredivisie
# ============================================
equipos_holanda = [
    {"id": 1942, "name": "Ajax", "country": "Netherlands"},
    {"id": 1943, "name": "PSV Eindhoven", "country": "Netherlands"},
    {"id": 1944, "name": "Feyenoord", "country": "Netherlands"},
    {"id": 1945, "name": "AZ Alkmaar", "country": "Netherlands"},
    {"id": 1946, "name": "FC Utrecht", "country": "Netherlands"},
    {"id": 1947, "name": "Vitesse", "country": "Netherlands"},
    {"id": 1948, "name": "FC Twente", "country": "Netherlands"},
    {"id": 1949, "name": "SC Heerenveen", "country": "Netherlands"},
    {"id": 1950, "name": "FC Groningen", "country": "Netherlands"},
    {"id": 1951, "name": "Willem II", "country": "Netherlands"},
    {"id": 1952, "name": "NEC Nijmegen", "country": "Netherlands"},
    {"id": 1953, "name": "Fortuna Sittard", "country": "Netherlands"},
    {"id": 1954, "name": "Go Ahead Eagles", "country": "Netherlands"},
    {"id": 1955, "name": "RKC Waalwijk", "country": "Netherlands"},
    {"id": 1956, "name": "Sparta Rotterdam", "country": "Netherlands"},
    {"id": 1957, "name": "PEC Zwolle", "country": "Netherlands"},
    {"id": 1958, "name": "Heracles Almelo", "country": "Netherlands"},
]

# ============================================
# PORTUGAL - Primeira Liga
# ============================================
equipos_portugal = [
    {"id": 211, "name": "Benfica", "country": "Portugal"},
    {"id": 212, "name": "Porto", "country": "Portugal"},
    {"id": 213, "name": "Sporting CP", "country": "Portugal"},
    {"id": 214, "name": "Braga", "country": "Portugal"},
    {"id": 215, "name": "Vitória Guimarães", "country": "Portugal"},
    {"id": 216, "name": "Boavista", "country": "Portugal"},
    {"id": 217, "name": "Rio Ave", "country": "Portugal"},
    {"id": 218, "name": "Famalicão", "country": "Portugal"},
    {"id": 219, "name": "Moreirense", "country": "Portugal"},
    {"id": 220, "name": "Gil Vicente", "country": "Portugal"},
    {"id": 221, "name": "Estoril", "country": "Portugal"},
    {"id": 222, "name": "Portimonense", "country": "Portugal"},
    {"id": 223, "name": "Marítimo", "country": "Portugal"},
    {"id": 224, "name": "Nacional", "country": "Portugal"},
    {"id": 225, "name": "Santa Clara", "country": "Portugal"},
    {"id": 226, "name": "Chaves", "country": "Portugal"},
    {"id": 227, "name": "Vizela", "country": "Portugal"},
    {"id": 228, "name": "Arouca", "country": "Portugal"},
    {"id": 229, "name": "Casa Pia", "country": "Portugal"},
    {"id": 230, "name": "Estrela Amadora", "country": "Portugal"},
]

# ============================================
# ALEMANIA - Bundesliga
# ============================================
equipos_alemania = [
    {"id": 157, "name": "Bayern München", "country": "Germany"},
    {"id": 158, "name": "Borussia Dortmund", "country": "Germany"},
    {"id": 159, "name": "RB Leipzig", "country": "Germany"},
    {"id": 160, "name": "Bayer Leverkusen", "country": "Germany"},
    {"id": 161, "name": "Borussia Mönchengladbach", "country": "Germany"},
    {"id": 162, "name": "Wolfsburg", "country": "Germany"},
    {"id": 163, "name": "Eintracht Frankfurt", "country": "Germany"},
    {"id": 164, "name": "Werder Bremen", "country": "Germany"},
    {"id": 165, "name": "Hoffenheim", "country": "Germany"},
    {"id": 166, "name": "Freiburg", "country": "Germany"},
    {"id": 167, "name": "Union Berlin", "country": "Germany"},
    {"id": 168, "name": "Mainz", "country": "Germany"},
    {"id": 169, "name": "Augsburg", "country": "Germany"},
    {"id": 170, "name": "Stuttgart", "country": "Germany"},
    {"id": 171, "name": "Köln", "country": "Germany"},
    {"id": 172, "name": "Bochum", "country": "Germany"},
    {"id": 173, "name": "Darmstadt", "country": "Germany"},
    {"id": 174, "name": "Heidenheim", "country": "Germany"},
]

# ============================================
# ITALIA - Serie A
# ============================================
equipos_italia = [
    {"id": 487, "name": "Juventus", "country": "Italy"},
    {"id": 488, "name": "Milan", "country": "Italy"},
    {"id": 489, "name": "Inter", "country": "Italy"},
    {"id": 490, "name": "Roma", "country": "Italy"},
    {"id": 491, "name": "Lazio", "country": "Italy"},
    {"id": 492, "name": "Napoli", "country": "Italy"},
    {"id": 493, "name": "Atalanta", "country": "Italy"},
    {"id": 494, "name": "Fiorentina", "country": "Italy"},
    {"id": 495, "name": "Torino", "country": "Italy"},
    {"id": 496, "name": "Bologna", "country": "Italy"},
    {"id": 497, "name": "Sassuolo", "country": "Italy"},
    {"id": 498, "name": "Udinese", "country": "Italy"},
    {"id": 499, "name": "Empoli", "country": "Italy"},
    {"id": 500, "name": "Lecce", "country": "Italy"},
    {"id": 501, "name": "Salernitana", "country": "Italy"},
    {"id": 502, "name": "Spezia", "country": "Italy"},
    {"id": 503, "name": "Cremonese", "country": "Italy"},
    {"id": 504, "name": "Monza", "country": "Italy"},
    {"id": 505, "name": "Verona", "country": "Italy"},
    {"id": 506, "name": "Sampdoria", "country": "Italy"},
]

# ============================================
# FRANCIA - Ligue 1
# ============================================
equipos_francia = [
    {"id": 85, "name": "Paris Saint Germain", "country": "France"},
    {"id": 86, "name": "Marseille", "country": "France"},
    {"id": 87, "name": "Lyon", "country": "France"},
    {"id": 88, "name": "Monaco", "country": "France"},
    {"id": 89, "name": "Lille", "country": "France"},
    {"id": 90, "name": "Rennes", "country": "France"},
    {"id": 91, "name": "Nice", "country": "France"},
    {"id": 92, "name": "Lens", "country": "France"},
    {"id": 93, "name": "Strasbourg", "country": "France"},
    {"id": 94, "name": "Nantes", "country": "France"},
    {"id": 95, "name": "Montpellier", "country": "France"},
    {"id": 96, "name": "Reims", "country": "France"},
    {"id": 97, "name": "Toulouse", "country": "France"},
    {"id": 98, "name": "Brest", "country": "France"},
    {"id": 99, "name": "Clermont", "country": "France"},
    {"id": 100, "name": "Auxerre", "country": "France"},
    {"id": 101, "name": "Ajaccio", "country": "France"},
    {"id": 102, "name": "Troyes", "country": "France"},
    {"id": 103, "name": "Angers", "country": "France"},
    {"id": 104, "name": "Lorient", "country": "France"},
]

# Agrupar todos los equipos
todos_los_equipos = []
todos_los_equipos.extend(equipos_inglaterra)
todos_los_equipos.extend(equipos_espana)
todos_los_equipos.extend(equipos_holanda)
todos_los_equipos.extend(equipos_portugal)
todos_los_equipos.extend(equipos_alemania)
todos_los_equipos.extend(equipos_italia)
todos_los_equipos.extend(equipos_francia)

print(f"📊 Total equipos a agregar: {len(todos_los_equipos)}")

# Cargar base de datos actual o crear nueva
db_file = "data/teams_database.json"
if os.path.exists(db_file):
    with open(db_file, 'r') as f:
        db = json.load(f)
    print(f"✅ Base actual cargada")
else:
    db = {
        "total_teams": 0,
        "indexes": {"by_name": {}},
        "teams": {}
    }
    print("🆕 Creando nueva base de datos")

# Verificar estructura
if isinstance(db, list):
    print("⚠️ Convirtiendo de lista a diccionario...")
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

# Agregar equipos
agregados = 0
duplicados = 0

print("\n📝 Agregando equipos:")
for equipo in todos_los_equipos:
    team_id = str(equipo['id'])
    team_name = equipo['name']
    
    if team_id in db.get('teams', {}):
        print(f"   ⏭️  {team_name} ya existe (ID: {team_id})")
        duplicados += 1
        continue
    
    # Agregar a teams
    if 'teams' not in db:
        db['teams'] = {}
    db['teams'][team_id] = equipo
    
    # Agregar a índices
    if 'indexes' not in db:
        db['indexes'] = {'by_name': {}}
    if 'by_name' not in db['indexes']:
        db['indexes']['by_name'] = {}
    
    name_lower = team_name.lower()
    db['indexes']['by_name'][name_lower] = team_id
    
    # Variantes comunes
    if ' ' in name_lower:
        db['indexes']['by_name'][name_lower.replace(' ', '')] = team_id
    
    # Variantes específicas
    if 'manchester united' in name_lower:
        db['indexes']['by_name']['manutd'] = team_id
        db['indexes']['by_name']['united'] = team_id
    elif 'liverpool' in name_lower:
        db['indexes']['by_name']['lfc'] = team_id
    elif 'arsenal' in name_lower:
        db['indexes']['by_name']['arsenal'] = team_id
    elif 'chelsea' in name_lower:
        db['indexes']['by_name']['chelsea'] = team_id
    elif 'tottenham' in name_lower:
        db['indexes']['by_name']['spurs'] = team_id
    elif 'real madrid' in name_lower:
        db['indexes']['by_name']['realmadrid'] = team_id
        db['indexes']['by_name']['madrid'] = team_id
    elif 'barcelona' in name_lower:
        db['indexes']['by_name']['barca'] = team_id
    elif 'bayern' in name_lower:
        db['indexes']['by_name']['bayern'] = team_id
    elif 'ajax' in name_lower:
        db['indexes']['by_name']['ajax'] = team_id
    elif 'psv' in name_lower:
        db['indexes']['by_name']['psv'] = team_id
    elif 'benfica' in name_lower:
        db['indexes']['by_name']['benfica'] = team_id
    elif 'porto' in name_lower:
        db['indexes']['by_name']['porto'] = team_id
    
    print(f"   ✅ {team_name} (ID: {team_id}, {equipo['country']})")
    agregados += 1

# Actualizar total
db['total_teams'] = len(db.get('teams', {}))

# Guardar cambios
backup_file = "data/teams_database_backup_manual.json"
if os.path.exists(db_file):
    os.rename(db_file, backup_file)
    print(f"\n✅ Backup guardado: {backup_file}")

with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)

print("\n" + "=" * 70)
print("📊 RESUMEN FINAL")
print("=" * 70)
print(f"✅ Equipos agregados: {agregados}")
print(f"⏭️  Equipos duplicados: {duplicados}")
print(f"📊 Total equipos en base: {db['total_teams']}")
print(f"📊 Total índices: {len(db.get('indexes', {}).get('by_name', {}))}")

# Verificar equipos clave
print("\n🔍 VERIFICANDO EQUIPOS CLAVE:")
from modules.team_database import TeamDatabase
db_check = TeamDatabase()
equipos_clave = [
    'Tottenham', 'Arsenal', 'Liverpool', 'Manchester United',
    'Real Madrid', 'Barcelona', 'Atletico Madrid',
    'Ajax', 'PSV Eindhoven', 'Benfica', 'Porto',
    'Bayern München', 'Borussia Dortmund',
    'Juventus', 'Milan', 'Inter',
    'Paris Saint Germain', 'Marseille'
]

for equipo in equipos_clave:
    team_id = db_check.get_team_id(equipo)
    if team_id:
        print(f"  ✅ {equipo}: ID {team_id}")
    else:
        print(f"  ❌ {equipo}: No encontrado")
