#!/usr/bin/env python3
"""
Convertir la base de datos de lista a diccionario con índices
"""
import json

print("🔧 CONVIRTIENDO BASE DE DATOS...")
print("=" * 60)

# Cargar archivo actual (lista)
with open('data/teams_database.json', 'r') as f:
    teams_list = json.load(f)

print(f"📊 Equipos en lista: {len(teams_list)}")

# Crear nueva estructura
new_database = {
    "total_teams": len(teams_list),
    "indexes": {
        "by_name": {}
    },
    "teams": {}
}

# Procesar cada equipo
paises = set()
for team in teams_list:
    if isinstance(team, dict):
        team_id = str(team.get('id', ''))
        team_name = team.get('name', '')
        team_country = team.get('country', '')
        
        if team_id and team_name:
            # Guardar en teams por ID
            new_database['teams'][team_id] = team
            
            # Guardar en índices por nombre (minúsculas)
            name_lower = team_name.lower()
            new_database['indexes']['by_name'][name_lower] = team_id
            
            # Guardar también sin espacios para búsquedas flexibles
            if ' ' in name_lower:
                no_spaces = name_lower.replace(' ', '')
                new_database['indexes']['by_name'][no_spaces] = team_id
            
            # Guardar país
            if team_country:
                paises.add(team_country)

print(f"✅ Nuevo formato creado:")
print(f"   - Equipos: {len(new_database['teams'])}")
print(f"   - Índices: {len(new_database['indexes']['by_name'])}")
print(f"   - Países: {len(paises)}")

# Guardar backup del original
import os
os.rename('data/teams_database.json', 'data/teams_database_backup_list.json')

# Guardar nuevo formato
with open('data/teams_database.json', 'w') as f:
    json.dump(new_database, f, indent=2)

print(f"\n✅ Archivo convertido: data/teams_database.json")
print(f"✅ Backup guardado: data/teams_database_backup_list.json")

# Mostrar algunos países como ejemplo
print(f"\n🌍 Primeros 20 países:")
for i, pais in enumerate(sorted(paises)[:20]):
    print(f"  {i+1}. {pais}")
