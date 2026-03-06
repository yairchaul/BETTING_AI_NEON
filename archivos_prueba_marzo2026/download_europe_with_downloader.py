#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar equipos europeos usando TeamDownloader (que SÍ funciona)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from modules.team_downloader import TeamDownloader

# Países europeos principales
EUROPEAN_COUNTRIES = [
    "England", "Spain", "Italy", "Germany", "France",
    "Portugal", "Netherlands", "Belgium", "Turkey",
    "Greece", "Russia", "Switzerland", "Austria",
    "Sweden", "Norway", "Denmark", "Scotland", "Poland",
    "Ukraine", "Croatia", "Czech-Republic", "Romania"
]

print("🔍 DESCARGANDO EQUIPOS EUROPEOS (usando TeamDownloader)")
print("=" * 60)

# Usar la misma API key que funcionó
API_KEY = "ddec28ffdbfdd1dd97a04613e390abf8"
print(f"📡 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")

# Crear el descargador
downloader = TeamDownloader(api_key=API_KEY, data_file='data/teams_database_europe.json')

# Descargar equipos europeos
all_teams = []
for country in EUROPEAN_COUNTRIES:
    print(f"\n📡 Procesando {country}...")
    teams = downloader.download_teams_by_country(country)
    if teams:
        print(f"   → {len(teams)} equipos encontrados")
        all_teams.extend(teams)
    else:
        print(f"   → 0 equipos encontrados")

# Guardar resultados
with open('data/teams_database_europe.json', 'w', encoding='utf-8') as f:
    json.dump(all_teams, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print(f"✅ DESCARGA COMPLETADA")
print(f"📊 Total equipos europeos: {len(all_teams)}")
