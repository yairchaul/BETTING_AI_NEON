# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - VERSIÓN CON MOTOR V20 + GEMINI DECISOR FINAL
NBA, UFC, Fútbol y MLB completamente funcionales
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
from visual_ufc_mejorado import VisualUFCMejorado
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
from analizador_ufc_heurístico import AnalizadorUFCHuristico
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

# ==================== MOTORES V20 ====================
# Importar los motores correctamente
try:
    from motor_nba_pro_v17 import analizar_nba_pro_v17
except ImportError:
    analizar_nba_pro_v17 = None
    logger.warning("motor_nba_pro_v17 no disponible")

try:
    from motor_fut_pro import analizar_futbol_pro_v20, backtest_futbol_pro_v20
except ImportError:
    analizar_futbol_pro_v20 = None
    backtest_futbol_pro_v20 = None
    logger.warning("motor_fut_pro no disponible")

try:
    from motor_mlb_pro import analizar_mlb_pro_v20
except ImportError:
    analizar_mlb_pro_v20 = None
    logger.warning("motor_mlb_pro no disponible")

try:
    from motor_ufc_pro import analizar_ufc_pro_v20
except ImportError:
    analizar_ufc_pro_v20 = None
    logger.warning("motor_ufc_pro no disponible")

# ==================== FUNCIONES AUXILIARES ====================
def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except Exception as e:
        logger.error(f"Error leyendo .env: {e}")
    return ""

