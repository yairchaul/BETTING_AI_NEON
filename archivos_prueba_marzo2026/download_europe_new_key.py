#!/usr/bin/env python3
"""
Script para descargar equipos europeos con la nueva API key
"""
import json
import time
import requests
from pathlib import Path

# NUEVA API KEY
API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    'x-apisports-key': API_KEY,
    'x-apisports-host': 'v3.football.api-sports.io'
}

# Países europeos principales
EUROPEAN_COUNTRIES = [
    "England", "Spain", "Italy", "Germany", "France",
    "Portugal", "Netherlands", "Belgium", "Turkey",
    "Greece", "Russia", "Switzerland", "Austria",
    "Sweden", "Norway", "Denmark", "Scotland", "Poland",
    "Ukraine", "Croatia", "Czech-Republic", "Romania"
]

def test_connection():
    """Probar conexión a la API"""
    try:
        response = requests.get(f"{BASE_URL}/status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa")
            print(f"📊 Requests hoy: {data.get('response', {}).get('requests', {}).get('current', 0)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_teams_by_country(country):
    """Obtener equipos de un país específico"""
    try:
        url = f"{BASE_URL}/teams"
        params = {'country': country, 'limit': 1000}
        
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
    print("🔍 DESCARGANDO EQUIPOS EUROPEOS (Nueva API Key)")
    print("=" * 60)
    print(f"📡 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    
    # Probar conexión primero
    if not test_connection():
        print("❌ No se puede continuar sin conexión a la API")
        return
    
    all_teams = []
    
    for i, country in enumerate(EUROPEAN_COUNTRIES, 1):
        print(f"\n📡 [{i}/{len(EUROPEAN_COUNTRIES)}] Procesando {country}...")
        
        teams = get_teams_by_country(country)
        if teams:
            print(f"   → {len(teams)} equipos encontrados")
            all_teams.extend(teams)
        else:
            print(f"   → 0 equipos encontrados")
        
        time.sleep(1)  # Pausa para no sobrecargar la API
    
    # Guardar resultados
    output_file = Path("data/teams_database_europe.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_teams, f, indent=2, ensure_ascii=False)
    
    # También actualizar el archivo principal si existe
    main_file = Path("data/teams_database.json")
    if main_file.exists():
        with open(main_file, 'r', encoding='utf-8') as f:
            main_teams = json.load(f)
        
        # Combinar (evitando duplicados por ID)
        existing_ids = {t['id'] for t in main_teams}
        new_teams = [t for t in all_teams if t['id'] not in existing_ids]
        main_teams.extend(new_teams)
        
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(main_teams, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Actualizado archivo principal: +{len(new_teams)} equipos nuevos")
    
    print("\n" + "=" * 60)
    print("✅ DESCARGA COMPLETADA")
    print(f"📁 Archivo guardado: {output_file}")
    print(f"📊 Total equipos europeos: {len(all_teams)}")
    print(f"🌍 Países procesados: {len(EUROPEAN_COUNTRIES)}")

if __name__ == "__main__":
    main()
