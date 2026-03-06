#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear la base de datos en el formato exacto que espera TeamDatabase
"""
import json

print("🔍 CREANDO BASE DE DATOS EN FORMATO CORRECTO")
print("=" * 60)

# Cargar la lista de equipos que ya tenemos
input_file = "data/teams_database_list.json"
with open(input_file, 'r', encoding='utf-8') as f:
    teams_list = json.load(f)

print(f"📊 Total equipos: {len(teams_list)}")

# Crear la estructura esperada por TeamDatabase
database = {
    "total_teams": len(teams_list),
    "indexes": {
        "by_name": {}
    },
    "teams": {}
}

# Llenar la estructura
for team in teams_list:
    team_id = str(team['id'])
    team_name = team['name']
    team_name_lower = team_name.lower()
    
    # Guardar en teams por ID
    database['teams'][team_id] = team
    
    # Guardar en índices por nombre (normalizado)
    database['indexes']['by_name'][team_name_lower] = team_id
    
    # También guardar variantes comunes
    if ' ' in team_name:
        # Para equipos con espacios, guardar también sin espacios
        no_spaces = team_name_lower.replace(' ', '')
        database['indexes']['by_name'][no_spaces] = team_id
    
    # Para nombres como "Bayern München", guardar también "Bayern"
    if ' ' in team_name:
        first_word = team_name_lower.split()[0]
        if first_word not in database['indexes']['by_name']:
            database['indexes']['by_name'][first_word] = team_id

print(f"✅ Índices creados: {len(database['indexes']['by_name'])} entradas")

# Guardar archivo
output_file = "data/teams_database_final.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(database, f, indent=2, ensure_ascii=False)

print(f"✅ Archivo guardado: {output_file}")

# Reemplazar el archivo que usa TeamDatabase
import os
os.rename("data/teams_database.json", "data/teams_database_old.json")
os.rename(output_file, "data/teams_database.json")

print("\n📁 Archivos:")
print(f"  - Backup: data/teams_database_old.json")
print(f"  - Nueva base: data/teams_database.json")

# Probar con TeamDatabase
print("\n🔍 Probando con TeamDatabase:")
from modules.team_database import TeamDatabase

db = TeamDatabase('data/teams_database.json')

test_teams = ['Tottenham', 'Arsenal', 'Real Madrid', 'Barcelona', 'Bayern', 'Liverpool', 'Cienciano', 'Melgar']
print("\n🔍 Buscando equipos:")
for team in test_teams:
    team_id = db.get_team_id(team)
    if team_id:
        print(f"  ✅ {team}: ID {team_id}")
    else:
        print(f"  ❌ {team}: No encontrado")
