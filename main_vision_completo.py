# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Motores adaptados y estables)
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

# ==================== MOTORES v20 (nombres exactos que estás usando) ====================
from motor_nba_pro_v17 import analizar_nba_pro_v17, backtest_nba_pro_v17
from motor_mlb_pro import analizar_mlb_pro_v20, backtest_mlb_pro   # usamos v20 aunque el archivo se llama motor_mlb_pro
from motor_ufc_pro import analizar_ufc_pro_v20
from motor_fut_pro import analizar_futbol_pro_v20, backtest_futbol_pro_v20   # nombre del archivo que usaste

# ==================== FUNCIONES AUXILIARES ====================
def actualizar_odds_ufc():
    try:
        from scraper_odds_ufc_definitivo import actualizar_odds_ufc as scraper_odds
        st.info("🔄 Actualizando odds de UFC...")
        return scraper_odds()
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
    with st.spinner("🔄 Actualizando datos UFC..."):
        actualizar_datos_ufc()
    with st.spinner("🔄 Actualizando odds UFC..."):
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
    h1, h2, h3, h4 { color: #fff; text-shadow: 0 0 5px #fff, 0 0 10px #ff6600, 0 0 20px #00ff41; text-align: center; }
    .stButton>button { border: 2px solid #00ff41 !important; background: transparent !important; color: #00ff41 !important; }
    .stButton>button:hover { background-color: #00ff41 !important; color: #000 !important; }
    .profit-card { background: #1a1f2a; padding: 15px; border-radius: 10px; border: 1px solid #00ff41; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 BETTING AI - NEON EDITION")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')} - Motores v20")

GEMINI_API_KEY = get_gemini_api_key()
LIGAS_FUTBOL = ESPNLeagueCodes.obtener_todas()

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
        
        # Motores v20
        st.session_state.motores_v20 = {
            'nba': analizar_nba_pro_v17,
            'mlb': analizar_mlb_pro_v20,
            'ufc': analizar_ufc_pro_v20,
            'futbol': analizar_futbol_pro_v20
        }
        
        st.session_state.nba_partidos = []
        st.session_state.ufc_combates = []
        st.session_state.futbol_partidos = {}
        st.session_state.mlb_partidos = []
        st.session_state.init = True

    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.header("⚙️ CONTROLES")
        st.session_state.tracker.render_sidebar_tracker()
        st.markdown("---")
        
        if st.button("🔄 ACTUALIZAR ODDS UFC", use_container_width=True):
            actualizar_odds_ufc()
            st.success("✅ Odds actualizados")

        if st.button("🏀 CARGAR NBA", use_container_width=True):
            st.session_state.nba_partidos = st.session_state.scrapers['nba'].get_games()
            st.success(f"✅ {len(st.session_state.nba_partidos)} partidos") if st.session_state.nba_partidos else st.warning("No hay partidos NBA hoy")

        if st.button("⚾ CARGAR MLB", use_container_width=True):
            st.session_state.mlb_partidos = st.session_state.scrapers['mlb'].get_games()
            st.success(f"✅ {len(st.session_state.mlb_partidos)} partidos") if st.session_state.mlb_partidos else st.warning("No hay partidos MLB hoy")

        if st.button("🥊 CARGAR UFC", use_container_width=True):
            st.session_state.ufc_combates = st.session_state.scrapers['ufc'].get_events()
            st.success(f"✅ {len(st.session_state.ufc_combates)} combates") if st.session_state.ufc_combates else st.warning("No hay eventos UFC hoy")

        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: Premier, LaLiga...")
        ligas_filtradas = [l for l in LIGAS_FUTBOL if buscar_liga.lower() in l.lower()] if buscar_liga else LIGAS_FUTBOL
        with st.container(height=400):
            for liga in sorted(ligas_filtradas)[:50]:
                if st.button(f"⚽ {liga}", key=f"btn_liga_{liga}", use_container_width=True):
                    partidos = st.session_state.scrapers['futbol'].get_games(liga)
                    st.session_state.futbol_partidos[liga] = partidos
                    st.success(f"✅ {len(partidos)} partidos")

        st.markdown("---")
        st.subheader("🔥 MOTORES v20")
        if st.button("📊 Backtest TODOS", use_container_width=True):
            with st.spinner("Corriendo backtests..."):
                # Nota: backtest_mlb_pro no lo tienes definido, por eso lo omitimos o usamos uno genérico
                bt_nba = backtest_nba_pro_v17([])
                bt_fut = backtest_futbol_pro_v20([])
                st.success(f"""
                🏀 NBA: Precisión **{bt_nba['precision']}%**  
                ⚽ FÚTBOL: Precisión **{bt_fut['precision']}%**
                """)

    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    with tab1:  # NBA
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                accion = st.session_state.visual_nba.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("🏀 Analizando NBA..."):
                        resultado = st.session_state.motores_v20['nba'](p)
                        render_analisis_card(resultado)
                    st.rerun()
                st.markdown("---")
        else:
            st.info("👈 Carga NBA en el sidebar")

    with tab2:  # UFC
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                p1 = c.get('peleador1', {}).get('nombre', '')
                p2 = c.get('peleador2', {}).get('nombre', '')
                accion = st.session_state.visual_ufc.render(c, idx, st.session_state.tracker, None)
                if accion == "analizar":
                    with st.spinner("🥊 Analizando UFC..."):
                        resultado = st.session_state.motores_v20['ufc']({"peleador1": p1, "peleador2": p2})
                        render_analisis_card(resultado)
                    st.rerun()
                st.markdown("---")
        else:
            st.info("👈 Carga UFC en el sidebar")

    with tab3:  # FÚTBOL
        if st.session_state.futbol_partidos:
            for liga, partidos in st.session_state.futbol_partidos.items():
                if partidos:
                    st.markdown(f"### ⚽ {liga}")
                    for idx, p in enumerate(partidos):
                        accion = st.session_state.visual_futbol.render(p, idx, liga, st.session_state.tracker, None, None, None, None)
                        if accion == "analizar":
                            with st.spinner("⚽ Analizando Fútbol..."):
                                resultado = st.session_state.motores_v20['futbol'](p)
                                render_analisis_card(resultado)
                            st.rerun()
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    with tab4:  # MLB
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                accion = st.session_state.visual_mlb.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB..."):
                        resultado = st.session_state.motores_v20['mlb'](p)
                        render_analisis_card(resultado)
                    st.rerun()
                st.markdown("---")
        else:
            st.info("👈 Carga MLB en el sidebar")

    # Profit card
    try:
        if os.path.exists("data/bitacora_maestra.csv"):
            df = pd.read_csv("data/bitacora_maestra.csv")
            ganadas = len(df[df.get('acierto', False) == True])
            perdidas = len(df[df.get('acierto', False) == False])
            profit = ((ganadas * 0.90) - perdidas) * 10
            color = "#00ff41" if profit >= 0 else "#ff4b4b"
            st.sidebar.markdown(f"""
            <div class="profit-card">
                <span>Profit Estimado</span>
                <h2 style='color: {color}; margin: 0;'>${profit:.2f} USD</h2>
                <span>{ganadas}W / {perdidas}L</span>
            </div>
            """, unsafe_allow_html=True)
    except:
        pass

if __name__ == "__main__":
    main()
