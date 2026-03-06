#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir la base de datos al formato correcto
"""
import json

print("🔍 CONVIRTIENDO BASE DE DATOS AL FORMATO CORRECTO")
print("=" * 60)

# Cargar archivo
input_file = "data/teams_database_complete.json"
with open(input_file, 'r', encoding='utf-8') as f:
    teams = json.load(f)

print(f"📊 Total equipos: {len(teams)}")

# Crear diccionario con el formato esperado
# El formato esperado es: { "team_name": { "id": 123, "country": "..." } }
database_dict = {}

for team in teams:
    if isinstance(team, dict):
        team_name = team.get('name', '')
        team_id = team.get('id', '')
        team_country = team.get('country', '')
        
        if team_name and team_id:
            # Guardar por nombre exacto
            database_dict[team_name] = {
                'id': team_id,
                'country': team_country,
                'name': team_name
            }
            
            # También guardar versiones en minúsculas para búsqueda flexible
            database_dict[team_name.lower()] = {
                'id': team_id,
                'country': team_country,
                'name': team_name
            }

print(f"✅ Diccionario creado con {len(database_dict)} entradas")

# Guardar en formato correcto
output_file = "data/teams_database_fixed.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(database_dict, f, indent=2, ensure_ascii=False)

print(f"✅ Archivo guardado: {output_file}")

# Reemplazar el original
import os
os.rename("data/teams_database.json", "data/teams_database_backup.json")
os.rename(output_file, "data/teams_database.json")

print("\n📁 Archivos:")
print(f"  - Original respaldado: data/teams_database_backup.json")
print(f"  - Nuevo formato: data/teams_database.json")

# Verificar que funciona
print("\n🔍 Verificando búsquedas:")
test_teams = ['Tottenham', 'Arsenal', 'Real Madrid', 'Barcelona', 'Bayern', 'Liverpool']

with open("data/teams_database.json", 'r', encoding='utf-8') as f:
    db = json.load(f)

for team in test_teams:
    # Buscar por nombre exacto
    if team in db:
        print(f"  ✅ {team}: ID {db[team]['id']} ({db[team]['country']})")
    # Buscar por minúsculas
    elif team.lower() in db:
        print(f"  ✅ {team}: ID {db[team.lower()]['id']} ({db[team.lower()]['country']})")
    else:
        # Búsqueda parcial
        found = False
        for key in db:
            if team.lower() in key.lower():
                print(f"  ⚠️ {team}: Posible match -> {key} (ID {db[key]['id']})")
                found = True
                break
        if not found:
            print(f"  ❌ {team}: No encontrado")
