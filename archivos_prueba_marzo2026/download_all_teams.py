#!/usr/bin/env python3
"""
Script para descargar equipos de Sudamérica y Europa
"""
import json
import time
import requests
from pathlib import Path

API_KEY = "ddec28ffdbfdd1dd97a04613e390abf8"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    'x-apisports-key': API_KEY,
    'x-apisports-host': 'v3.football.api-sports.io'
}

# Todos los países
COUNTRIES = [
    # Sudamérica
    "Mexico", "Argentina", "Brazil", "Chile", "Colombia", 
    "Peru", "Uruguay", "Ecuador", "Paraguay", "Bolivia", "Venezuela",
    # Europa
    "England", "Spain", "Italy", "Germany", "France", 
    "Portugal", "Netherlands", "Belgium", "Turkey", 
    "Greece", "Russia", "Switzerland", "Austria", 
    "Sweden", "Norway", "Denmark", "Scotland", "Poland",
    "Ukraine", "Croatia", "Czech-Republic", "Romania"
]

def get_teams_by_country(country):
    """Obtener equipos de un país específico"""
    try:
        url = f"{BASE_URL}/teams"
        params = {
            'country': country,
            'limit': 1000
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                teams = []
                for item in data['response']:
                    team = item['team']
                    teams.append({
                        'id': team['id'],
                        'name': team['name'],
                        'country': country,
                        'code': team.get('code', ''),
                        'founded': team.get('founded', 0),
                        'logo': team.get('logo', '')
                    })
                return teams
        return []
    except Exception as e:
        print(f"  Error: {e}")
        return []

def main():
    print("🔍 DESCARGANDO BASE DE DATOS COMPLETA DE EQUIPOS")
    print("=" * 60)
    print(f"📡 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    
    # Verificar conexión
    try:
        test_response = requests.get(f"{BASE_URL}/status", headers=headers)
        if test_response.status_code == 200:
            print("✅ Conexión exitosa")
        else:
            print("❌ Error de conexión")
            return
    except:
        print("❌ No se pudo conectar")
        return
    
    all_teams = []
    
    for i, country in enumerate(COUNTRIES, 1):
        print(f"\n📡 [{i}/{len(COUNTRIES)}] Procesando {country}...")
        
        teams = get_teams_by_country(country)
        if teams:
            print(f"   → {len(teams)} equipos encontrados")
            all_teams.extend(teams)
        else:
            print(f"   → 0 equipos encontrados")
        
        time.sleep(1)  # Pausa para no sobrecargar la API
    
    # Guardar resultados
    output_file = Path("data/teams_database_complete.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_teams, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ DESCARGA COMPLETADA")
    print(f"📁 Archivo guardado: {output_file}")
    print(f"📊 Total equipos: {len(all_teams)}")
    print(f"🌍 Países procesados: {len(COUNTRIES)}")

if __name__ == "__main__":
    main()
