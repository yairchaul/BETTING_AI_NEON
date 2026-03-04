# test_odds.py
from modules.odds_api_integrator import OddsAPIIntegrator
import streamlit as st

print("🔍 PROBANDO ODDS-API.IO")
print("=" * 50)

# Crear instancia
odds_api = OddsAPIIntegrator()

# Verificar si tiene la key
if odds_api.api_key:
    print(f"✅ API Key cargada: {odds_api.api_key[:5]}...{odds_api.api_key[-5:]}")
else:
    print("❌ No se pudo cargar la API Key")

print("-" * 50)

# Probar conexión
success, message = odds_api.test_connection()
print(message)

if success:
    print("\n✅ API conectada correctamente")
    
    # Probar búsqueda de partidos
    equipos = [
        ("Manchester City", "Liverpool"),
        ("Real Madrid", "Barcelona"),
        ("America", "Chivas"),
        ("Cruz Azul", "Pumas")
    ]
    
    for local, visitante in equipos:
        print(f"\n🔎 Buscando: {local} vs {visitante}")
        odds = odds_api.get_live_odds(local, visitante)
        
        if odds:
            print(f"   ✅ Local: {odds['cuota_local']}")
            print(f"   ✅ Empate: {odds['cuota_empate']}")
            print(f"   ✅ Visitante: {odds['cuota_visitante']}")
            if odds.get('liga'):
                print(f"   📌 Liga: {odds['liga']}")
        else:
            print("   ⏳ No hay odds disponibles ahora")
            
    print("\n✨ Prueba completada")
