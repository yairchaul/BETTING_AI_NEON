# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Versión Unificada)
Funciona igual en local y Streamlit Cloud con datos dinámicos
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

# ==================== MOTORES ====================
from motor_nba_pro_v17 import analizar_nba_pro_v17
from motor_mlb_pro import analizar_mlb_pro_v20
from motor_ufc_pro import analizar_ufc_pro_v20
from motor_fut_pro import analizar_futbol_pro_v20

# ==================== GEMINI ====================
try:
    from cerebro_gemini_pro import CerebroGeminiPro
except ImportError:
    CerebroGeminiPro = None

# ==================== FUNCIONES AUXILIARES ====================
def get_gemini_api_key():
    """Obtiene API key desde secrets, .env, o variable de entorno"""
    # Streamlit Cloud secrets
    try:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except:
        pass
    
    # Archivo .env local
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        pass
    
    # Variable de entorno
    import os
    return os.environ.get('GEMINI_API_KEY', '')

def inicializar_bd_ufc():
    """Inicializa BD UFC con estructura completa"""
    os.makedirs("data", exist_ok=True)
    try:
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        
        # Tabla eventos UFC
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
        
        # Tabla peleadores UFC
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
        
        # Insertar datos base si tabla vacía
        cursor.execute("SELECT COUNT(*) FROM peleadores_ufc")
        if cursor.fetchone()[0] == 0:
            peleadores = [
                ("Israel Adesanya", "24-5-0", 193, 84, 203, "Freestyle", 0.9, 0.5, "-120"),
                ("Joe Pyfer", "15-3-0", 188, 84, 190, "Boxing", 0.6, 0.5, "-106"),
                ("Bruna Brasil", "11-6-1", 167, 52, 166, "MMA", 0.9, 0.5, "+390"),
                ("Alexia Thainara", "13-1-0", 162, 52, 170, "MMA", 0.5, 0.5, "-520"),
                ("Renato Moicano", "20-7-1", 180, 70, 183, "Freestyle", 0.7, 0.6, "-150"),
                ("Grant Duncan", "15-2-0", 178, 70, 180, "Boxing", 0.8, 0.4, "+130"),
                ("Ricky Simon", "20-5-0", 170, 61, 168, "Wrestling", 0.6, 0.7, "-200"),
                ("Adrian Yanez", "16-4-0", 170, 61, 170, "Boxing", 0.8, 0.3, "+170"),
                ("Maycee Barber", "15-2-0", 165, 57, 165, "MMA", 0.9, 0.5, "-148"),
                ("Alexa Grasso", "16-5-1", 165, 57, 167, "MMA", 0.5, 0.6, "+124"),
            ]
            for p in peleadores:
                cursor.execute('''
                    INSERT OR IGNORE INTO peleadores_ufc 
                    (nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds, ultima_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (*p, datetime.now().isoformat()))
            logger.info("✅ Peleadores base insertados")
        
        conn.commit()
        conn.close()
        logger.info("✅ BD UFC inicializada")
    except Exception as e:
        logger.error(f"Error BD UFC: {e}")

def obtener_datos_peleador(nombre):
    """Obtiene datos de un peleador desde la BD"""
    try:
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds
            FROM peleadores_ufc 
            WHERE nombre LIKE ? OR nombre = ?
            LIMIT 1
        ''', (f"%{nombre}%", nombre))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'nombre': row[0],
                'record': row[1] if row[1] else '0-0-0',
                'altura': int(row[2]) if row[2] else 0,
                'peso': row[3] if row[3] else 0,
                'alcance': int(row[4]) if row[4] else 0,
                'postura': row[5] if row[5] else 'N/A',
                'ko_rate': row[6] if row[6] else 0.5,
                'grappling': row[7] if row[7] else 0.5,
                'odds': row[8] if row[8] else 'N/A'
            }
        return None
    except Exception as e:
        logger.error(f"Error obteniendo peleador {nombre}: {e}")
        return None

def mostrar_player_props_nba(analisis):
    """Muestra los player props de NBA"""
    col1, col2 = st.columns(2)
    with col1:
        top3 = analisis.get('top_3pm_local')
        if top3:
            st.markdown(f"**🏀 {top3.get('nombre', 'N/A')}**")
            st.caption(f"🎯 {top3.get('triples_por_partido', 0)} triples/partido")
    with col2:
        top3 = analisis.get('top_3pm_visit')
        if top3:
            st.markdown(f"**🏀 {top3.get('nombre', 'N/A')}**")
            st.caption(f"🎯 {top3.get('triples_por_partido', 0)} triples/partido")

