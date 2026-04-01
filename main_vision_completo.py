# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Versión Final Optimizada)
Scraper UFC robusto + Motores v20 + Gemini mejorado
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import os
import logging
import sqlite3
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== IMPORTS ====================
from espn_nba import ESPN_NBA
from espn_mlb import ESPN_MLB_Mejorado as ESPN_MLB
from espn_ufc import ESPN_UFC
from espn_futbol import ESPN_FUTBOL
from bet_tracker import BetTracker
from visual_nba_mejorado import VisualNBAMejorado
from visual_ufc_final import VisualUFCFinal
from visual_futbol_triple import VisualFutbolTriple
from visual_mlb import VisualMLB
from database_manager import db
from render_unificado import render_analisis_card

# ==================== MOTORES V20 ====================
from motor_nba_pro_v17 import analizar_nba_pro_v17
from motor_mlb_pro import analizar_mlb_pro_v20
from motor_ufc_pro import analizar_ufc_pro_v20
from motor_fut_pro import analizar_futbol_pro_v20

# ==================== GEMINI PRO ====================
try:
    from cerebro_gemini_pro import CerebroGeminiPro
except ImportError:
    CerebroGeminiPro = None
    logger.warning("cerebro_gemini_pro no encontrado")

# ==================== FUNCIONES AUXILIARES ====================
def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        return ""

