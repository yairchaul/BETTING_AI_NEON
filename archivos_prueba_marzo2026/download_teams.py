# -*- coding: utf-8 -*-
"""
Script para descargar la base de datos completa de equipos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from modules.team_downloader import TeamDownloader

print("=" * 60)
print("🔍 DESCARGADOR DE BASE DE DATOS DE EQUIPOS")
print("=" * 60)

# Cargar API key desde secrets
try:
    api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    if not api_key:
        print("❌ No se encontró FOOTBALL_API_KEY en secrets.toml")
        print("   Asegúrate de tener el archivo .streamlit/secrets.toml con la key")
        sys.exit(1)
    print(f"✅ API Key encontrada: {api_key[:5]}...{api_key[-5:]}")
except Exception as e:
    print(f"❌ Error cargando secrets: {e}")
    sys.exit(1)

# Crear el descargador
downloader = TeamDownloader(api_key=api_key, data_file='data/teams_database.json')

# Preguntar si proceder
print("\n⚠️  Este proceso descargará TODOS los equipos de TODOS los países.")
print(f"   Puede tomar varios minutos y consumirá ~{231} llamadas a la API.")
print("   Aprox: 1 minuto por cada 20 países (total ~230 países)\n")

respuesta = input("¿Continuar con la descarga? (s/n): ")
if respuesta.lower() == 's':
    database = downloader.download_all_teams()
    
    if database:
        print("\n📊 Verificando equipos sudamericanos...")
        equipos_sudamerica = [
            'Cienciano', 'Melgar', 'Orense SC', 'Macara',
            'America de Cali', 'Bucaramanga', 'Millonarios',
            'River Plate', 'Racing', 'San Lorenzo'
        ]
        
        for equipo in equipos_sudamerica:
            team_id = downloader.get_team_id(equipo, database)
            if team_id:
                print(f"   ✅ {equipo}: ID {team_id}")
            else:
                print(f"   ❌ {equipo}: No encontrado")
else:
    print("❌ Descarga cancelada")

print("\n" + "=" * 60)
