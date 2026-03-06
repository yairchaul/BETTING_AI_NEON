#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar equipos europeos usando TeamDownloader (versión final)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from modules.team_downloader import TeamDownloader

# NUEVA API KEY
API_KEY = "11eaff423a9042393b1fe21512384884"

# Países europeos
EUROPEAN_COUNTRIES = [
    "England", "Spain", "Italy", "Germany", "France",
    "Portugal", "Netherlands", "Belgium", "Turkey",
    "Greece", "Russia", "Switzerland", "Austria",
    "Sweden", "Norway", "Denmark", "Scotland", "Poland",
    "Ukraine", "Croatia", "Czech-Republic", "Romania",
    "Hungary", "Serbia"
]

print("🔍 DESCARGANDO EQUIPOS EUROPEOS")
print("=" * 60)
print(f"📡 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")

# Crear el descargador
downloader = TeamDownloader(api_key=API_KEY, data_file='data/teams_database_europe.json')

# Obtener lista de países disponibles
print("\n📡 Obteniendo lista de países disponibles...")
paises_disponibles = downloader.get_countries()
if paises_disponibles:
    print(f"✅ {len(paises_disponibles)} países disponibles")
    print("   Ejemplos:", paises_disponibles[:10])
    
    # Verificar qué países europeos están disponibles
    disponibles_en_europa = [p for p in EUROPEAN_COUNTRIES if p in paises_disponibles]
    no_disponibles = [p for p in EUROPEAN_COUNTRIES if p not in paises_disponibles]
    
    print(f"\n📊 Países europeos en API: {len(disponibles_en_europa)}/{len(EUROPEAN_COUNTRIES)}")
    if disponibles_en_europa:
        print("   ✅ Disponibles:", ", ".join(disponibles_en_europa[:10]))
    if no_disponibles:
        print("   ❌ No disponibles:", ", ".join(no_disponibles[:10]))
else:
    print("⚠️ No se pudo obtener la lista de países")

# Descargar equipos
all_teams = []
paises_con_equipos = []

print("\n📡 Descargando equipos por país...")

for country in EUROPEAN_COUNTRIES:
    print(f"\n📍 Procesando {country}...")
    
    teams_data = downloader.get_teams_by_country(country)
    
    # Verificar la estructura de teams_data
    if teams_data:
        if isinstance(teams_data, dict) and teams_data.get('teams'):
            teams_list = teams_data['teams']
            print(f"   → {len(teams_list)} equipos encontrados")
            all_teams.extend(teams_list)
            paises_con_equipos.append(country)
            
            # Mostrar algunos equipos
            for i, team in enumerate(teams_list[:3]):
                print(f"     {i+1}. {team.get('name', 'N/A')}")
        elif isinstance(teams_data, list):
            # Si es una lista directamente
            print(f"   → {len(teams_data)} equipos encontrados (formato lista)")
            all_teams.extend(teams_data)
            paises_con_equipos.append(country)
        else:
            print(f"   → Formato inesperado: {type(teams_data)}")
    else:
        print(f"   → No se encontraron equipos")

# Guardar resultados
output_file = "data/teams_database_europe.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_teams, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("✅ DESCARGA COMPLETADA")
print(f"📁 Archivo guardado: {output_file}")
print(f"📊 Total equipos europeos: {len(all_teams)}")
print(f"🌍 Países con equipos: {len(paises_con_equipos)}/{len(EUROPEAN_COUNTRIES)}")

if paises_con_equipos:
    print("\n📋 Países con equipos encontrados:")
    for pais in paises_con_equipos:
        print(f"  - {pais}")

# Mostrar algunos equipos como ejemplo
if all_teams:
    print("\n🏆 Ejemplos de equipos descargados:")
    for i, team in enumerate(all_teams[:10]):
        print(f"  {i+1}. {team.get('name', 'N/A')} ({team.get('country', 'N/A')})")

# Actualizar archivo principal
main_file = "data/teams_database.json"
if os.path.exists(main_file) and all_teams:
    with open(main_file, 'r', encoding='utf-8') as f:
        main_teams = json.load(f)
    
    # Combinar evitando duplicados
    existing_ids = {t.get('id') for t in main_teams if t.get('id')}
    new_teams = [t for t in all_teams if t.get('id') not in existing_ids]
    
    if new_teams:
        main_teams.extend(new_teams)
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(main_teams, f, indent=2, ensure_ascii=False)
        print(f"\n📊 Archivo principal actualizado: +{len(new_teams)} equipos nuevos")
        print(f"📊 Total equipos ahora: {len(main_teams)}")
