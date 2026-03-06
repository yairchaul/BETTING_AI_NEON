#!/usr/bin/env python3
"""
Descargar equipos de ligas específicas - VERSIÓN CORREGIDA
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

# Primero, obtener la temporada actual para cada liga
print("\n📡 Obteniendo temporadas actuales...")

temporadas_actuales = {}

for liga_id, liga_nombre, pais in LIGAS[:2]:  # Probamos con 2 ligas primero
    url = f"{BASE_URL}/leagues"
    params = {'id': liga_id}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('response'):
            liga_info = data['response'][0]
            seasons = liga_info.get('seasons', [])
            # Buscar la temporada actual
            for season in seasons:
                if season.get('current'):
                    temporadas_actuales[liga_id] = season.get('year')
                    print(f"   ✅ {liga_nombre}: Temporada {temporadas_actuales[liga_id]}")
                    break
            else:
                # Si no hay current, usar la última
                if seasons:
                    temporadas_actuales[liga_id] = seasons[-1].get('year')
                    print(f"   ⚠️ {liga_nombre}: Usando última temporada {temporadas_actuales[liga_id]}")
    time.sleep(1)

print("\n📡 Descargando equipos...")

all_teams = []

for liga_id, liga_nombre, pais in LIGAS:
    print(f"\n📡 [{liga_nombre}]")
    
    # Usar la temporada que encontramos o 2024 como fallback
    season = temporadas_actuales.get(liga_id, 2024)
    
    # Obtener equipos de la liga
    url = f"{BASE_URL}/teams"
    params = {'league': liga_id, 'season': season}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # La API devuelve {"response": [...]}
            equipos = data.get('response', [])
            
            print(f"   → Temporada {season}: {len(equipos)} equipos encontrados")
            
            for item in equipos:
                if isinstance(item, dict):
                    team = item.get('team', {})
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
                        print(f"     ✅ {team_info['name']}")
            
            time.sleep(1)  # Pausa para no saturar la API
        else:
            print(f"   ❌ Error {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

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
    
    # Versiones comunes
    if 'Manchester' in team_name:
        database['indexes']['by_name'][team_name.lower().replace(' ', '')] = team_id
    if 'Real Madrid' in team_name:
        database['indexes']['by_name']['realmadrid'] = team_id
    if 'Barcelona' in team_name:
        database['indexes']['by_name']['barca'] = team_id

# Guardar archivo
output_file = "data/teams_database_completa.json"
Path("data").mkdir(exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(database, f, indent=2)

print(f"\n✅ Base de datos guardada: {output_file}")
print(f"📊 Total equipos: {database['total_teams']}")
print(f"📊 Total índices: {len(database['indexes']['by_name'])}")

# Mostrar algunos equipos como ejemplo
print("\n🏆 Ejemplos de equipos descargados:")
for i, (team_id, team) in enumerate(list(database['teams'].items())[:10]):
    print(f"  {i+1}. {team['name']} (ID: {team_id}, {team['country']})")

# Hacer backup del archivo actual
import os
if os.path.exists("data/teams_database.json"):
    os.rename("data/teams_database.json", "data/teams_database_backup_antes.json")
    print("✅ Backup creado: data/teams_database_backup_antes.json")

# Usar el nuevo archivo
os.rename(output_file, "data/teams_database.json")
print("✅ Nueva base de datos activada: data/teams_database.json")
