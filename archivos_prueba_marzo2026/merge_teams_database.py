#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fusionar la base de datos sudamericana con la europea
"""
import json
import os

print("🔍 FUSIONANDO BASES DE DATOS DE EQUIPOS")
print("=" * 60)

# Cargar archivo original (sudamérica)
original_file = "data/teams_database.json"
if not os.path.exists(original_file):
    print(f"❌ No se encuentra {original_file}")
    exit(1)

with open(original_file, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

print(f"📊 Archivo original: {len(original_data)} equipos")

# Cargar archivo europeo
europe_file = "data/teams_database_europe.json"
if not os.path.exists(europe_file):
    print(f"❌ No se encuentra {europe_file}")
    exit(1)

with open(europe_file, 'r', encoding='utf-8') as f:
    europe_data = json.load(f)

print(f"📊 Archivo europeo: {len(europe_data)} equipos")

# Filtrar solo los diccionarios válidos
print("\n🔍 Limpiando datos...")
original_valid = [item for item in original_data if isinstance(item, dict)]
europe_valid = [item for item in europe_data if isinstance(item, dict)]

print(f"✅ Original: {len(original_valid)}/{len(original_data)} son diccionarios")
print(f"✅ Europeo: {len(europe_valid)}/{len(europe_data)} son diccionarios")

# Crear conjunto de IDs existentes
existing_ids = set()
for team in original_valid:
    if 'id' in team:
        existing_ids.add(team['id'])

# Añadir equipos europeos nuevos
new_teams = []
for team in europe_valid:
    if 'id' in team and team['id'] not in existing_ids:
        new_teams.append(team)
        existing_ids.add(team['id'])

print(f"\n📊 Equipos nuevos a añadir: {len(new_teams)}")

# Combinar
combined = original_valid + new_teams

# Guardar resultado
output_file = "data/teams_database_complete.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

print(f"\n✅ Archivo combinado guardado: {output_file}")
print(f"📊 Total equipos: {len(combined)}")
print(f"   - Original: {len(original_valid)}")
print(f"   - Europeos nuevos: {len(new_teams)}")

# Mostrar algunos equipos como ejemplo
print("\n🏆 Ejemplos de equipos en base combinada:")
for i, team in enumerate(combined[:15]):
    print(f"  {i+1}. {team.get('name', 'N/A')} ({team.get('country', 'N/A')})")

# Opcional: Reemplazar el archivo original
respuesta = input("\n¿Reemplazar teams_database.json con la versión combinada? (s/n): ")
if respuesta.lower() == 's':
    with open(original_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"✅ Archivo original actualizado: {original_file}")
