"""
MAIN VISION COMPLETO - CON TRES ANÁLISIS
"""
import streamlit as st
from datetime import datetime

from espn_data_pipeline import ESPNDataPipeline
from bet_tracker import BetTracker
from visual_nba_mejorado import VisualNBAMejorado
from visual_ufc import VisualUFC
from visual_futbol import VisualFutbol
from analizador_nba import AnalizadorNBA
from analizador_gemini_nba import AnalizadorGeminiNBA
from analizador_premium import AnalizadorPremium

# ============================================
# CONFIGURACIÓN
# ============================================
st.set_page_config(page_title="BETTING AI - TRIPLE ANÁLISIS", page_icon="🎯", layout="wide")

st.title("🎯 BETTING AI - Triple Análisis (Heurístico + Gemini + Premium)")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')}")

def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        return ""

GEMINI_API_KEY = get_gemini_api_key()

LIGAS_FUTBOL = [
    "México - Liga MX", "UEFA - Champions League", "La Liga",
    "Inglaterra - Premier League", "Bundesliga 1", "Serie A",
    "Ligue 1", "Holanda - Eredivisie", "Portugal - Primeira Liga",
    "México - Liga de Expansión MX"
]

def main():
    if 'init' not in st.session_state:
        st.session_state.espn = ESPNDataPipeline()
        st.session_state.tracker = BetTracker()
        st.session_state.visual_nba = VisualNBAMejorado()
        st.session_state.visual_ufc = VisualUFC()
        st.session_state.visual_futbol = VisualFutbol()
        st.session_state.analizador_premium = AnalizadorPremium()
        
        if GEMINI_API_KEY:
            st.session_state.analizador_gemini = AnalizadorGeminiNBA(GEMINI_API_KEY)
        else:
            st.session_state.analizador_gemini = None
        
        st.session_state.nba_partidos = []
        st.session_state.ufc_combates = []
        st.session_state.futbol_partidos = {}
        st.session_state.nba_analisis_heur = {}
        st.session_state.nba_analisis_gemini = {}
        st.session_state.nba_analisis_premium = {}
        
        st.session_state.init = True

    with st.sidebar:
        st.header("⚙️ CONTROLES")
        st.session_state.tracker.render_sidebar_tracker()
        st.markdown("---")
        
        if st.button("🏀 CARGAR NBA", use_container_width=True):
            with st.spinner("Cargando NBA..."):
                st.session_state.nba_partidos = st.session_state.espn.get_nba_games_with_odds()
                st.session_state.nba_analisis_heur = {}
                st.session_state.nba_analisis_gemini = {}
                st.session_state.nba_analisis_premium = {}
                st.success(f"✅ {len(st.session_state.nba_partidos)} partidos")
        
        if st.button("🥊 CARGAR UFC", use_container_width=True):
            with st.spinner("Cargando UFC..."):
                st.session_state.ufc_combates = st.session_state.espn.get_ufc_events()
                st.success(f"✅ {len(st.session_state.ufc_combates)} combates")
        
        st.markdown("---")
        st.subheader("⚽ FÚTBOL")
        for liga in LIGAS_FUTBOL:
            if st.button(f"⚽ {liga}", key=f"btn_{liga}", use_container_width=True):
                with st.spinner(f"Cargando {liga}..."):
                    partidos = st.session_state.espn.get_soccer_games_today(liga)
                    st.session_state.futbol_partidos[liga] = partidos
                    st.success(f"✅ {len(partidos)} partidos")

    tab1, tab2, tab3 = st.tabs(["🏀 NBA (TRIPLE ANÁLISIS)", "🥊 UFC", "⚽ FÚTBOL"])

    with tab1:
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                key = f"nba_{p['local']}_{p['visitante']}_{idx}"
                
                analisis_heur = st.session_state.nba_analisis_heur.get(key)
                analisis_gemini = st.session_state.nba_analisis_gemini.get(key)
                analisis_premium = st.session_state.nba_analisis_premium.get(key)
                
                accion = st.session_state.visual_nba.render(
                    p, idx,
                    tracker=st.session_state.tracker,
                    analisis_heurístico=analisis_heur,
                    analisis_gemini=analisis_gemini,
                    analisis_premium=analisis_premium
                )
                
                if accion == "analizar":
                    with st.spinner("📊 Ejecutando triple análisis..."):
                        # 1. Heurístico
                        analizador_heur = AnalizadorNBA(p)
                        resultado_heur = analizador_heur.analizar()
                        st.session_state.nba_analisis_heur[key] = resultado_heur
                        
                        # 2. Premium (siempre disponible)
                        resumen = analizador_heur.obtener_resumen()
                        resultado_premium = st.session_state.analizador_premium.analizar(p, resultado_heur)
                        st.session_state.nba_analisis_premium[key] = resultado_premium
                        
                        # 3. Gemini (si disponible)
                        if st.session_state.analizador_gemini:
                            resultado_gemini = st.session_state.analizador_gemini.analizar(p, resumen)
                            st.session_state.nba_analisis_gemini[key] = resultado_gemini
                        
                        st.rerun()
        else:
            st.info("👈 Carga NBA en el sidebar")

    with tab2:
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                st.session_state.visual_ufc.render(c, idx, st.session_state.tracker)
        else:
            st.info("👈 Carga UFC en el sidebar")

    with tab3:
        if st.session_state.futbol_partidos:
            for liga, partidos in st.session_state.futbol_partidos.items():
                if partidos:
                    with st.expander(f"**{liga}** ({len(partidos)} partidos)"):
                        for idx, p in enumerate(partidos):
                            st.session_state.visual_futbol.render(p, idx, liga, st.session_state.tracker)
                else:
                    st.write(f"⚪ {liga}: No hay partidos")
        else:
            st.info("👈 Carga ligas en el sidebar")

if __name__ == "__main__":
    main()
