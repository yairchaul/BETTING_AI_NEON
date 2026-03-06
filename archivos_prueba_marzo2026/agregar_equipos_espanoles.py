#!/usr/bin/env python3
"""
Agregar equipos españoles manualmente a la base de datos
"""
import json
import os

# Lista de equipos españoles principales (IDs reales de API-Football)
equipos_espanoles = [
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
]

print("🇪🇸 AGREGANDO EQUIPOS ESPAÑOLES")
print("=" * 60)

# Cargar base de datos actual
db_file = 'data/teams_database.json'
with open(db_file, 'r') as f:
    db = json.load(f)

# Verificar estructura y convertir si es necesario
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

# Agregar equipos españoles
agregados = 0
existentes = 0

for equipo in equipos_espanoles:
    equipo_id = str(equipo['id'])
    equipo_nombre = equipo['name']
    
    # Verificar si ya existe
    if equipo_id in db.get('teams', {}):
        print(f"⏭️  {equipo_nombre} ya existe (ID: {equipo_id})")
        existentes += 1
        continue
    
    # Agregar a teams
    if 'teams' not in db:
        db['teams'] = {}
    db['teams'][equipo_id] = equipo
    
    # Agregar a índices
    if 'indexes' not in db:
        db['indexes'] = {'by_name': {}}
    if 'by_name' not in db['indexes']:
        db['indexes']['by_name'] = {}
    
    nombre_lower = equipo_nombre.lower()
    db['indexes']['by_name'][nombre_lower] = equipo_id
    
    # También agregar sin espacios
    if ' ' in nombre_lower:
        db['indexes']['by_name'][nombre_lower.replace(' ', '')] = equipo_id
    
    print(f"✅ Agregado: {equipo_nombre} (ID: {equipo_id})")
    agregados += 1

# Actualizar total_teams
db['total_teams'] = len(db.get('teams', {}))

# Guardar cambios
with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)

print("\n" + "=" * 60)
print(f"📊 RESUMEN:")
print(f"   - Equipos agregados: {agregados}")
print(f"   - Equipos ya existentes: {existentes}")
print(f"   - Total equipos ahora: {db['total_teams']}")
print(f"   - Total índices: {len(db.get('indexes', {}).get('by_name', {}))}")
