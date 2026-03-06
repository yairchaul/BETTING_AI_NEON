#!/usr/bin/env python3
"""
Verificar qué temporadas están disponibles en la API
"""
import requests

API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"
headers = {'x-apisports-key': API_KEY}

print("🔍 VERIFICANDO TEMPORADAS DISPONIBLES PARA 2026")
print("=" * 60)

# Ver información de LaLiga
liga_id = 140
url = f"{BASE_URL}/leagues"
params = {'id': liga_id}

response = requests.get(url, headers=headers, params=params)
if response.status_code == 200:
    data = response.json()
    if data.get('response'):
        liga_info = data['response'][0]
        seasons = liga_info.get('seasons', [])
        
        print(f"\n📅 Temporadas disponibles para LaLiga:")
        ultimas_temporadas = seasons[-5:]  # Últimas 5
        for season in ultimas_temporadas:
            year = season.get('year')
            start = season.get('start')
            end = season.get('end')
            current = season.get('current', False)
            print(f"   • {year} ({start} a {end}) {'(ACTUAL)' if current else ''}")
        
        # Ver si 2026 está disponible
        temporada_2026 = next((s for s in seasons if s.get('year') == 2026), None)
        if temporada_2026:
            print(f"\n✅ 2026 SÍ está disponible!")
        else:
            print(f"\n❌ 2026 NO está disponible aún")
            print(f"   Usaremos la temporada más reciente: {ultimas_temporadas[-1].get('year')}")
