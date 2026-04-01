# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Versión Final con Multi-IA)
NBA, MLB, UFC, Fútbol con Gemini + Grok + DeepSeek
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import os
import logging
import sqlite3

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

# ==================== MOTORES ====================
from motor_nba_pro_v17 import analizar_nba_pro_v17
from motor_mlb_pro import analizar_mlb_pro_v20
from motor_ufc_pro import analizar_ufc_pro_v20
from motor_fut_pro import analizar_futbol_pro_v20

# ==================== MULTI-IA ====================
try:
    from cerebro_multi_ia import cerebro_multi
except ImportError:
    cerebro_multi = None
    logger.warning("cerebro_multi_ia no encontrado")

# ==================== FUNCIONES AUXILIARES ====================
def inicializar_bd_ufc():
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
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error BD UFC: {e}")

def mostrar_analisis_ia(resultado_ia):
    """Muestra el análisis de la IA con estilo neon"""
    if not resultado_ia:
        return
    
    st.markdown("""
        <style>
        .ia-card {
            background: rgba(0, 255, 255, 0.05);
            border-left: 3px solid #00f2ff;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
        }
        .ia-header {
            color: #00f2ff;
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .ia-content {
            color: #e0e0e0;
            font-size: 0.9em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if resultado_ia.get('consenso'):
        st.markdown(f"""
            <div class="ia-card">
                <div class="ia-header">🤖 MULTI-IA CONSENSUS</div>
                <div class="ia-content">{resultado_ia['consenso']}</div>
            </div>
        """, unsafe_allow_html=True)
    elif resultado_ia.get('gemini_prediccion'):
        st.markdown(f"""
            <div class="ia-card">
                <div class="ia-header">🤖 GEMINI ANALYSIS</div>
                <div class="ia-content">{resultado_ia['gemini_prediccion']}</div>
            </div>
        """, unsafe_allow_html=True)

def main():
    if 'init' not in st.session_state:
        inicializar_bd_ufc()
        
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
        
        st.session_state.motores = {
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
        
        if st.button("🏀 CARGAR NBA", use_container_width=True):
            with st.spinner("Cargando NBA..."):
                st.session_state.nba_partidos = st.session_state.scrapers['nba'].get_games()
                if st.session_state.nba_partidos:
                    st.success(f"✅ {len(st.session_state.nba_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos NBA hoy")

        if st.button("⚾ CARGAR MLB", use_container_width=True):
            with st.spinner("Cargando MLB..."):
                st.session_state.mlb_partidos = st.session_state.scrapers['mlb'].get_games()
                if st.session_state.mlb_partidos:
                    st.success(f"✅ {len(st.session_state.mlb_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos MLB hoy")

        if st.button("🥊 CARGAR UFC", use_container_width=True):
            with st.spinner("🔄 Buscando cartelera UFC (100% dinámico)..."):
                ufc_scraper = st.session_state.scrapers['ufc']
                st.session_state.ufc_combates = ufc_scraper.get_events()
                if st.session_state.ufc_combates:
                    st.success(f"✅ {len(st.session_state.ufc_combates)} combates")
                else:
                    st.info("ℹ️ No hay eventos UFC disponibles")

        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        
        # Obtener ligas dinámicamente
        with st.spinner("Cargando ligas disponibles..."):
            futbol_scraper = st.session_state.scrapers['futbol']
            ligas = futbol_scraper.get_available_leagues()
        
        st.caption(f"📋 {len(ligas)} ligas disponibles")
        
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: Premier, LaLiga...")
        
        if buscar_liga:
            ligas_filtradas = [l for l in ligas if buscar_liga.lower() in l.lower()]
        else:
            ligas_filtradas = ligas[:20]
        
        for liga in ligas_filtradas:
            if st.button(f"⚽ {liga}", key=f"btn_{liga}", use_container_width=True):
                with st.spinner(f"Cargando {liga}..."):
                    partidos = futbol_scraper.get_games(liga)
                    st.session_state.futbol_partidos[liga] = partidos
                    if partidos:
                        st.success(f"✅ {len(partidos)} partidos")
                    else:
                        st.warning(f"⚠️ No hay partidos de {liga} hoy")

        if st.button("🧹 LIMPIAR CACHÉ", use_container_width=True):
            st.session_state.futbol_partidos = {}
            st.rerun()

        if st.button("🔄 RESET TOTAL", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    # NBA TAB
    with tab1:
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                accion = st.session_state.visual_nba.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("🏀 Analizando NBA..."):
                        try:
                            resultado = st.session_state.motores['nba'](p)
                            render_analisis_card(resultado)
                            
                            # Análisis con Multi-IA
                            if cerebro_multi:
                                analisis_ia = cerebro_multi.orquestrar_analisis("NBA", p, resultado)
                                mostrar_analisis_ia(analisis_ia)
                            
                        except Exception as e:
                            st.error(f"Error en análisis NBA: {e}")
                st.markdown("---")
        else:
            st.info("👈 Carga NBA en el sidebar")

    # UFC TAB
    with tab2:
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                p1 = c.get('peleador1', {}).get('nombre', '')
                p2 = c.get('peleador2', {}).get('nombre', '')
                partido_visual = {'peleador1': p1, 'peleador2': p2}
                
                accion = st.session_state.visual_ufc.render(partido_visual, idx, st.session_state.tracker, None)
                if accion == "analizar":
                    with st.spinner("🥊 Analizando UFC..."):
                        try:
                            resultado = st.session_state.motores['ufc']({"peleador1": p1, "peleador2": p2})
                            render_analisis_card(resultado)
                            
                            # Análisis con Multi-IA
                            if cerebro_multi:
                                analisis_ia = cerebro_multi.orquestrar_analisis("UFC", partido_visual, resultado)
                                mostrar_analisis_ia(analisis_ia)
                            
                        except Exception as e:
                            st.error(f"Error en análisis UFC: {e}")
                st.markdown("---")
        else:
            st.info("👈 Carga UFC en el sidebar")

    # FÚTBOL TAB
    with tab3:
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
                                    
                                    # Análisis con Multi-IA
                                    if cerebro_multi:
                                        analisis_ia = cerebro_multi.orquestrar_analisis("FÚTBOL", p, resultado)
                                        mostrar_analisis_ia(analisis_ia)
                                    
                                except Exception as e:
                                    st.error(f"Error en análisis Fútbol: {e}")
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    # MLB TAB
    with tab4:
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                accion = st.session_state.visual_mlb.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB..."):
                        try:
                            resultado = st.session_state.motores['mlb'](p)
                            render_analisis_card(resultado)
                            
                            # Análisis con Multi-IA
                            if cerebro_multi:
                                analisis_ia = cerebro_multi.orquestrar_analisis("MLB", p, resultado)
                                mostrar_analisis_ia(analisis_ia)
                            
                        except Exception as e:
                            st.error(f"Error en análisis MLB: {e}")
                st.markdown("---")
        else:
            st.info("👈 Carga MLB en el sidebar")

if __name__ == "__main__":
    main()
