# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Versión Final Estable para Streamlit Cloud)
Sin Selenium + Datos de prueba robustos + Gemini mejorado
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

# ==================== CEREBRO GEMINI ====================
try:
    from cerebro_gemini_pro import CerebroGeminiPro
except ImportError:
    CerebroGeminiPro = None

# ==================== FUNCIONES AUXILIARES ====================
def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        return ""

def inicializar_bd():
    """Crea tablas y datos de prueba si no existen"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/betting_stats.db")
    cursor = conn.cursor()
    
    # Tabla peleadores UFC
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peleadores_ufc (
            id INTEGER PRIMARY KEY,
            nombre TEXT UNIQUE,
            record TEXT,
            altura REAL,
            peso REAL,
            alcance REAL,
            postura TEXT,
            ko_rate REAL,
            grappling REAL,
            odds TEXT
        )
    ''')
    
    # Insertar datos de prueba si está vacío
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
                (nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', p)
    
    conn.commit()
    conn.close()

def main():
    if 'init' not in st.session_state:
        inicializar_bd()
        
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
        
        # Motores
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
        else:
            st.session_state.gemini = None
        
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
            with st.spinner("Cargando UFC..."):
                st.session_state.ufc_combates = st.session_state.scrapers['ufc'].get_events()
                st.success(f"✅ {len(st.session_state.ufc_combates)} combates") if st.session_state.ufc_combates else st.warning("No hay eventos UFC hoy")

        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: Premier, LaLiga, Liga MX...")
        ligas_filtradas = [l for l in ["Premier League", "La Liga", "Serie A", "Bundesliga", "Liga MX"] 
                          if buscar_liga.lower() in l.lower()] if buscar_liga else ["Premier League", "La Liga", "Serie A", "Bundesliga", "Liga MX"]
        
        for liga in ligas_filtradas:
            if st.button(f"⚽ {liga}", key=f"btn_{liga}", use_container_width=True):
                with st.spinner(f"Cargando {liga}..."):
                    partidos = st.session_state.scrapers['futbol'].get_games(liga)
                    st.session_state.futbol_partidos[liga] = partidos
                    st.success(f"✅ {len(partidos)} partidos")

    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    with tab1:  # NBA
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                accion = st.session_state.visual_nba.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("🏀 Analizando NBA..."):
                        resultado = st.session_state.motores['nba'](p)
                        render_analisis_card(resultado)
                        
                        if st.session_state.gemini:
                            gemini_resp = st.session_state.gemini.orquestrar_decision_final("NBA", p, resultado)
                            st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                            st.info(gemini_resp)
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
                        resultado = st.session_state.motores['ufc']({"peleador1": p1, "peleador2": p2})
                        render_analisis_card(resultado)
                        
                        if st.session_state.gemini:
                            gemini_resp = st.session_state.gemini.orquestrar_decision_final("UFC", c, resultado)
                            st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                            st.info(gemini_resp)
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
                                resultado = st.session_state.motores['futbol'](p)
                                render_analisis_card(resultado)
                                
                                if st.session_state.gemini:
                                    gemini_resp = st.session_state.gemini.orquestrar_decision_final("FÚTBOL", p, resultado)
                                    st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                    st.info(gemini_resp)
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    with tab4:  # MLB
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                accion = st.session_state.visual_mlb.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB..."):
                        resultado = st.session_state.motores['mlb'](p)
                        render_analisis_card(resultado)
                        
                        if st.session_state.gemini:
                            gemini_resp = st.session_state.gemini.orquestrar_decision_final("MLB", p, resultado)
                            st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                            st.info(gemini_resp)
                st.markdown("---")
        else:
            st.info("👈 Carga MLB en el sidebar")

if __name__ == "__main__":
    main()