def mostrar_player_props_mlb(analisis):
    """Muestra los player props de MLB"""
    col1, col2 = st.columns(2)
    with col1:
        hr = analisis.get('top_hr_local')
        if hr:
            if isinstance(hr, list):
                for h in hr[:2]:
                    st.markdown(f"**⚾ {h.get('nombre', 'N/A')}**")
                    st.caption(f"💪 {h.get('hr', 0)} HR")
            else:
                st.markdown(f"**⚾ {hr.get('nombre', 'N/A')}**")
                st.caption(f"💪 {hr.get('hr', 0)} HR")
    with col2:
        hr = analisis.get('top_hr_visit')
        if hr:
            if isinstance(hr, list):
                for h in hr[:2]:
                    st.markdown(f"**⚾ {h.get('nombre', 'N/A')}**")
                    st.caption(f"💪 {h.get('hr', 0)} HR")
            else:
                st.markdown(f"**⚾ {hr.get('nombre', 'N/A')}**")
                st.caption(f"💪 {hr.get('hr', 0)} HR")

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
        
        # Gemini
        gemini_key = get_gemini_api_key()
        if gemini_key and CerebroGeminiPro:
            st.session_state.gemini = CerebroGeminiPro(gemini_key)
            st.success("✅ Gemini conectado")
        else:
            st.session_state.gemini = None
            st.warning("⚠️ Gemini no disponible - Revisa API key")
        
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
        
        # NBA
        if st.button("🏀 CARGAR NBA", use_container_width=True):
            with st.spinner("Cargando NBA..."):
                st.session_state.nba_partidos = st.session_state.scrapers['nba'].get_games()
                if st.session_state.nba_partidos:
                    st.success(f"✅ {len(st.session_state.nba_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos NBA hoy")

        # MLB
        if st.button("⚾ CARGAR MLB", use_container_width=True):
            with st.spinner("Cargando MLB..."):
                st.session_state.mlb_partidos = st.session_state.scrapers['mlb'].get_games()
                if st.session_state.mlb_partidos:
                    st.success(f"✅ {len(st.session_state.mlb_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos MLB hoy")

        # UFC
        if st.button("🥊 CARGAR UFC", use_container_width=True):
            with st.spinner("🔄 Buscando cartelera UFC..."):
                ufc_scraper = st.session_state.scrapers['ufc']
                st.session_state.ufc_combates = ufc_scraper.get_events()
                if st.session_state.ufc_combates:
                    st.success(f"✅ {len(st.session_state.ufc_combates)} combates")
                else:
                    st.info("ℹ️ No hay eventos UFC disponibles")

        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        
        # Obtener ligas dinámicamente
        with st.spinner("Cargando ligas..."):
            futbol_scraper = st.session_state.scrapers['futbol']
            ligas = futbol_scraper.get_available_leagues()
        
        st.caption(f"📋 {len(ligas)} ligas disponibles")
        
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: Premier, LaLiga, A-League...")
        
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

    # ==================== NBA TAB ====================
    with tab1:
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                accion = st.session_state.visual_nba.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("🏀 Analizando NBA..."):
                        try:
                            resultado = st.session_state.motores['nba'](p)
                            render_analisis_card(resultado)
                            if resultado.get('top_3pm_local') or resultado.get('top_3pm_visit'):
                                st.markdown("### 🏀 MÁXIMOS TRIPLEROS")
                                mostrar_player_props_nba(resultado)
                            if st.session_state.gemini:
                                gemini_resp = st.session_state.gemini.orquestrar_decision_final("NBA", p, resultado)
                                st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                st.info(gemini_resp)
                        except Exception as e:
                            st.error(f"Error en análisis NBA: {e}")
                st.markdown("---")
        else:
            st.info("👈 Carga NBA en el sidebar")

    # ==================== UFC TAB ====================
    with tab2:
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                # Manejar diferentes formatos de datos
                if isinstance(c, dict):
                    p1_raw = c.get('peleador1', {})
                    p2_raw = c.get('peleador2', {})
                    
                    if isinstance(p1_raw, str):
                        p1_nombre = p1_raw
                        p1_dict = {'nombre': p1_nombre}
                    else:
                        p1_nombre = p1_raw.get('nombre', '')
                        p1_dict = p1_raw
                    
                    if isinstance(p2_raw, str):
                        p2_nombre = p2_raw
                        p2_dict = {'nombre': p2_nombre}
                    else:
                        p2_nombre = p2_raw.get('nombre', '')
                        p2_dict = p2_raw
                else:
                    p1_nombre = ''
                    p2_nombre = ''
                    p1_dict = {'nombre': ''}
                    p2_dict = {'nombre': ''}
                
                # Enriquecer con datos de BD
                datos_p1 = obtener_datos_peleador(p1_nombre)
                datos_p2 = obtener_datos_peleador(p2_nombre)
                
                if datos_p1:
                    p1_dict = datos_p1
                if datos_p2:
                    p2_dict = datos_p2
                
                partido_visual = {
                    'peleador1': p1_dict,
                    'peleador2': p2_dict
                }
                
                accion = st.session_state.visual_ufc.render(partido_visual, idx, st.session_state.tracker, None)
                if accion == "analizar":
                    with st.spinner("🥊 Analizando UFC..."):
                        try:
                            resultado = st.session_state.motores['ufc']({
                                "peleador1": p1_nombre,
                                "peleador2": p2_nombre
                            })
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

    # ==================== FÚTBOL TAB ====================
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
                                    if st.session_state.gemini:
                                        gemini_resp = st.session_state.gemini.orquestrar_decision_final("FÚTBOL", p, resultado)
                                        st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                                        st.info(gemini_resp)
                                except Exception as e:
                                    st.error(f"Error en análisis Fútbol: {e}")
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    # ==================== MLB TAB ====================
    with tab4:
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                accion = st.session_state.visual_mlb.render(p, idx, st.session_state.tracker, None, None, None)
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB..."):
                        try:
                            resultado = st.session_state.motores['mlb'](p)
                            render_analisis_card(resultado)
                            if resultado.get('top_hr_local') or resultado.get('top_hr_visit'):
                                st.markdown("### ⚾ CANDIDATOS A HOME RUN")
                                mostrar_player_props_mlb(resultado)
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
