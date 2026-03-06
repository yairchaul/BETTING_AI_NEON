#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear la base de datos en formato correcto desde los archivos existentes
"""
import json
import os

print("🔍 CREANDO BASE DE DATOS EN FORMATO CORRECTO")
print("=" * 60)

# Recopilar todos los equipos disponibles
all_teams = []

# 1. Intentar cargar equipos europeos
europe_file = "data/teams_database_europe.json"
if os.path.exists(europe_file):
    with open(europe_file, 'r', encoding='utf-8') as f:
        europe_teams = json.load(f)
        print(f"📊 Equipos europeos: {len(europe_teams)}")
        all_teams.extend(europe_teams)

# 2. Intentar cargar equipos sudamericanos (del backup)
sudamerica_file = "data/teams_database_backup.json"
if os.path.exists(sudamerica_file):
    with open(sudamerica_file, 'r', encoding='utf-8') as f:
        sudamerica_teams = json.load(f)
        print(f"📊 Equipos sudamericanos: {len(sudamerica_teams)}")
        all_teams.extend(sudamerica_teams)

# 3. Si no hay sudamericanos, intentar con el archivo original
if not os.path.exists(sudamerica_file):
    original_file = "data/teams_database_old.json"
    if os.path.exists(original_file):
        with open(original_file, 'r', encoding='utf-8') as f:
            original_teams = json.load(f)
            print(f"📊 Equipos originales: {len(original_teams)}")
            all_teams.extend(original_teams)

print(f"\n📊 Total equipos recopilados: {len(all_teams)}")

# Eliminar duplicados por ID
unique_teams = {}
for team in all_teams:
    if isinstance(team, dict) and 'id' in team:
        team_id = team['id']
        if team_id not in unique_teams:
            unique_teams[team_id] = team

print(f"✅ Equipos únicos: {len(unique_teams)}")

# Crear la estructura esperada por TeamDatabase
database = {
    "total_teams": len(unique_teams),
    "indexes": {
        "by_name": {}
    },
    "teams": {}
}

# Llenar la estructura
for team_id, team in unique_teams.items():
    team_id_str = str(team_id)
    team_name = team.get('name', '')
    team_country = team.get('country', '')
    
    if not team_name:
        continue
    
    team_name_lower = team_name.lower()
    
    # Guardar en teams por ID
    database['teams'][team_id_str] = {
        'id': team_id,
        'name': team_name,
        'country': team_country,
        'code': team.get('code', ''),
        'founded': team.get('founded', 0),
        'logo': team.get('logo', '')
    }
    
    # Guardar en índices por nombre
    database['indexes']['by_name'][team_name_lower] = team_id_str
    
    # Guardar variantes (sin espacios)
    if ' ' in team_name_lower:
        no_spaces = team_name_lower.replace(' ', '')
        database['indexes']['by_name'][no_spaces] = team_id_str
    
    # Guardar primera palabra para búsquedas parciales
    first_word = team_name_lower.split()[0] if ' ' in team_name_lower else team_name_lower
    if first_word not in database['indexes']['by_name']:
        database['indexes']['by_name'][first_word] = team_id_str

print(f"✅ Índices creados: {len(database['indexes']['by_name'])} entradas")

# Guardar archivo final
output_file = "data/teams_database_final.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(database, f, indent=2, ensure_ascii=False)

print(f"✅ Archivo guardado: {output_file}")

# Reemplazar el archivo que usa TeamDatabase
if os.path.exists("data/teams_database.json"):
    os.rename("data/teams_database.json", "data/teams_database_old2.json")

os.rename(output_file, "data/teams_database.json")

print("\n📁 Archivos:")
print(f"  - Nueva base: data/teams_database.json")

# Probar con TeamDatabase
print("\n🔍 Probando con TeamDatabase:")
from modules.team_database import TeamDatabase

db = TeamDatabase('data/teams_database.json')

# Lista de equipos a probar
test_teams = [
    'Tottenham', 'Arsenal', 'Real Madrid', 'Barcelona', 
    'Bayern', 'Liverpool', 'Manchester United',
    'Cienciano', 'Melgar', 'Bucaramanga'
]

print("\n🔍 Buscando equipos:")
for team in test_teams:
    team_id = db.get_team_id(team)
    if team_id:
        # Intentar obtener más información
        team_info = database['teams'].get(str(team_id), {})
        country = team_info.get('country', 'desconocido')
        print(f"  ✅ {team}: ID {team_id} ({country})")
    else:
        # Búsqueda flexible
        found = False
        for key in database['indexes']['by_name']:
            if team.lower() in key:
                team_id = database['indexes']['by_name'][key]
                team_info = database['teams'].get(str(team_id), {})
                print(f"  ⚠️ {team}: Posible match -> {team_info.get('name', '')} (ID {team_id})")
                found = True
                break
        if not found:
            print(f"  ❌ {team}: No encontrado")

# Verificar estadísticas
print(f"\n📊 Estadísticas finales:")
print(f"  - Total equipos: {database['total_teams']}")
print(f"  - Total índices: {len(database['indexes']['by_name'])}")
print(f"  - Países disponibles: {len(set(t.get('country', '') for t in database['teams'].values()))}")
