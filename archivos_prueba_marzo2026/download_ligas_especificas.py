#!/usr/bin/env python3
"""
Descargar equipos de ligas específicas (más eficiente)
"""
import requests
import json
import time
from pathlib import Path

API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"
headers = {'x-apisports-key': API_KEY}

# Ligas que nos interesan con sus IDs
LIGAS = [
    (39, "Premier League", "England"),
    (140, "LaLiga", "Spain"),
    (135, "Serie A", "Italy"),
    (78, "Bundesliga", "Germany"),
    (61, "Ligue 1", "France"),
    (88, "Eredivisie", "Netherlands"),
    (94, "Primeira Liga", "Portugal"),
    (144, "Jupiler Pro League", "Belgium"),
    (203, "Süper Lig", "Turkey"),
    (179, "Premiership", "Scotland"),
    (119, "Superliga", "Denmark"),
    (113, "Allsvenskan", "Sweden"),
    (103, "Eliteserien", "Norway"),
]

print("🔍 DESCARGANDO EQUIPOS POR LIGAS ESPECÍFICAS")
print("=" * 60)

all_teams = []
total_requests = 0

for liga_id, liga_nombre, pais in LIGAS:
    print(f"\n📡 [{liga_nombre}]")
    
    # Obtener equipos de la liga
    url = f"{BASE_URL}/teams"
    params = {'league': liga_id, 'season': 2025}
    
    response = requests.get(url, headers=headers, params=params)
    total_requests += 1
    
    if response.status_code == 200:
        data = response.json()
        
        # La API puede devolver lista o dict con 'response'
        equipos = data if isinstance(data, list) else data.get('response', [])
        
        print(f"   → {len(equipos)} equipos encontrados")
        
        for item in equipos:
            # Extraer equipo según formato
            if isinstance(item, dict):
                team = item.get('team', item)  # Algunos formatos tienen 'team' anidado
                team_info = {
                    'id': team.get('id'),
                    'name': team.get('name'),
                    'country': pais,
                    'code': team.get('code', ''),
                    'founded': team.get('founded', 0),
                    'logo': team.get('logo', '')
                }
                if team_info['id'] and team_info['name']:
                    all_teams.append(team_info)
        
        time.sleep(1)  # Pausa para no saturar la API
    else:
        print(f"   ❌ Error {response.status_code}")

print(f"\n✅ Total equipos descargados: {len(all_teams)}")

# Guardar en formato compatible con TeamDatabase
database = {
    "total_teams": len(all_teams),
    "indexes": {"by_name": {}},
    "teams": {}
}

for team in all_teams:
    team_id = str(team['id'])
    team_name = team['name']
    
    database['teams'][team_id] = team
    database['indexes']['by_name'][team_name.lower()] = team_id
    
    # Versión sin espacios
    if ' ' in team_name.lower():
        database['indexes']['by_name'][team_name.lower().replace(' ', '')] = team_id

# Guardar archivo
output_file = "data/teams_database_completa.json"
Path("data").mkdir(exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(database, f, indent=2)

print(f"\n✅ Base de datos guardada: {output_file}")
print(f"📊 Total equipos: {database['total_teams']}")
print(f"📊 Total índices: {len(database['indexes']['by_name'])}")

# Hacer backup del archivo actual
import os
if os.path.exists("data/teams_database.json"):
    os.rename("data/teams_database.json", "data/teams_database_backup.json")
    print("✅ Backup creado: data/teams_database_backup.json")

# Usar el nuevo archivo
os.rename(output_file, "data/teams_database.json")
print("✅ Nueva base de datos activada: data/teams_database.json")
