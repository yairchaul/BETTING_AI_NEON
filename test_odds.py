# test_odds.py
from modules.odds_api_integrator import OddsAPIIntegrator
import streamlit as st
from dotenv import load_dotenv
import os

# Cargar secrets manualmente para prueba
load_dotenv()

# Probar conexión
odds_api = OddsAPIIntegrator()
success, message = odds_api.test_connection()
print(message)

if success:
    # Probar búsqueda de un partido real
    odds = odds_api.get_live_odds("Manchester City", "Liverpool")
    if odds:
        print("\n✅ Odds encontradas:")
        print(f"Local: {odds['cuota_local']}")
        print(f"Empate: {odds['cuota_empate']}")
        print(f"Visitante: {odds['cuota_visitante']}")
    else:
        print("\nℹ️ No hay odds para este partido ahora")