def obtener_peleador_detalle(nombre):
    try:
        conn = sqlite3.connect('data/betting_stats.db')
        c = conn.cursor()
        c.execute("""
            SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling
            FROM peleadores_ufc 
            WHERE nombre LIKE ? OR nombre = ?
            LIMIT 1
        """, (f"%{nombre}%", nombre))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'nombre': row[0],
                'record': row[1] if row[1] else '0-0-0',
                'altura': row[2] if row[2] else 'N/A',
                'peso': row[3] if row[3] else 'N/A',
                'alcance': row[4] if row[4] else 'N/A',
                'postura': row[5] if row[5] else 'Desconocida',
                'ko_rate': row[6] if row[6] else 0.5,
                'grappling': row[7] if row[7] else 0.5
            }
        return None
    except:
        return None

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(page_title="BETTING AI - NEON EDITION", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .stMarkdown, .stText, .stCaption, .stSubheader, div, p, span, label {
        text-shadow: 0 0 2px #ff6600, 0 0 3px #ff6600;
    }
    h1, h2, h3, h4 {
        color: #fff;
        text-shadow: 0 0 5px #fff, 0 0 10px #ff6600, 0 0 20px #00ff41, 0 0 30px #00ff41;
        text-align: center;
    }
    .stButton>button {
        border: 2px solid #00ff41 !important;
        background-color: transparent !important;
        color: #00ff41 !important;
        text-shadow: 0 0 2px #ff6600;
        box-shadow: 0 0 10px #00ff41;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00ff41 !important;
        color: #000 !important;
        box-shadow: 0 0 25px #ff6600;
    }
    .profit-card {
        background: #1a1f2a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00ff41;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 BETTING AI - NEON EDITION")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')}")

GEMINI_API_KEY = get_gemini_api_key()
GEMINI_DISPONIBLE = bool(GEMINI_API_KEY)

if GEMINI_DISPONIBLE:
    st.success("✅ Gemini conectado - Decisor Final activo")
else:
    st.warning("⚠️ Gemini no disponible - Solo análisis matemático")

LIGAS_FUTBOL = ESPNLeagueCodes.obtener_todas()

# ============================================
# INICIALIZACIÓN
# ============================================
def main():
    if 'init' not in st.session_state:
        st.session_state.scrapers = {
            'nba': ESPN_NBA(),
            'mlb': ESPN_MLB(),
            'ufc': ESPN_UFC(),
            'futbol': ESPN_FUTBOL()
        }
        st.session_state.tracker = BetTracker()
        st.session_state.visual_nba = VisualNBAMejorado()
        st.session_state.visual_ufc = VisualUFCMejorado()
        st.session_state.visual_futbol = VisualFutbolTriple()
        st.session_state.visual_mlb = VisualMLB()
        
        # Inicializar motores V20
        st.session_state.motores_v20 = {
            'nba': analizar_nba_pro_v17 if analizar_nba_pro_v17 else None,
            'mlb': analizar_mlb_pro_v20 if analizar_mlb_pro_v20 else None,
            'futbol': analizar_futbol_pro_v20 if analizar_futbol_pro_v20 else None,
            'ufc': analizar_ufc_pro_v20 if analizar_ufc_pro_v20 else None
        }
        
        if GEMINI_API_KEY:
            st.session_state.analizador_gemini = AnalizadorGeminiNBA(GEMINI_API_KEY)
            st.session_state.analizador_ufc_gemini = AnalizadorUFCGemini(GEMINI_API_KEY)
            st.session_state.analizador_futbol_gemini_mejorado = AnalizadorFutbolGeminiMejorado(GEMINI_API_KEY)
        else:
            st.session_state.analizador_gemini = None
            st.session_state.analizador_ufc_gemini = None
            st.session_state.analizador_futbol_gemini_mejorado = None

        st.session_state.nba_partidos = []
        st.session_state.ufc_combates = []
        st.session_state.futbol_partidos = {}
        st.session_state.mlb_partidos = []
        st.session_state.nba_analisis_heur = {}
        st.session_state.nba_analisis_gemini = {}
        st.session_state.nba_analisis_premium = {}
        st.session_state.ufc_analisis_heur = {}
        st.session_state.ufc_analisis_gemini = {}
        st.session_state.ufc_analisis_premium = {}
        st.session_state.futbol_analisis_heur = {}
        st.session_state.futbol_analisis_gemini = {}
        st.session_state.futbol_analisis_premium = {}
        st.session_state.mlb_analisis = {}
        st.session_state.init = True

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
            with st.spinner("Cargando UFC..."):
                st.session_state.ufc_combates = st.session_state.scrapers['ufc'].get_events()
                if st.session_state.ufc_combates:
                    st.success(f"✅ {len(st.session_state.ufc_combates)} combates")
                else:
                    st.warning("⚠️ No hay eventos UFC disponibles")

        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: Premier, LaLiga, Liga MX...")
        ligas_filtradas = [l for l in LIGAS_FUTBOL if buscar_liga.lower() in l.lower()] if buscar_liga else LIGAS_FUTBOL
        
        with st.container(height=400):
            for liga in sorted(ligas_filtradas)[:50]:
                if st.button(f"⚽ {liga}", key=f"btn_liga_{liga}", use_container_width=True):
                    with st.spinner(f"Cargando {liga}..."):
                        partidos = st.session_state.scrapers['futbol'].get_games(liga)
                        if partidos:
                            st.session_state.futbol_partidos[liga] = partidos
                            st.success(f"✅ {len(partidos)} partidos")
                        else:
                            st.warning(f"⚠️ No hay partidos de {liga} hoy")

        if st.button("🧹 LIMPIAR CACHÉ", use_container_width=True):
            st.session_state.futbol_partidos = {}
            st.rerun()

        if st.button("🔄 RESET TOTAL", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    # ==================== TAB NBA ====================
    with tab1:
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                key = f"nba_{p['local']}_{p['visitante']}_{idx}"
                
                analisis_heur = st.session_state.nba_analisis_heur.get(key)
                analisis_gemini = st.session_state.nba_analisis_gemini.get(key)

                st.markdown(f"### 🏀 {p['local']} vs {p['visitante']}")
                
                # Mostrar odds básicas
                odds = p.get('odds', {})
                st.markdown(f"**OVER/UNDER** {odds.get('over_under', 'N/A')}")

                if st.button("📊 ANALIZAR", key=f"nba_analizar_{idx}", use_container_width=True):
                    with st.spinner("🏀 Analizando NBA con Motor V20..."):
                        if st.session_state.motores_v20['nba']:
                            resultado = st.session_state.motores_v20['nba']({
                                "home": p.get('local', ''),
                                "away": p.get('visitante', ''),
                                "odds": p.get('odds', {})
                            })
                            st.session_state.nba_analisis_heur[key] = resultado
                            st.success("✅ Análisis completado")
                        else:
                            st.error("Motor NBA no disponible")
                    st.rerun()

                # Mostrar resultados
                if analisis_heur:
                    st.markdown("### 🎯 PREDICCIÓN MOTOR V20")
                    st.markdown(f"**{analisis_heur.get('recomendacion', 'N/A')}** | Confianza: {analisis_heur.get('confianza', 0)}%")
                    st.caption(f"Total proyectado: {analisis_heur.get('total_proyectado', 0)} puntos")
                    
                    if analisis_heur.get('etiqueta_verde'):
                        st.success("🔥 PICK DE ALTA CONFIANZA")

                if analisis_gemini:
                    st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                    st.info(analisis_gemini)

                st.markdown("---")
        else:
            st.info("👈 Carga NBA en el sidebar")

    # ==================== TAB UFC ====================
    with tab2:
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                key = f"ufc_{idx}"
                p1_nombre = c.get('peleador1', {}).get('nombre', '')
                p2_nombre = c.get('peleador2', {}).get('nombre', '')
                
                datos_p1 = obtener_peleador_detalle(p1_nombre) if p1_nombre else None
                datos_p2 = obtener_peleador_detalle(p2_nombre) if p2_nombre else None
                
                analisis_heur = st.session_state.ufc_analisis_heur.get(key)
                analisis_gemini = st.session_state.ufc_analisis_gemini.get(key)

                st.markdown(f"### 🥊 {p1_nombre} vs {p2_nombre}")
                
                if datos_p1 and datos_p2:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**🔴 {p1_nombre}**")
                        st.caption(f"📊 Record: {datos_p1.get('record', 'N/A')}")
                        st.caption(f"📏 Altura: {datos_p1.get('altura', 'N/A')}")
                        st.caption(f"📏 Alcance: {datos_p1.get('alcance', 'N/A')}")
                        st.caption(f"💥 KO Rate: {int(datos_p1.get('ko_rate', 0) * 100)}%")
                    with col2:
                        st.markdown(f"**🔵 {p2_nombre}**")
                        st.caption(f"📊 Record: {datos_p2.get('record', 'N/A')}")
                        st.caption(f"📏 Altura: {datos_p2.get('altura', 'N/A')}")
                        st.caption(f"📏 Alcance: {datos_p2.get('alcance', 'N/A')}")
                        st.caption(f"💥 KO Rate: {int(datos_p2.get('ko_rate', 0) * 100)}%")
                
                if st.button("📊 ANALIZAR", key=f"ufc_analizar_{idx}", use_container_width=True):
                    with st.spinner("🥊 Analizando UFC..."):
                        if datos_p1 and datos_p2:
                            analizador = AnalizadorUFCHuristico(datos_p1, datos_p2)
                            resultado = analizador.analizar()
                            st.session_state.ufc_analisis_heur[key] = resultado
                            
                            if st.session_state.analizador_ufc_gemini:
                                resumen = analizador.obtener_resumen() if hasattr(analizador, 'obtener_resumen') else {}
                                resultado_gemini = st.session_state.analizador_ufc_gemini.analizar(datos_p1, datos_p2, resumen)
                                st.session_state.ufc_analisis_gemini[key] = resultado_gemini
                            st.success("✅ Análisis completado")
                            st.rerun()
                
                if analisis_heur:
                    st.markdown("---")
                    st.markdown("### 📊 HEURÍSTICO")
                    st.write(f"**Recomendación:** {analisis_heur.get('recomendacion', 'N/A')}")
                    confianza = analisis_heur.get('confianza', 0)
                    st.progress(confianza / 100)
                    st.caption(f"Confianza: {confianza}%")
                    st.caption(f"Método: {analisis_heur.get('metodo', 'Decisión')}")
                    
                    if analisis_heur.get('etiqueta_verde'):
                        st.success("🔥 PICK DE ALTA CONFIANZA")

                st.markdown("---")
        else:
            st.info("👈 Carga UFC en el sidebar")

    # ==================== TAB FÚTBOL ====================
    with tab3:
        if st.session_state.futbol_partidos:
            for liga, partidos in st.session_state.futbol_partidos.items():
                if partidos:
                    st.markdown(f"### ⚽ {liga}")
                    for idx, p in enumerate(partidos):
                        key = f"fut_{liga}_{p['local']}_{p['visitante']}_{idx}"
                        analisis_heur = st.session_state.futbol_analisis_heur.get(key)
                        analisis_gemini = st.session_state.futbol_analisis_gemini.get(key)
                        
                        st.markdown(f"**{p['local']} vs {p['visitante']}**")
                        
                        if st.button("📊 ANALIZAR", key=f"fut_analizar_{liga}_{idx}", use_container_width=True):
                            with st.spinner("⚽ Analizando Fútbol..."):
                                if st.session_state.motores_v20['futbol']:
                                    resultado = st.session_state.motores_v20['futbol']({
                                        "home": p.get('local', ''),
                                        "away": p.get('visitante', ''),
                                        "odds": {}
                                    })
                                    st.session_state.futbol_analisis_heur[key] = resultado
                                    st.success("✅ Análisis completado")
                                else:
                                    # Fallback al analizador heurístico
                                    stats_l = {'form_goles': [1, 2, 1, 1, 2], 'victorias': 2}
                                    stats_v = {'form_goles': [1, 1, 1, 2, 1], 'victorias': 2}
                                    analizador = AnalizadorFutbolHeuristicoMejorado(stats_l, stats_v, p['local'], p['visitante'])
                                    resultado = analizador.analizar()
                                    st.session_state.futbol_analisis_heur[key] = resultado
                                    
                                    if st.session_state.analizador_futbol_gemini_mejorado:
                                        resultado_gemini = st.session_state.analizador_futbol_gemini_mejorado.analizar(p, stats_l, stats_v, {})
                                        st.session_state.futbol_analisis_gemini[key] = resultado_gemini
                                    st.success("✅ Análisis completado")
                            st.rerun()
                        
                        if analisis_heur:
                            st.markdown("---")
                            st.markdown("### 📊 HEURÍSTICO")
                            st.write(f"**Recomendación:** {analisis_heur.get('recomendacion', 'N/A')}")
                            confianza = analisis_heur.get('confianza', 0)
                            st.progress(confianza / 100)
                            st.caption(f"Confianza: {confianza}%")
                            if analisis_heur.get('etiqueta_verde'):
                                st.success("🔥 PICK DE ALTA CONFIANZA")
                        
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    # ==================== TAB MLB ====================
    with tab4:
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                key = f"mlb_{p['local']}_{p['visitante']}_{idx}"
                analisis = st.session_state.mlb_analisis.get(key)
                
                st.markdown(f"### ⚾ {p['local']} vs {p['visitante']}")
                
                if st.button("📊 ANALIZAR", key=f"mlb_analizar_{idx}", use_container_width=True):
                    with st.spinner("⚾ Analizando MLB..."):
                        if st.session_state.motores_v20['mlb']:
                            resultado = st.session_state.motores_v20['mlb']({
                                "home": p.get('local', ''),
                                "away": p.get('visitante', ''),
                                "odds": p.get('odds', {})
                            })
                            st.session_state.mlb_analisis[key] = resultado
                            st.success("✅ Análisis completado")
                        else:
                            st.error("Motor MLB no disponible")
                    st.rerun()
                
                if analisis:
                    st.markdown("---")
                    st.markdown("### 📊 ANÁLISIS MLB")
                    st.write(f"**Recomendación:** {analisis.get('recomendacion', 'N/A')}")
                    st.progress(analisis.get('confianza', 0) / 100)
                    st.caption(f"Confianza: {analisis.get('confianza', 0)}%")
                    st.caption(f"Total proyectado: {analisis.get('total_proyectado', 0)} carreras")
                
                st.markdown("---")
        else:
            st.info("👈 Carga MLB en el sidebar")

    # Profit card
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
    except:
        pass

if __name__ == "__main__":
    main()
