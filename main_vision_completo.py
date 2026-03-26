# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - Versión para Streamlit Cloud
Ejecuta scrapers automáticamente al iniciar
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

# ==================== FUNCIONES DE ACTUALIZACIÓN ====================
def actualizar_odds_ufc():
    """Ejecuta scraper de odds UFC"""
    try:
        from scraper_odds_ufc_definitivo import actualizar_odds_ufc as scraper_odds
        st.info("🔄 Actualizando odds de UFC...")
        odds = scraper_odds()
        return odds
    except Exception as e:
        st.warning(f"⚠️ No se pudieron actualizar odds UFC: {e}")
        return {}

def actualizar_datos_ufc():
    """Ejecuta scraper de datos de peleadores UFC"""
    try:
        from scraper_ufc_final import actualizar_ufc as scraper_ufc
        st.info("🔄 Actualizando datos de peleadores UFC...")
        scraper_ufc()
        return True
    except Exception as e:
        st.warning(f"⚠️ No se pudieron actualizar datos UFC: {e}")
        return False

# ==================== INICIALIZACIÓN CON SCRAPERS ====================
def inicializar_datos():
    """Inicializa datos ejecutando scrapers"""
    st.info("🚀 Inicializando BETTING AI NEON...")
    
    # Crear carpetas necesarias
    os.makedirs("data", exist_ok=True)
    
    # Ejecutar scrapers en segundo plano
    with st.spinner("🔄 Actualizando datos de peleadores UFC..."):
        actualizar_datos_ufc()
    
    with st.spinner("🔄 Actualizando odds de UFC..."):
        actualizar_odds_ufc()

# ============================================
# FUNCIONES AUXILIARES
# ============================================
def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        return ""

