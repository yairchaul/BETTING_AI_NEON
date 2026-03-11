"""
MAIN VISION - Versión final con todos los análisis
"""
import streamlit as st
from datetime import datetime
import os

from api_client import OddsAPIClient
from visual_futbol import VisualFutbol
from visual_nba_jerarquico import VisualNBA
from visual_ufc_mejorado import VisualUFC

st.set_page_config(
    page_title="BETTING_AI - Análisis Profesional",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 BETTING_AI - Análisis Deportivo Profesional")
st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')} | Datos: Caliente.mx + ESPN")

# Inicializar
if 'api_client' not in st.session_state:
    st.session_state.api_client = OddsAPIClient()
    st.session_state.visual_futbol = VisualFutbol()
    st.session_state.visual_nba = VisualNBA()
    st.session_state.visual_ufc = VisualUFC()
    st.session_state.partidos_futbol = []
    st.session_state.partidos_nba = []
    st.session_state.combates_ufc = []

# Sidebar
with st.sidebar:
    st.header("🎯 CONTROLES")
    
    if st.button("🔄 ACTUALIZAR TODOS LOS DEPORTES", use_container_width=True):
        with st.spinner("📡 Extrayendo datos en tiempo real..."):
            st.session_state.partidos_futbol = st.session_state.api_client.get_partidos_futbol()
            st.session_state.partidos_nba = st.session_state.api_client.get_partidos_nba()
            st.session_state.combates_ufc = st.session_state.api_client.get_combates_ufc()
            st.success(f"✅ Fútbol: {len(st.session_state.partidos_futbol)} | NBA: {len(st.session_state.partidos_nba)} | UFC: {len(st.session_state.combates_ufc)}")
    
    st.markdown("---")
    st.markdown("""
    ### 📊 JERARQUÍA NBA
    1. **Spread** (Handicap)
    2. **Totals** (Over/Under)
    3. **Moneyline** (Ganador)
    
    ### 🥊 ANÁLISIS UFC
    - Ganador probable
    - Método (KO/Sumisión/Decisión)
    - Round más probable
    - % Finalización
    """)

# Pestañas
tab1, tab2, tab3 = st.tabs(["⚽ FÚTBOL (7 REGLAS)", "🏀 NBA (JERÁRQUICO)", "🥊 UFC (COMPLETO)"])

with tab1:
    if st.session_state.partidos_futbol:
        for i, partido in enumerate(st.session_state.partidos_futbol):
            st.session_state.visual_futbol.render(partido, i)
    else:
        st.info("👈 Actualiza para ver los partidos de hoy")

with tab2:
    if st.session_state.partidos_nba:
        for i, partido in enumerate(st.session_state.partidos_nba):
            st.session_state.visual_nba.render(partido, i)
    else:
        st.info("No hay partidos NBA programados para hoy")

with tab3:
    if st.session_state.combates_ufc:
        for i, combate in enumerate(st.session_state.combates_ufc):
            st.session_state.visual_ufc.render(combate, i)
    else:
        st.info("No hay eventos UFC programados")

# Footer
st.markdown("---")
st.caption("⚡ Fútbol: 7 reglas jerárquicas | NBA: Spread > Totals > Moneyline | UFC: Simulación Monte Carlo")
