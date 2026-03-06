#!/usr/bin/env python3
"""
Agregar equipos de Holanda (Eredivisie) y Portugal (Primeira Liga) a la base de datos
"""
import json
import os

print("🇳🇱🇵🇹 AGREGANDO EQUIPOS DE HOLANDA Y PORTUGAL")
print("=" * 60)

# Equipos de Holanda - Eredivisie (IDs reales de API-Football)
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
    {"id": 1959, "name": "Almere City", "country": "Netherlands"},
    {"id": 1960, "name": "Volendam", "country": "Netherlands"},
    {"id": 1961, "name": "Excelsior", "country": "Netherlands"},
]

# Equipos de Portugal - Primeira Liga
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

# Función para agregar equipos
def agregar_equipos(equipos, pais):
    agregados = 0
    existentes = 0
    
    for equipo in equipos:
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
        
        # Agregar variantes comunes
        if equipo_nombre == "Ajax":
            db['indexes']['by_name']['ajax amsterdam'] = equipo_id
        elif equipo_nombre == "PSV Eindhoven":
            db['indexes']['by_name']['psv'] = equipo_id
        elif equipo_nombre == "Sporting CP":
            db['indexes']['by_name']['sporting'] = equipo_id
            db['indexes']['by_name']['sporting lisboa'] = equipo_id
        elif equipo_nombre == "Benfica":
            db['indexes']['by_name']['sl benfica'] = equipo_id
        elif equipo_nombre == "Porto":
            db['indexes']['by_name']['fc porto'] = equipo_id
        
        print(f"✅ Agregado: {equipo_nombre} (ID: {equipo_id})")
        agregados += 1
    
    return agregados, existentes

print(f"\n📊 Procesando Holanda...")
agregados_holanda, existentes_holanda = agregar_equipos(equipos_holanda, "Holanda")

print(f"\n📊 Procesando Portugal...")
agregados_portugal, existentes_portugal = agregar_equipos(equipos_portugal, "Portugal")

# Actualizar total_teams
db['total_teams'] = len(db.get('teams', {}))

# Guardar cambios
with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)

print("\n" + "=" * 60)
print("📊 RESUMEN FINAL:")
print(f"   🇳🇱 Holanda: +{agregados_holanda} equipos (ya existían: {existentes_holanda})")
print(f"   🇵🇹 Portugal: +{agregados_portugal} equipos (ya existían: {existentes_portugal})")
print(f"   Total equipos ahora: {db['total_teams']}")
print(f"   Total índices: {len(db.get('indexes', {}).get('by_name', {}))}")

# Verificar algunos equipos clave
print("\n🔍 Verificando equipos agregados:")
equipos_verificar = [
    ("Ajax", "Holanda"),
    ("PSV Eindhoven", "Holanda"),
    ("Feyenoord", "Holanda"),
    ("Benfica", "Portugal"),
    ("Porto", "Portugal"),
    ("Sporting CP", "Portugal")
]

for equipo, pais in equipos_verificar:
    if equipo.lower() in db['indexes']['by_name']:
        team_id = db['indexes']['by_name'][equipo.lower()]
        print(f"   ✅ {equipo}: ID {team_id}")
    else:
        print(f"   ❌ {equipo}: No encontrado")
