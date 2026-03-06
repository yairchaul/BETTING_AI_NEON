#!/usr/bin/env python3
"""
Agregar equipos que aparecen en las capturas de Caliente.mx
"""
import json
import os

print("📸 AGREGANDO EQUIPOS DE CAPTURAS DE CALIENTE.MX")
print("=" * 70)

equipos_capturas = [
    # Eredivisie (Holanda)
    {"id": 1942, "name": "Ajax Amsterdam", "country": "Netherlands"},
    {"id": 1943, "name": "PSV Eindhoven", "country": "Netherlands"},
    {"id": 1944, "name": "Feyenoord", "country": "Netherlands"},
    {"id": 1945, "name": "AZ Alkmaar", "country": "Netherlands"},
    {"id": 1946, "name": "FC Utrecht", "country": "Netherlands"},
    {"id": 1948, "name": "FC Twente", "country": "Netherlands"},
    {"id": 1950, "name": "FC Groningen", "country": "Netherlands"},
    {"id": 1956, "name": "Sparta Rotterdam", "country": "Netherlands"},
    {"id": 1957, "name": "PEC Zwolle", "country": "Netherlands"},
    {"id": 1958, "name": "Heracles Almelo", "country": "Netherlands"},
    {"id": 1960, "name": "SBV Excelsior", "country": "Netherlands"},
    {"id": 1949, "name": "SC Heerenveen", "country": "Netherlands"},
    
    # LaLiga
    {"id": 541, "name": "Real Madrid", "country": "Spain"},
    {"id": 539, "name": "Celta de Vigo", "country": "Spain"},
    
    # Ligue 1
    {"id": 85, "name": "Paris Saint Germain", "country": "France"},
    {"id": 91, "name": "AS Monaco", "country": "France"},
    
    # Serie A
    {"id": 492, "name": "Napoli", "country": "Italy"},
    {"id": 495, "name": "Torino", "country": "Italy"},
    
    # Bundesliga
    {"id": 157, "name": "Bayern Munich", "country": "Germany"},
    {"id": 161, "name": "Borussia Monchengladbach", "country": "Germany"},
]

# Cargar base de datos
db_file = "data/teams_database.json"
with open(db_file, 'r') as f:
    db = json.load(f)

agregados = 0
for equipo in equipos_capturas:
    team_id = str(equipo['id'])
    if team_id not in db.get('teams', {}):
        db['teams'][team_id] = equipo
        name_lower = equipo['name'].lower()
        db['indexes']['by_name'][name_lower] = team_id
        print(f"  ✅ Agregado: {equipo['name']}")
        agregados += 1

db['total_teams'] = len(db['teams'])
with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)

print(f"\n✅ {agregados} equipos agregados")