def obtener_peleador_detalle(nombre):
    try:
        conn = sqlite3.connect('data/betting_stats.db')
        c = conn.cursor()
        c.execute("""
            SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling, odds
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
                'grappling': row[7] if row[7] else 0.5,
                'odds': row[8] if row[8] else 'N/A'
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
        # Ejecutar scrapers al iniciar
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
        
        st.session_state.analizador_mlb = MotorMLBPro()
        st.session_state.analizador_premium = AnalizadorPremiumProfesional()
        st.session_state.analizador_futbol_premium = AnalizadorFutbolPremium()
        st.session_state.ufc_aggregator = UFCDataAggregator()
        st.session_state.analizador_ufc_premium = AnalizadorUFCPremium()
        st.session_state.analizador_ufc_ko = AnalizadorUFCKOPro()
        st.session_state.visual_ufc_ko = VisualUFCKO()
        st.session_state.analizador_ufc_maestro = AnalizadorUFCMaestro()
        st.session_state.analizador_props = AnalizadorNBAProps()
        st.session_state.visual_props = VisualNBAProps()
        st.session_state.gestor_ligas = GestorLigasUniversal()
        
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
        st.session_state.ufc_analisis_heur = {}
        st.session_state.ufc_analisis_gemini = {}
        st.session_state.futbol_analisis_heur = {}
        st.session_state.futbol_analisis_gemini = {}
        st.session_state.mlb_analisis = {}
        st.session_state.mlb_analisis_gemini = {}
        st.session_state.init = True

    with st.sidebar:
        st.header("⚙️ CONTROLES")
        st.session_state.tracker.render_sidebar_tracker()
        st.markdown("---")
        
        # Botón para actualizar manualmente
        if st.button("🔄 ACTUALIZAR ODDS UFC", use_container_width=True):
            with st.spinner("Actualizando odds..."):
                actualizar_odds_ufc()
                st.success("✅ Odds actualizados")

        if st.button("🏀 CARGAR NBA", use_container_width=True):
            with st.spinner("Cargando NBA..."):
                st.session_state.nba_partidos = st.session_state.scrapers['nba'].get_games()
                if st.session_state.nba_partidos:
                    st.success(f"✅ {len(st.session_state.nba_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos NBA hoy")

        if st.button("⚾ CARGAR MLB", use_container_width=True):
            with st.spinner("Cargando MLB..."):
                partidos = st.session_state.scrapers['mlb'].get_games()
                st.session_state.mlb_partidos = partidos
                if st.session_state.mlb_partidos:
                    st.success(f"✅ {len(st.session_state.mlb_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos MLB hoy")

        if st.button("🥊 CARGAR UFC", use_container_width=True):
            with st.spinner("Cargando UFC..."):
                combates = st.session_state.scrapers['ufc'].get_events()
                st.session_state.ufc_combates = combates
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
                        st.session_state.futbol_partidos[liga] = partidos
                        st.success(f"✅ {len(partidos)} partidos")

        if st.button("🧹 LIMPIAR CACHÉ", use_container_width=True):
            st.session_state.futbol_partidos = {}
            st.rerun()

        if st.button("🔄 RESET TOTAL", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs(["🏀 NBA", "🥊 UFC", "⚽ FÚTBOL", "⚾ MLB"])

    # ==================== TAB NBA ====================
    with tab1:
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                key = f"nba_{p['local']}_{p['visitante']}_{idx}"
                analisis_heur = st.session_state.nba_analisis_heur.get(key)
                analisis_gemini = st.session_state.nba_analisis_gemini.get(key)
                
                accion = st.session_state.visual_nba.render(
                    p, idx, st.session_state.tracker,
                    analisis_heuristico=analisis_heur,
                    analisis_gemini=analisis_gemini,
                    analisis_premium=None
                )
                
                if accion == "analizar":
                    with st.spinner("🏀 Analizando con Motor V17..."):
                        integrador = st.session_state.integrador_v17
                        fecha_hoy = datetime.now().strftime("%Y%m%d")
                        linea_ou = p.get('odds', {}).get('over_under', 225.0)
                        prediccion = integrador.predecir_partido(p['local'], p['visitante'], fecha_hoy, linea_ou)
                        
                        if prediccion.get('status') == 'OK':
                            resultado = {
                                'recomendacion': prediccion.get('over_under', {}).get('pick', 'N/A'),
                                'ev_mejor': prediccion.get('over_under', {}).get('ev_pct', 0),
                                'confianza': prediccion.get('over_under', {}).get('confianza', 0),
                                'total_proyectado': prediccion.get('proyecciones', {}).get('total', 0),
                                'etiqueta_verde': prediccion.get('etiqueta_verde', False),
                                'detalle': prediccion.get('proyecciones', {}).get('detalle', '')
                            }
                            st.session_state.nba_analisis_heur[key] = resultado
                            
                            if st.session_state.analizador_gemini:
                                decision_gemini = st.session_state.analizador_gemini.analizar_con_decision(p, resultado)
                                st.session_state.nba_analisis_gemini[key] = decision_gemini
                            st.success("✅ Análisis completado")
                        else:
                            st.warning(prediccion.get('msg', 'No se pudo analizar'))
                    st.rerun()
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
                
                analisis_heur = st.session_state.ufc_analisis_heur.get(key)
                analisis_gemini = st.session_state.ufc_analisis_gemini.get(key)
                
                accion = st.session_state.visual_ufc.render(
                    c, idx, st.session_state.tracker,
                    analisis=analisis_heur
                )
                
                if accion == "analizar":
                    with st.spinner("🥊 Analizando UFC con odds reales..."):
                        analizador = AnalizadorUFCFinal(p1_nombre, p2_nombre)
                        resultado = analizador.analizar()
                        st.session_state.ufc_analisis_heur[key] = resultado
                        
                        if st.session_state.analizador_ufc_gemini:
                            decision_gemini = st.session_state.analizador_ufc_gemini.analizar(
                                resultado.get('stats_p1', {}),
                                resultado.get('stats_p2', {}),
                                resultado.get('factor_clave', '')
                            )
                            st.session_state.ufc_analisis_gemini[key] = decision_gemini
                        elif st.session_state.analizador_gemini:
                            decision_gemini = st.session_state.analizador_gemini.orquestrar_decision_final(
                                deporte="ufc",
                                partido=c,
                                analisis_heuristico=resultado
                            )
                            st.session_state.ufc_analisis_gemini[key] = decision_gemini
                        
                        st.success("✅ Análisis completado")
                        st.rerun()
                
                if analisis_heur:
                    stats1 = analisis_heur.get('stats_p1', {})
                    stats2 = analisis_heur.get('stats_p2', {})
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🔴 {p1_nombre}**")
                        st.caption(f"📊 Record: {stats1.get('record', 'N/A')}")
                        st.caption(f"📏 Altura: {stats1.get('altura_cm', 0)} cm")
                        st.caption(f"📏 Alcance: {stats1.get('alcance_cm', 0)} cm")
                        st.caption(f"💥 KO Rate: {stats1.get('ko_rate', 0)}%")
                        st.caption(f"🎲 Odds: {analisis_heur.get('odds_p1', 'N/A')}")
                        if analisis_heur.get('ev_p1', 0) > 0:
                            st.caption(f"📈 EV: +{analisis_heur.get('ev_p1', 0)}%")
                    
                    with col2:
                        st.markdown(f"**🔵 {p2_nombre}**")
                        st.caption(f"📊 Record: {stats2.get('record', 'N/A')}")
                        st.caption(f"📏 Altura: {stats2.get('altura_cm', 0)} cm")
                        st.caption(f"📏 Alcance: {stats2.get('alcance_cm', 0)} cm")
                        st.caption(f"💥 KO Rate: {stats2.get('ko_rate', 0)}%")
                        st.caption(f"🎲 Odds: {analisis_heur.get('odds_p2', 'N/A')}")
                        if analisis_heur.get('ev_p2', 0) > 0:
                            st.caption(f"📈 EV: +{analisis_heur.get('ev_p2', 0)}%")
                    
                    st.markdown("---")
                    
                    recomendacion = analisis_heur.get('recomendacion', 'N/A')
                    confianza = analisis_heur.get('confianza', 0)
                    metodo = analisis_heur.get('metodo', 'Decision')
                    factor_clave = analisis_heur.get('factor_clave', '')
                    factor_adicional = analisis_heur.get('factor_adicional', '')
                    etiqueta_verde = analisis_heur.get('etiqueta_verde', False)
                    
                    color = "#00ff41" if "GANA" in recomendacion else "#ff6600"
                    icono = "🏆" if "GANA" in recomendacion else "🥊"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1a1f2a 0%, #0f1419 100%); 
                                border-radius: 12px; 
                                padding: 20px; 
                                margin: 15px 0; 
                                border-left: 4px solid {color};'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='color: #888; font-size: 12px;'>RECOMENDACION</span>
                                <h3 style='color: {color}; margin: 0;'>{icono} {recomendacion}</h3>
                                <p style='color: #888; font-size: 11px; margin: 5px 0 0;'>{factor_clave}</p>
                                <p style='color: #ff6600; font-size: 10px; margin: 3px 0 0;'>{factor_adicional}</p>
                            </div>
                            <div style='text-align: center;'>
                                <span style='color: #888; font-size: 12px;'>CONFIANZA</span>
                                <h3 style='color: #00ff41; margin: 0;'>{confianza}%</h3>
                            </div>
                            <div style='text-align: center;'>
                                <span style='color: #888; font-size: 12px;'>METODO</span>
                                <h3 style='color: #ff6600; margin: 0;'>{metodo}</h3>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(confianza / 100)
                    
                    if etiqueta_verde:
                        st.success("🔥 PICK DE ALTA CONFIANZA - Valor positivo detectado")
                
                if analisis_gemini:
                    st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                    st.info(analisis_gemini)
                
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
                        
                        accion = st.session_state.visual_futbol.render(
                            p, idx, liga, st.session_state.tracker,
                            stats_data=None,
                            analisis_heurístico=analisis_heur,
                            analisis_gemini=analisis_gemini,
                            analisis_premium=None
                        )
                        
                        if accion == "analizar":
                            with st.spinner("⚽ Analizando Fútbol..."):
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
                        st.markdown("---")
        else:
            st.info("👈 Carga ligas en el sidebar")

    # ==================== TAB MLB ====================
    with tab4:
        if st.session_state.mlb_partidos:
            for idx, p in enumerate(st.session_state.mlb_partidos):
                key = f"mlb_{p['local']}_{p['visitante']}_{idx}"
                analisis = st.session_state.mlb_analisis.get(key)
                analisis_gemini = st.session_state.mlb_analisis_gemini.get(key) if hasattr(st.session_state, 'mlb_analisis_gemini') else None
                
                accion = st.session_state.visual_mlb.render(
                    p, idx, st.session_state.tracker,
                    analisis=analisis,
                    stats_local=None,
                    stats_visit=None
                )
                
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB..."):
                        res = st.session_state.analizador_mlb.analizar_partido(p)
                        st.session_state.mlb_analisis[key] = res
                        
                        if st.session_state.analizador_gemini:
                            decision_gemini = st.session_state.analizador_gemini.analizar_con_decision(p, res)
                            st.session_state.mlb_analisis_gemini[key] = decision_gemini
                        st.rerun()
                
                if analisis:
                    st.markdown("---")
                    recomendacion = analisis.get('recomendacion', 'N/A')
                    confianza = analisis.get('confianza', 0)
                    total_proyectado = analisis.get('total_proyectado', 0)
                    proyeccion_local = analisis.get('proyeccion_local', 0)
                    proyeccion_visitante = analisis.get('proyeccion_visitante', 0)
                    
                    if "OVER" in recomendacion:
                        icono = "📈"
                        color = "#00ff41"
                    elif "UNDER" in recomendacion:
                        icono = "📉"
                        color = "#ff6600"
                    else:
                        icono = "⚾"
                        color = "#ff6600"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1a1f2a 0%, #0f1419 100%); 
                                border-radius: 12px; 
                                padding: 20px; 
                                margin: 15px 0; 
                                border-left: 4px solid {color};'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='color: #888; font-size: 12px;'>RECOMENDACION</span>
                                <h3 style='color: {color}; margin: 0;'>{icono} {recomendacion}</h3>
                            </div>
                            <div style='text-align: center;'>
                                <span style='color: #888; font-size: 12px;'>CONFIANZA</span>
                                <h3 style='color: #00ff41; margin: 0;'>{confianza}%</h3>
                            </div>
                            <div style='text-align: center;'>
                                <span style='color: #888; font-size: 12px;'>TOTAL IA</span>
                                <h3 style='color: #ff6600; margin: 0;'>{total_proyectado}</h3>
                            </div>
                        </div>
                        <div style='margin-top: 10px;'>
                            <span style='color: #888; font-size: 11px;'>Proyección: {proyeccion_local:.1f} - {proyeccion_visitante:.1f} carreras</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(confianza / 100)
                    
                    if analisis.get('etiqueta_verde', False):
                        st.success("🔥 PICK DE ALTA CONFIANZA - Valor positivo detectado")
                
                if analisis_gemini:
                    st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                    st.info(analisis_gemini)
                
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
