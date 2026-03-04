# test_motores.py
import streamlit as st
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.smart_searcher import SmartSearcher
from modules.elo_system import ELOSystem
from modules.xgboost_predictor import XGBoostPredictor

print("?? VERIFICANDO MOTORES DE AN?LISIS")
print("=" * 60)

# Inicializar
analyzer = ProAnalyzerUltimate()
searcher = SmartSearcher()
elo = ELOSystem()
xgb = XGBoostPredictor()

# Verificar cada motor
print(f"\n? SmartSearcher: {'Disponible' if searcher else 'No disponible'}")
print(f"? ELOSystem: {'Disponible' if elo else 'No disponible'}")
print(f"? XGBoost: {'Disponible' if xgb else 'No disponible'}")

# Probar una b?squeda de ejemplo
print("\n?? Probando b?squeda de datos para 'Puebla'...")
try:
    resultados = searcher.search_team('Puebla')
    print(f"   Encontrados: {len(resultados)} resultados")
    if resultados:
        print(f"   Primer resultado: {resultados[0]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
