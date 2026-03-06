#!/usr/bin/env python3
"""
Buscar partidos en 2026 (para probar)
"""
import requests
from datetime import datetime, timedelta

API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"
headers = {'x-apisports-key': API_KEY}

# Probar diferentes fechas de 2026
fechas = [
    "2026-03-15",  # Mediados de Marzo 2026
    "2026-04-01",
    "2026-05-20",
    "2026-08-15",  # Inicio de temporadas europeas
    "2026-09-01",
]

ligas = [
    (140, "LaLiga"),
    (39, "Premier League"),
    (262, "Liga MX"),
    (253, "MLS"),
]

for fecha in fechas:
    print(f"\n{'='*60}")
    print(f"📅 FECHA: {fecha}")
    print('='*60)
    
    for liga_id, liga_nombre in ligas:
        url = f"{BASE_URL}/fixtures"
        params = {
            'league': liga_id,
            'season': 2026,
            'date': fecha,
            'timezone': 'America/Mexico_City'
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            partidos = data.get('response', [])
            print(f"\n{liga_nombre}: {len(partidos)} partidos")
            
            for partido in partidos[:3]:
                local = partido['teams']['home']['name']
                visitante = partido['teams']['away']['name']
                hora = partido['fixture']['date'][11:16]
                print(f"  {hora} - {local} vs {visitante}")
        else:
            print(f"\n{liga_nombre}: Error {response.status_code}")
