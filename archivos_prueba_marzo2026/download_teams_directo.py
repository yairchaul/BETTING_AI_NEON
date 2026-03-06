# -*- coding: utf-8 -*-
"""
Script para descargar la base de datos completa de equipos
Versión DIRECTA - usa la API key manualmente
"""
import requests
import json
import os
import time
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN - PON TU API KEY AQUÍ
# =============================================================================
FOOTBALL_API_KEY = "ddec28ffdbfdd1dd97a04613e390abf8"  # Tu API key actual
# =============================================================================

class TeamDownloaderDirecto:
    def __init__(self, api_key, data_file='data/teams_database.json'):
        self.api_key = api_key
        self.data_file = data_file
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {'x-apisports-key': api_key}
        self.last_request_time = 0
        self.request_interval = 0.5
        
    def _rate_limit(self):
        now = time.time()
        if now - self.last_request_time < self.request_interval:
            time.sleep(self.request_interval - (now - self.last_request_time))
        self.last_request_time = now
    
    def get_countries(self):
        self._rate_limit()
        try:
            url = f"{self.base_url}/countries"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                print(f"❌ Error obteniendo países: {response.status_code}")
                print(response.text[:200])
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_teams_by_country(self, country):
        self._rate_limit()
        try:
            url = f"{self.base_url}/teams"
            params = {"country": country}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                return []
        except:
            return []
    
    def download_all_teams(self):
        print("🔍 DESCARGANDO BASE DE DATOS DE EQUIPOS")
        print("=" * 60)
        print(f"📡 API Key: {self.api_key[:5]}...{self.api_key[-5:]}")
        print()
        
        # 1. Verificar que la API funciona
        print("📡 Verificando conexión...")
        test_countries = self.get_countries()
        if not test_countries:
            print("❌ No se pudo conectar a la API. Verifica tu API key.")
            return None
        print(f"✅ Conexión exitosa. {len(test_countries)} países disponibles.\n")
        
        # 2. Obtener países más importantes primero
        paises_prioritarios = [
            'Mexico', 'Argentina', 'Brazil', 'Chile', 'Colombia', 'Peru', 'Uruguay',
            'Ecuador', 'Paraguay', 'Bolivia', 'Venezuela', 'USA', 'Canada',
            'Spain', 'England', 'Italy', 'Germany', 'France', 'Portugal',
            'Netherlands', 'Belgium', 'Turkey', 'Greece', 'Russia'
        ]
        
        all_teams = []
        procesados = set()
        
        for i, pais in enumerate(paises_prioritarios, 1):
            print(f"📡 [{i}/{len(paises_prioritarios)}] Procesando {pais}...")
            teams_data = self.get_teams_by_country(pais)
            
            for team_data in teams_data:
                team = team_data['team']
                team_info = {
                    'id': team['id'],
                    'name': team['name'],
                    'country': pais,
                    'code': team.get('code', ''),
                    'founded': team.get('founded', 0)
                }
                all_teams.append(team_info)
                procesados.add(team['name'])
            
            print(f"   → {len(teams_data)} equipos encontrados")
            time.sleep(0.5)
        
        # 3. Crear índices
        print("\n📊 Creando índices...")
        name_index = {}
        for team in all_teams:
            normalized = team['name'].lower().strip()
            name_index[normalized] = team['id']
            
            # Versiones sin acentos
            unaccented = (normalized.replace('á', 'a').replace('é', 'e')
                                    .replace('í', 'i').replace('ó', 'o')
                                    .replace('ú', 'u').replace('ü', 'u')
                                    .replace('ñ', 'n'))
            if unaccented != normalized:
                name_index[unaccented] = team['id']
        
        country_index = {}
        for team in all_teams:
            country = team['country']
            if country not in country_index:
                country_index[country] = []
            country_index[country].append(team['id'])
        
        # 4. Guardar
        database = {
            'last_update': datetime.now().isoformat(),
            'total_teams': len(all_teams),
            'teams': all_teams,
            'indexes': {
                'by_name': name_index,
                'by_country': country_index
            }
        }
        
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print(f"✅ DESCARGA COMPLETADA")
        print(f"📁 Archivo guardado: {self.data_file}")
        print(f"📊 Total equipos: {len(all_teams)}")
        print(f"🌍 Países procesados: {len(paises_prioritarios)}")
        
        return database

# =============================================================================
# EJECUTAR
# =============================================================================
if __name__ == "__main__":
    if not FOOTBALL_API_KEY:
        print("❌ ERROR: Debes poner tu API key en el script")
        print("   Edita la línea: FOOTBALL_API_KEY = 'tu_key_aqui'")
    else:
        downloader = TeamDownloaderDirecto(FOOTBALL_API_KEY)
        downloader.download_all_teams()