def inicializar_bd_ufc():
    """Inicializa BD UFC con estructura correcta"""
    os.makedirs("data", exist_ok=True)
    try:
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos_ufc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                fecha TEXT,
                cartelera TEXT,
                ultima_actualizacion TEXT,
                fecha_evento TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peleadores_ufc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                record TEXT,
                altura REAL,
                peso REAL,
                alcance REAL,
                postura TEXT,
                ko_rate REAL,
                grappling REAL,
                odds TEXT,
                ultima_actualizacion TEXT
            )
        ''')

        # Insertar peleadores base si no existen
        cursor.execute("SELECT COUNT(*) FROM peleadores_ufc")
        if cursor.fetchone()[0] == 0:
            peleadores = [
                ("Israel Adesanya", "24-5-0", 193, 84, 203, "Freestyle", 0.9, 0.5, "-120"),
                ("Joe Pyfer", "15-3-0", 188, 84, 190, "Boxing", 0.6, 0.5, "-106"),
                ("Bruna Brasil", "11-6-1", 167, 52, 166, "MMA", 0.9, 0.5, "+390"),
                ("Alexia Thainara", "13-1-0", 162, 52, 170, "MMA", 0.5, 0.5, "-520"),
            ]
            for p in peleadores:
                cursor.execute('''
                    INSERT OR IGNORE INTO peleadores_ufc 
                    (nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds, ultima_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (*p, datetime.now().isoformat()))
            logger.info("✅ Peleadores base insertados")

        conn.commit()
        logger.info("✅ Base de datos UFC inicializada")
    except Exception as e:
        logger.error(f"Error inicializando BD: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    if 'init' not in st.session_state:
        inicializar_bd_ufc()
        
        st.session_state.scrapers = {
            'nba': ESPN_NBA(),
            'mlb': ESPN_MLB(),
            'ufc': ESPN_UFC(),          # ← Scraper mejorado
            'futbol': ESPN_FUTBOL()
        }
        st.session_state.tracker = BetTracker()
        st.session_state.visual_nba = VisualNBAMejorado()
        st.session_state.visual_ufc = VisualUFCFinal()
        st.session_state.visual_futbol = VisualFutbolTriple()
        st.session_state.visual_mlb = VisualMLB()
        
        # Motores v20
        st.session_state.motores = {
            'nba': analizar_nba_pro_v17,
            'mlb': analizar_mlb_pro_v20,
            'ufc': analizar_ufc_pro_v20,
            'futbol': analizar_futbol_pro_v20
        }
        
        # Gemini
        gemini_key = get_gemini_api_key()
        if gemini_key and CerebroGeminiPro:
            st.session_state.gemini = CerebroGeminiPro(gemini_key)
            st.success("✅ Gemini conectado - Decisor Final activo")
        else:
            st.session_state.gemini = None
            st.warning("⚠️ Gemini no disponible - Solo análisis matemático")
        
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
        
        if st.button("🏀 CARGAR NBA", use_container_width=True):
            with st.spinner("Cargando NBA..."):
                st.session_state.nba_partidos = st.session_state.scrapers['nba'].get_games()
                st.success(f"✅ {len(st.session_state.nba_partidos)} partidos") if st.session_state.nba_partidos else st.warning("No hay partidos NBA hoy")

        if st.button("⚾ CARGAR MLB", use_container_width=True):
            with st.spinner("Cargando MLB..."):
                st.session_state.mlb_partidos = st.session_state.scrapers['mlb'].get_games()
                st.success(f"✅ {len(st.session_state.mlb_partidos)} partidos") if st.session_state.mlb_partidos else st.warning("No hay partidos MLB hoy")

        if st.button("🥊 CARGAR UFC", use_container_width=True):
            with st.spinner("🔄 Buscando cartelera UFC actual (100% dinámico)..."):
                ufc_scraper = st.session_state.scrapers['ufc']
                st.session_state.ufc_combates = ufc_scraper.get_events()
                if st.session_state.ufc_combates:
                    st.success(f"✅ {len(st.session_state.ufc_combates)} combates cargados")
                else:
                    st.info("ℹ️ No hay eventos UFC disponibles en este momento")

        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: Premier, LaLiga, Liga MX...")
        ligas = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Liga MX"]
        ligas_filtradas = [l for l in ligas if buscar_liga.lower() in l.lower()] if buscar_liga else ligas
        
        for liga in ligas_filtradas:
            if st.button(f"⚽ {liga}", key=f"btn_{liga}", use_container_width=True):
                with st.spinner(f"Cargando {liga}..."):
                    partidos = st.session_state.scrapers['futbol'].get_games(liga)
                    st.session_state.futbol_partidos[liga] = partidos
                    st.success(f"✅ {len(partidos)} partidos") if partidos else st.warning(f"No hay partidos de {liga} hoy")

        if st.button("🧹 LIMPIAR CACHÉ", use_container_width=True):
            st.session_state.futbol_partidos = {}
            st.rerun()

        if st.button("🔄 RESET TOTAL", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    with tab1:  # NBA
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                accion = st.session_state.visual_nba.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("🏀 Analizando NBA..."):
                        try:
                            resultado = st.session_state.motores['nba'](p)
                            render_analisis_card(resultado)
                            if st.session_state.gemini:
                                gemini_resp = st.session_state.gemini.orquestrar_decision_final("NBA", p, resultado)
                                st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                st.info(gemini_resp)
                        except Exception as e:
                            st.error(f"Error en análisis NBA: {e}")
                st.markdown("---")
        else:
            st.info("👈 Carga NBA en el sidebar")

    with tab2:  # UFC
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                p1 = c.get('peleador1', {}).get('nombre', '')
                p2 = c.get('peleador2', {}).get('nombre', '')
                
                partido_visual = {
                    'peleador1': {'nombre': p1},
                    'peleador2': {'nombre': p2}
                }
                
                accion = st.session_state.visual_ufc.render(partido_visual, idx, st.session_state.tracker, None)
                if accion == "analizar":
                    with st.spinner("🥊 Analizando UFC..."):
                        try:
                            resultado = st.session_state.motores['ufc']({"peleador1": p1, "peleador2": p2})
                            render_analisis_card(resultado)
                            if st.session_state.gemini:
                                gemini_resp = st.session_state.gemini.orquestrar_decision_final("UFC", partido_visual, resultado)
                                st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                st.info(gemini_resp)
                        except Exception as e:
                            st.error(f"Error en análisis UFC: {e}")
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
                                try:
                                    resultado = st.session_state.motores['futbol'](p)
                                    render_analisis_card(resultado)
                                    if st.session_state.gemini:
                                        gemini_resp = st.session_state.gemini.orquestrar_decision_final("FÚTBOL", p, resultado)
                                        st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                        st.info(gemini_resp)
                                except Exception as e:
                                    st.error(f"Error en análisis Fútbol: {e}")
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    with tab4:  # MLB
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                accion = st.session_state.visual_mlb.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB..."):
                        try:
                            resultado = st.session_state.motores['mlb'](p)
                            render_analisis_card(resultado)
                            if st.session_state.gemini:
                                gemini_resp = st.session_state.gemini.orquestrar_decision_final("MLB", p, resultado)
                                st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                st.info(gemini_resp)
                        except Exception as e:
                            st.error(f"Error en análisis MLB: {e}")
                st.markdown("---")
        else:
            st.info("👈 Carga MLB en el sidebar")

    # ==================== PROFIT CARD ====================
    try:
        if os.path.exists("data/bitacora_maestra.csv"):
            df = pd.read_csv("data/bitacora_maestra.csv")
            if 'acierto' in df.columns:
                ganadas = len(df[df['acierto'] == True])
                perdidas = len(df[df['acierto'] == False])
                if ganadas + perdidas > 0:
                    profit = ((ganadas * 0.90) - perdidas) * 10
                    color = "#00ff41" if profit >= 0 else "#ff4b4b"
                    st.sidebar.markdown(f"""
                    <div class="profit-card">
                        <span>Profit Estimado</span>
                        <h2 style='color: {color}; margin: 0;'>${profit:.2f} USD</h2>
                        <span>{ganadas}W / {perdidas}L</span>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error en profit card: {e}")

if __name__ == "__main__":
    main()
