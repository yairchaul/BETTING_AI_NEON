# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Motores v20 integrados sin romper nada)
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import os
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== IMPORTS ORIGINALES ====================
from espn_nba import ESPN_NBA
from espn_mlb import ESPN_MLB_Mejorado as ESPN_MLB
from espn_ufc import ESPN_UFC
from espn_futbol import ESPN_FUTBOL
from bet_tracker import BetTracker
from visual_nba_mejorado import VisualNBAMejorado
from visual_ufc_final import VisualUFCFinal
from visual_futbol_triple import VisualFutbolTriple
from visual_mlb import VisualMLB
from analizador_nba_mejorado import AnalizadorNBAMejorado
from analizador_gemini_nba import AnalizadorGeminiNBA
from analizador_premium_profesional import AnalizadorPremiumProfesional
from calculador_probabilidades_futbol import CalculadorProbabilidadesFutbol
from selector_mejor_opcion import SelectorMejorOpcion
from analizador_futbol_heurístico_mejorado import AnalizadorFutbolHeuristicoMejorado
from analizador_futbol_gemini_mejorado import AnalizadorFutbolGeminiMejorado
from analizador_futbol_premium import AnalizadorFutbolPremium
from ufc_data_aggregator import UFCDataAggregator
from analizador_ufc_final import AnalizadorUFCFinal
from analizador_ufc_gemini import AnalizadorUFCGemini
from analizador_ufc_premium import AnalizadorUFCPremium
from analizador_ufc_ko_pro import AnalizadorUFCKOPro
from visual_ufc_ko import VisualUFCKO
from analizador_nba_props import AnalizadorNBAProps
from visual_nba_props import VisualNBAProps
from gestor_ligas_universal import GestorLigasUniversal
from espn_league_codes import ESPNLeagueCodes
from analizador_ufc_maestro import AnalizadorUFCMaestro
from database_manager import db
from render_unificado import render_analisis_card
from integrador_v17 import get_integrador

# ==================== MOTORES v20 (usando nombres exactos de tu repo) ====================
from motor_nba_pro_v17 import analizar_nba_pro_v17, backtest_nba_v17
from motor_mlb_pro import analizar_mlb_pro, backtest_mlb_pro
from motor_ufc_pro import analizar_ufc_pro, backtest_ufc_pro
from motor_futbol_pro_v20 import analizar_futbol_pro_v20, backtest_futbol_pro_v20

# ==================== FUNCIONES AUXILIARES ====================
def actualizar_odds_ufc():
    try:
        from scraper_odds_ufc_definitivo import actualizar_odds_ufc as scraper_odds
        st.info("🔄 Actualizando odds de UFC...")
        odds = scraper_odds()
        return odds
    except Exception as e:
        st.warning(f"⚠️ No se pudieron actualizar odds UFC: {e}")
        return {}

def actualizar_datos_ufc():
    try:
        from scraper_ufc_final import actualizar_ufc as scraper_ufc
        st.info("🔄 Actualizando datos de peleadores UFC...")
        scraper_ufc()
        return True
    except Exception as e:
        st.warning(f"⚠️ No se pudieron actualizar datos UFC: {e}")
        return False

def inicializar_datos():
    st.info("🚀 Inicializando BETTING AI NEON...")
    os.makedirs("data", exist_ok=True)
    with st.spinner("🔄 Actualizando datos de peleadores UFC..."):
        actualizar_datos_ufc()
    with st.spinner("🔄 Actualizando odds de UFC..."):
        actualizar_odds_ufc()

def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        return ""

# ==================== CONFIGURACIÓN ====================
st.set_page_config(page_title="BETTING AI - NEON EDITION", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .stMarkdown, .stText, .stCaption, .stSubheader, div, p, span, label { text-shadow: 0 0 2px #ff6600, 0 0 3px #ff6600; }
    h1, h2, h3, h4 { color: #fff; text-shadow: 0 0 5px #fff, 0 0 10px #ff6600, 0 0 20px #00ff41, 0 0 30px #00ff41; text-align: center; }
    .stButton>button { border: 2px solid #00ff41 !important; background-color: transparent !important; color: #00ff41 !important; text-shadow: 0 0 2px #ff6600; box-shadow: 0 0 10px #00ff41; transition: 0.3s; }
    .stButton>button:hover { background-color: #00ff41 !important; color: #000 !important; box-shadow: 0 0 25px #ff6600; }
    .profit-card { background: #1a1f2a; padding: 15px; border-radius: 10px; border: 1px solid #00ff41; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 BETTING AI - NEON EDITION")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')} - Motores v20 probados")

GEMINI_API_KEY = get_gemini_api_key()
LIGAS_FUTBOL = ESPNLeagueCodes.obtener_todas()

# ==================== INICIALIZACIÓN ====================
def main():
    if 'init' not in st.session_state:
        inicializar_datos()
        
        st.session_state.scrapers = {
            'nba': ESPN_NBA(),
            'mlb': ESPN_MLB(),
            'ufc': ESPN_UFC(),
            'futbol': ESPN_FUTBOL()
        }
        st.session_state.tracker = BetTracker()
        st.session_state.visual_nba = VisualNBAMejorado()
        st.session_state.visual_ufc = VisualUFCFinal()
        st.session_state.visual_futbol = VisualFutbolTriple()
        st.session_state.visual_mlb = VisualMLB()
        st.session_state.integrador_v17 = get_integrador()
        
        # ==================== MOTORES v20 ====================
        st.session_state.motores_v20 = {
            'nba': analizar_nba_pro_v17,
            'mlb': analizar_mlb_pro,
            'ufc': analizar_ufc_pro,
            'futbol': analizar_futbol_pro_v20
        }
        
        # Mant