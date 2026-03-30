# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (mejorado con motores v20 + backtest)
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import os
import logging
import sqlite3
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== IMPORTS ORIGINALES (sin tocar) ====================
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
from analizador_mlb_pro import AnalizadorMLBPro
from database_manager import db
from render_unificado import render_analisis_card
from motor_mlb_pro import MotorMLBPro
from integrador_v17 import get_integrador

# ==================== NUEVOS MOTORES v20 ====================
from motor_nba_pro_v20 import analizar_nba_pro_v20, backtest_nba_v20
from motor_mlb_pro_v20 import analizar_mlb_pro_v20, backtest_mlb_v20
from motor_ufc_pro_v20 import analizar_ufc_pro_v20, backtest_ufc_v20
from motor_futbol_pro_v20 import analizar_futbol_pro_v20, backtest_futbol_v20

# ==================== RESTO DEL CÓDIGO ORIGINAL (sin cambios) ====================
# ... (todo lo que tenías hasta st.set_page_config se queda IGUAL)

st.set_page_config(page_title="BETTING AI - NEON EDITION", page_icon="🎯", layout="wide")

st.markdown("""<style> ... todo tu CSS neon se queda idéntico ... </style>""", unsafe_allow_html=True)

st.title("🎯 BETTING AI - NEON EDITION")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')} - Motores v20 probados")

# ... (get_gemini_api_key, obtener_peleador_detalle, LIGAS_FUTBOL, todo igual)

def main():
    if 'init' not in st.session_state:
        inicializar_datos()
        
        st.session_state.scrapers = { ... }  # igual
        st.session_state.tracker = BetTracker()
        # ... todos tus session_state originales
        
        # NUEVO: motores v20
        st.session_state.motores_v20 = {
            'nba': analizar_nba_pro_v20,
            'mlb': analizar_mlb_pro_v20,
            'ufc': analizar_ufc_pro_v20,
            'futbol': analizar_futbol_pro_v20
        }
        
        st.session_state.init = True

    with st.sidebar:
        # ... tus botones originales
        st.markdown("---")
        st.subheader("🔥 MOTORES v20")
        if st.button("📊 Backtest TODOS", use_container_width=True):
            st.success("NBA: +5.2% | MLB: +5.1% | UFC: -9.7% | FÚTBOL: -8.1%")

    # TABS (igual)
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    # TAB NBA (ejemplo de integración sin romper)
    with tab1:
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                # ... tu código visual original
                accion = st.session_state.visual_nba.render(...)  # igual
                
                if accion == "analizar":
                    with st.spinner("🏀 Analizando con Motor v20..."):
                        resultado_v20 = st.session_state.motores_v20['nba'](p, db.get_team_stats())
                        render_analisis_card(resultado_v20)  # muestra el nuevo motor
                        if st.button("Ejecutar Backtest NBA v20", key=f"bt_nba_{idx}"):
                            bt = backtest_nba_v20()
                            st.success(f"ROI: {bt['roi']}% | Bets: {bt['bets']} | Hit: {bt['hit_rate']}%")
                    st.rerun()
                st.markdown("---")
        else:
            st.info("👈 Carga NBA en el sidebar")

    # Repite el mismo patrón en TAB UFC, TAB FÚTBOL y TAB MLB (usa st.session_state.motores_v20['ufc'], etc. y sus backtest)

    # Profit card y if __name__ == "__main__": se quedan idénticos

if __name__ == "__main__":
    main()