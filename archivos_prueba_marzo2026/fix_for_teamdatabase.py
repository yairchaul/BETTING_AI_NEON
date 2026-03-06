#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir la base de datos al formato exacto que espera TeamDatabase
"""
import json

print("🔍 CONVIRTIENDO BASE DE DATOS PARA TEAMDATABASE")
print("=" * 60)

# Cargar archivo original (el que tiene 14385 entradas)
input_file = "data/teams_database.json"
with open(input_file, 'r', encoding='utf-8') as f:
    db_dict = json.load(f)

print(f"📊 Total entradas en diccionario: {len(db_dict)}")

# Extraer equipos únicos (sin duplicados por minúsculas)
unique_teams = {}
for key, value in db_dict.items():
    team_id = value.get('id')
    if team_id not in unique_teams:
        unique_teams[team_id] = {
            'id': team_id,
            'name': value.get('name', ''),
            'country': value.get('country', ''),
            'code': '',
            'founded': 0,
            'logo': ''
        }

print(f"✅ Equipos únicos: {len(unique_teams)}")

# Convertir a lista (formato que probablemente espera TeamDatabase)
teams_list = list(unique_teams.values())

print(f"\n📋 Primeros 10 equipos:")
for i, team in enumerate(teams_list[:10]):
    print(f"  {i+1}. {team['name']} (ID: {team['id']}, {team['country']})")

# Guardar en formato lista
output_file = "data/teams_database_list.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(teams_list, f, indent=2, ensure_ascii=False)

print(f"\n✅ Archivo guardado: {output_file}")

# Reemplazar el archivo que usa TeamDatabase
import os
os.rename("data/teams_database.json", "data/teams_database_dict_backup.json")
os.rename(output_file, "data/teams_database.json")

print(f"\n📁 Archivos:")
print(f"  - Backup del diccionario: data/teams_database_dict_backup.json")
print(f"  - Nueva lista: data/teams_database.json")

# Probar con TeamDatabase
print("\n🔍 Probando con TeamDatabase:")
from modules.team_database import TeamDatabase

db = TeamDatabase('data/teams_database.json')
print(f"✅ Base de datos cargada: {len(db.teams) if hasattr(db, 'teams') else 'desconocido'} equipos")

test_teams = ['Tottenham', 'Arsenal', 'Real Madrid', 'Barcelona', 'Bayern', 'Liverpool', 'Cienciano', 'Melgar']
print("\n🔍 Buscando equipos:")
for team in test_teams:
    team_id = db.get_team_id(team)
    if team_id:
        print(f"  ✅ {team}: ID {team_id}")
    else:
        print(f"  ❌ {team}: No encontrado")
