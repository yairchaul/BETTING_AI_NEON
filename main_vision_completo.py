# -*- coding: utf-8 -*-
"""
MAIN VISION COMPLETO - NEON V20 (Motores adaptados y estables)
Fusión de ambas versiones con mejoras
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

# ==================== MOTORES v20 (con fallbacks seguros) ====================
# NBA
try:
    from motor_nba_pro_v17 import analizar_nba_pro_v17, backtest_nba_pro_v17
except ImportError:
    analizar_nba_pro_v17 = None
    backtest_nba_pro_v17 = None
    logger.warning("motor_nba_pro_v17 no disponible")

# MLB
try:
    from motor_mlb_pro import analizar_mlb_pro_v20
except ImportError:
    analizar_mlb_pro_v20 = None
    logger.warning("motor_mlb_pro no disponible")

# UFC
try:
    from motor_ufc_pro import analizar_ufc_pro_v20
except ImportError:
    analizar_ufc_pro_v20 = None
    logger.warning("motor_ufc_pro no disponible")

# Fútbol
try:
    from motor_fut_pro import analizar_futbol_pro_v20, backtest_futbol_pro_v20
except ImportError:
    analizar_futbol_pro_v20 = None
    backtest_futbol_pro_v20 = None
    logger.warning("motor_fut_pro no disponible")

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
    """Inicializa datos al arrancar la app"""
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

def obtener_peleador_detalle(nombre):
    """Obtiene datos de peleador UFC desde BD"""
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

# ==================== CONFIGURACIÓN DE PÁGINA ====================
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
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')} - Motores v20")

GEMINI_API_KEY = get_gemini_api_key()
GEMINI_DISPONIBLE = bool(GEMINI_API_KEY)

if GEMINI_DISPONIBLE:
    st.success("✅ Gemini conectado - Decisor Final activo")
else:
    st.warning("⚠️ Gemini no disponible - Solo análisis matemático")

LIGAS_FUTBOL = ESPNLeagueCodes.obtener_todas()

# ==================== MAIN ====================
def main():
    if 'init' not in st.session_state:
        # Inicializar datos
        inicializar_datos()
        
        # Scrapers
        st.session_state.scrapers = {
            'nba': ESPN_NBA(),
            'mlb': ESPN_MLB(),
            'ufc': ESPN_UFC(),
            'futbol': ESPN_FUTBOL()
        }
        
        # Trackers y visuales
        st.session_state.tracker = BetTracker()
        st.session_state.visual_nba = VisualNBAMejorado()
        st.session_state.visual_ufc = VisualUFCFinal()
        st.session_state.visual_futbol = VisualFutbolTriple()
        st.session_state.visual_mlb = VisualMLB()
        
        # Analizadores adicionales
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
        
        # Gemini
        if GEMINI_API_KEY:
            st.session_state.analizador_gemini = AnalizadorGeminiNBA(GEMINI_API_KEY)
            st.session_state.analizador_ufc_gemini = AnalizadorUFCGemini(GEMINI_API_KEY)
            st.session_state.analizador_futbol_gemini_mejorado = AnalizadorFutbolGeminiMejorado(GEMINI_API_KEY)
        else:
            st.session_state.analizador_gemini = None
            st.session_state.analizador_ufc_gemini = None
            st.session_state.analizador_futbol_gemini_mejorado = None
        
        # Motores v20
        st.session_state.motores_v20 = {
            'nba': analizar_nba_pro_v17,
            'mlb': analizar_mlb_pro_v20,
            'ufc': analizar_ufc_pro_v20,
            'futbol': analizar_futbol_pro_v20
        }
        
        # Almacenamiento de datos
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
        st.session_state.init = True

    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.header("⚙️ CONTROLES")
        st.session_state.tracker.render_sidebar_tracker()
        st.markdown("---")
        
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
        
        st.markdown("---")
        st.subheader("🔥 MOTORES v20")
        if st.button("📊 Backtest RÁPIDO", use_container_width=True):
            with st.spinner("Corriendo backtests..."):
                bt_nba = backtest_nba_pro_v17([]) if backtest_nba_pro_v17 else {'precision': 0}
                bt_fut = backtest_futbol_pro_v20([]) if backtest_futbol_pro_v20 else {'precision': 0}
                st.success(f"""
                🏀 NBA: Precisión **{bt_nba['precision']}%**  
                ⚽ FÚTBOL: Precisión **{bt_fut['precision']}%**
                """)

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
                    with st.spinner("🏀 Analizando NBA con Motor v20..."):
                        if st.session_state.motores_v20['nba']:
                            resultado = st.session_state.motores_v20['nba']({
                                "home": p.get('local', ''),
                                "away": p.get('visitante', ''),
                                "odds": p.get('odds', {})
                            })
                            st.session_state.nba_analisis_heur[key] = resultado
                            
                            if st.session_state.analizador_gemini:
                                decision_gemini = st.session_state.analizador_gemini.analizar_con_decision(p, resultado)
                                st.session_state.nba_analisis_gemini[key] = decision_gemini
                            
                            render_analisis_card(resultado)
                            st.success("✅ Análisis completado")
                        else:
                            st.error("Motor NBA no disponible")
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
                
                datos_p1 = obtener_peleador_detalle(p1_nombre) if p1_nombre else None
                datos_p2 = obtener_peleador_detalle(p2_nombre) if p2_nombre else None
                
                analisis_heur = st.session_state.ufc_analisis_heur.get(key)
                analisis_gemini = st.session_state.ufc_analisis_gemini.get(key)
                
                accion = st.session_state.visual_ufc.render(
                    c, idx, st.session_state.tracker,
                    analisis=analisis_heur
                )
                
                if accion == "analizar":
                    with st.spinner("🥊 Analizando UFC con Motor v20..."):
                        if st.session_state.motores_v20['ufc'] and datos_p1 and datos_p2:
                            resultado = st.session_state.motores_v20['ufc']({
                                "peleador1": p1_nombre,
                                "peleador2": p2_nombre
                            })
                            st.session_state.ufc_analisis_heur[key] = resultado
                            
                            if st.session_state.analizador_ufc_gemini:
                                decision_gemini = st.session_state.analizador_ufc_gemini.analizar(datos_p1, datos_p2, resultado)
                                st.session_state.ufc_analisis_gemini[key] = decision_gemini
                            elif st.session_state.analizador_gemini:
                                decision_gemini = st.session_state.analizador_gemini.orquestrar_decision_final(
                                    deporte="ufc",
                                    partido=c,
                                    analisis_heuristico=resultado
                                )
                                st.session_state.ufc_analisis_gemini[key] = decision_gemini
                            
                            render_analisis_card(resultado)
                            st.success("✅ Análisis completado")
                        else:
                            st.error("Motor UFC no disponible o datos insuficientes")
                    st.rerun()
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
                            with st.spinner("⚽ Analizando Fútbol con Motor v20..."):
                                if st.session_state.motores_v20['futbol']:
                                    resultado = st.session_state.motores_v20['futbol']({
                                        "home": p.get('local', ''),
                                        "away": p.get('visitante', ''),
                                        "odds": p.get('odds', {})
                                    })
                                    st.session_state.futbol_analisis_heur[key] = resultado
                                    
                                    if st.session_state.analizador_futbol_gemini_mejorado:
                                        decision_gemini = st.session_state.analizador_futbol_gemini_mejorado.analizar(p, {}, {}, {})
                                        st.session_state.futbol_analisis_gemini[key] = decision_gemini
                                    
                                    render_analisis_card(resultado)
                                    st.success("✅ Análisis completado")
                                else:
                                    st.error("Motor Fútbol no disponible")
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
                
                accion = st.session_state.visual_mlb.render(
                    p, idx, st.session_state.tracker,
                    analisis=analisis,
                    stats_local=None,
                    stats_visit=None
                )
                
                if accion == "analizar":
                    with st.spinner("⚾ Analizando MLB con Motor v20..."):
                        if st.session_state.motores_v20['mlb']:
                            resultado = st.session_state.motores_v20['mlb']({
                                "home": p.get('local', ''),
                                "away": p.get('visitante', ''),
                                "odds": p.get('odds', {})
                            })
                            st.session_state.mlb_analisis[key] = resultado
                            render_analisis_card(resultado)
                            st.success("✅ Análisis completado")
                        else:
                            st.error("Motor MLB no disponible")
                    st.rerun()
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
    except:
        pass

if __name__ == "__main__":
    main()
