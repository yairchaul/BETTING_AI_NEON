#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar equipos europeos usando TeamDownloader (versión corregida)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from modules.team_downloader import TeamDownloader

# NUEVA API KEY
API_KEY = "11eaff423a9042393b1fe21512384884"

# Países europeos con nombres exactos (según API-Football)
EUROPEAN_COUNTRIES = [
    "England", "Spain", "Italy", "Germany", "France",
    "Portugal", "Netherlands", "Belgium", "Turkey",
    "Greece", "Russia", "Switzerland", "Austria",
    "Sweden", "Norway", "Denmark", "Scotland", "Poland",
    "Ukraine", "Croatia", "Czech-Republic", "Romania",
    "Hungary", "Serbia", "Bulgaria", "Slovakia", "Slovenia",
    "Finland", "Iceland", "Ireland", "Wales", "Northern-Ireland"
]

print("🔍 DESCARGANDO EQUIPOS EUROPEOS (usando TeamDownloader)")
print("=" * 60)
print(f"📡 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")

# Crear el descargador
downloader = TeamDownloader(api_key=API_KEY, data_file='data/teams_database_europe.json')

# Primero, obtener todos los países disponibles para verificar
print("\n📡 Obteniendo lista de países disponibles...")
paises_disponibles = downloader.get_countries()
if paises_disponibles:
    print(f"✅ {len(paises_disponibles)} países disponibles")
    # Mostrar algunos ejemplos
    print("   Ejemplos:", [c['name'] for c in paises_disponibles[:10]])
else:
    print("⚠️ No se pudo obtener la lista de países")

# Descargar equipos europeos
all_teams = []
paises_encontrados = []

print("\n📡 Descargando equipos por país...")

for country in EUROPEAN_COUNTRIES:
    print(f"\n📍 Procesando {country}...")
    
    # Usar el método correcto: get_teams_by_country
    teams_data = downloader.get_teams_by_country(country)
    
    if teams_data and teams_data.get('teams'):
        teams_list = teams_data['teams']
        print(f"   → {len(teams_list)} equipos encontrados")
        all_teams.extend(teams_list)
        paises_encontrados.append(country)
        
        # Mostrar primeros 3 equipos como ejemplo
        for i, team in enumerate(teams_list[:3]):
            print(f"     {i+1}. {team.get('name', 'N/A')}")
    else:
        print(f"   → 0 equipos encontrados")

# Guardar resultados
output_file = "data/teams_database_europe.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_teams, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("✅ DESCARGA COMPLETADA")
print(f"📁 Archivo guardado: {output_file}")
print(f"📊 Total equipos europeos: {len(all_teams)}")
print(f"🌍 Países con equipos: {len(paises_encontrados)}/{len(EUROPEAN_COUNTRIES)}")
if paises_encontrados:
    print("📋 Países encontrados:", ", ".join(paises_encontrados[:10]))

# Opcional: Actualizar el archivo principal
main_file = "data/teams_database.json"
if os.path.exists(main_file) and all_teams:
    with open(main_file, 'r', encoding='utf-8') as f:
        main_teams = json.load(f)
    
    # Combinar evitando duplicados por ID
    existing_ids = {t['id'] for t in main_teams if 'id' in t}
    new_teams = [t for t in all_teams if t.get('id') not in existing_ids]
    
    if new_teams:
        main_teams.extend(new_teams)
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(main_teams, f, indent=2, ensure_ascii=False)
        print(f"\n📊 Archivo principal actualizado: +{len(new_teams)} equipos nuevos")
