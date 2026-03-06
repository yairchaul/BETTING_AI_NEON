#!/usr/bin/env python3
"""
Agregar equipos faltantes de las capturas
"""
import json

print("➕ AGREGANDO EQUIPOS FALTANTES")
print("=" * 60)

equipos_faltantes = [
    # Eredivisie
    {"id": 1960, "name": "Excelsior", "country": "Netherlands", "variantes": ["sbv excelsior", "excelsior rotterdam"]},
    
    # LaLiga
    {"id": 539, "name": "Celta de Vigo", "country": "Spain", "variantes": ["celta", "rc celta"]},
    
    # Ligue 1
    {"id": 85, "name": "Paris Saint Germain", "country": "France", "variantes": ["psg", "paris sg", "paris saint-germain"]},
    
    # Serie A - CORREGIDO: Napoli (no Nápoles)
    {"id": 492, "name": "Napoli", "country": "Italy", "variantes": ["napoles", ssc napoli", "napoli"]},
    
    # Bundesliga - CORREGIDO: Borussia Mönchengladbach
    {"id": 161, "name": "Borussia Mönchengladbach", "country": "Germany", "variantes": ["borussia monchengladbach", "bm gladbach", "gladbach"]},
]

# Cargar base de datos actual
with open('data/teams_database.json', 'r') as f:
    db = json.load(f)

print(f"📊 Base actual: {db.get('total_teams', 0)} equipos")

agregados = 0
for equipo in equipos_faltantes:
    team_id = str(equipo['id'])
    team_name = equipo['name']
    
    if team_id in db.get('teams', {}):
        print(f"⏭️  {team_name} ya existe (ID: {team_id})")
        continue
    
    # Agregar a teams
    if 'teams' not in db:
        db['teams'] = {}
    db['teams'][team_id] = {
        'id': equipo['id'],
        'name': team_name,
        'country': equipo['country'],
        'code': '',
        'founded': 0,
        'logo': ''
    }
    
    # Agregar índices
    if 'indexes' not in db:
        db['indexes'] = {'by_name': {}}
    
    name_lower = team_name.lower()
    db['indexes']['by_name'][name_lower] = team_id
    
    # Variantes
    for variante in equipo.get('variantes', []):
        db['indexes']['by_name'][variante] = team_id
    
    # Sin espacios
    if ' ' in name_lower:
        db['indexes']['by_name'][name_lower.replace(' ', '')] = team_id
    
    print(f"✅ Agregado: {team_name} (ID: {team_id})")
    agregados += 1

# Actualizar total
db['total_teams'] = len(db.get('teams', {}))

# Guardar
with open('data/teams_database.json', 'w') as f:
    json.dump(db, f, indent=2)

print(f"\n📊 Total agregados: {agregados}")
print(f"📊 Total equipos ahora: {db['total_teams']}")

# Verificar nuevamente
print("\n🔍 VERIFICACIÓN FINAL:")
from modules.team_database import TeamDatabase
db_check = TeamDatabase()

for equipo in ['Excelsior', 'Celta de Vigo', 'PSG', 'Napoli', 'Borussia Mönchengladbach']:
    team_id = db_check.get_team_id(equipo)
    if team_id:
        print(f"  ✅ {equipo}: ID {team_id}")
    else:
        print(f"  ❌ {equipo}: No encontrado")
