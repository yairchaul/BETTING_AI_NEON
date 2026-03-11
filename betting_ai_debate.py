"""
BETTING_AI - SISTEMA COMPLETO CON DEBATE MULTI-AGENTE
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv

from api_client import OddsAPIClient
from stats_engine_renyi import RényiPredictor, NBAAnalyzer
from multi_agent import MultiAgentDebate

load_dotenv()

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
st.set_page_config(page_title="BETTING_AI - MULTI-AGENTE", layout="wide")

st.title("🤖 BETTING_AI - SISTEMA CON DEBATE MULTI-AGENTE")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')}")

# Mostrar estado de las APIs
col1, col2 = st.columns(2)
with col1:
    if os.getenv("ANTHROPIC_API_KEY"):
        st.success("✅ Claude API configurada")
    else:
        st.warning("⚠️ Claude API no configurada")
with col2:
    if os.getenv("OPENAI_API_KEY"):
        st.success("✅ GPT API configurada")
    else:
        st.warning("⚠️ GPT API no configurada")

# ============================================
# INICIALIZAR COMPONENTES
# ============================================
if 'odds_api' not in st.session_state:
    st.session_state.odds_api = OddsAPIClient()
    st.session_state.predictor = RényiPredictor()
    st.session_state.nba_analyzer = NBAAnalyzer()
    st.session_state.debate = MultiAgentDebate()
    st.session_state.partidos_futbol = []
    st.session_state.partidos_nba = []
    st.session_state.todos_picks = []
    st.session_state.debate_resultados = []

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.header("🎯 CONTROLES")
    
    if st.button("🔄 1. ACTUALIZAR PARTIDOS", use_container_width=True):
        with st.spinner("Extrayendo partidos..."):
            st.session_state.partidos_futbol = st.session_state.odds_api.get_partidos_futbol()
            st.session_state.partidos_nba = st.session_state.odds_api.get_partidos_nba()
            
            todos_picks = []
            
            # Procesar fútbol
            for p in st.session_state.partidos_futbol:
                try:
                    probs = st.session_state.predictor.predecir_partido_futbol(p)
                    
                    # Generar picks para diferentes mercados
                    mercados = [
                        ('Over 1.5', probs.get('over_1_5', 0.65)),
                        ('Over 2.5', probs.get('over_2_5', 0.45)),
                        ('BTTS Sí', probs.get('btts_si', 0.55)),
                        (f"Gana {p['local']}", probs.get('local', {}).get('probabilidad', 0.4)),
                        (f"Gana {p['visitante']}", probs.get('visitante', {}).get('probabilidad', 0.3))
                    ]
                    
                    for desc, prob in mercados:
                        if prob > 0.3:  # Solo picks con probabilidad mínima
                            cuota = round(1/prob * 0.95, 2)
                            value = (prob * cuota) - 1
                            
                            pick = {
                                'deporte': '⚽',
                                'liga': p['liga'],
                                'partido': f"{p['local']} vs {p['visitante']}",
                                'local': p['local'],
                                'visitante': p['visitante'],
                                'desc': f"{desc}",
                                'prob': prob,
                                'cuota': cuota,
                                'value': value,
                                'gf_local': probs.get('local', {}).get('gf', 0),
                                'gf_visit': probs.get('visitante', {}).get('gf', 0)
                            }
                            todos_picks.append(pick)
                except Exception as e:
                    pass
            
            st.session_state.todos_picks = todos_picks
            st.success(f"✅ {len(todos_picks)} picks generados")
    
    if st.button("🤖 2. DEBATIR PICKS", use_container_width=True):
        with st.spinner(f"🤔 {len(st.session_state.debate.agentes)} agentes debatiendo..."):
            resultados = st.session_state.debate.obtener_top_consenso(
                st.session_state.todos_picks, top_n=15
            )
            st.session_state.debate_resultados = resultados
            st.success(f"✅ Debate completado - {len(resultados)} picks analizados")
    
    if st.button("🧹 LIMPIAR RESULTADOS", use_container_width=True):
        st.session_state.debate_resultados = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 🤖 AGENTES ACTIVOS
    """)
    for a in st.session_state.debate.agentes:
        st.markdown(f"- {a.nombre}")

# ============================================
# MAIN CONTENT
# ============================================
if st.session_state.debate_resultados:
    st.header("🏆 RESULTADOS DEL DEBATE MULTI-AGENTE")
    
    # Separar por decisión
    apostar = [r for r in st.session_state.debate_resultados if r['decision'] == 'APOSTAR']
    analizar = [r for r in st.session_state.debate_resultados if r['decision'] == 'ANALIZAR_MAS']
    evitar = [r for r in st.session_state.debate_resultados if r['decision'] == 'EVITAR']
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total analizados", len(st.session_state.debate_resultados))
    with col2:
        st.metric("✅ APOSTAR", len(apostar), delta=f"{len(apostar)/len(st.session_state.debate_resultados)*100:.0f}%")
    with col3:
        st.metric("🤔 ANALIZAR", len(analizar))
    with col4:
        st.metric("❌ EVITAR", len(evitar))
    
    # Pestañas por decisión
    tab1, tab2, tab3 = st.tabs(["✅ RECOMENDADOS", "🤔 BAJO ANÁLISIS", "❌ DESCARTADOS"])
    
    with tab1:
        if apostar:
            for res in apostar:
                pick = res['pick']
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        st.markdown(f"**{pick['partido']}**")
                        st.caption(pick['liga'])
                    with col2:
                        st.markdown(f"🎯 {pick['desc']}")
                        st.caption(f"GF: {pick['gf_local']:.1f}-{pick['gf_visit']:.1f}")
                    with col3:
                        st.metric("Prob", f"{pick['prob']*100:.0f}%")
                        st.caption(f"Cuota: {pick['cuota']:.2f}")
                    with col4:
                        st.metric("Value", f"{pick['value']*100:.1f}%")
                        st.caption(f"Confianza: {res['confianza']:.0f}%")
                    
                    with st.expander("🗳️ Ver debate completo"):
                        st.markdown(f"**Decisión final:** {res['decision']} (confianza {res['confianza']:.0f}%)")
                        st.markdown(f"**Votos:** {res['votos_favor']} a favor, {res['votos_contra']} en contra")
                        st.markdown(f"**Justificación:** {res['justificacion']}")
                        
                        if 'opiniones' in res:
                            st.markdown("**Opiniones individuales:**")
                            for o in res['opiniones']:
                                emoji = "👍" if o['opinion'] == 'FAVORABLE' else "👎" if o['opinion'] == 'DESFAVORABLE' else "🤷"
                                st.markdown(f"- {emoji} **{o['agente']}**: {o['justificacion']} ({o['confianza']}%)")
                    
                    st.markdown("---")
        else:
            st.info("No hay picks recomendados")
    
    with tab2:
        if analizar:
            for res in analizar:
                pick = res['pick']
                st.markdown(f"**{pick['partido']}** - {pick['desc']} (Value: {pick['value']*100:.1f}%)")
        else:
            st.info("No hay picks en análisis")
    
    with tab3:
        if evitar:
            for res in evitar:
                pick = res['pick']
                st.markdown(f"**{pick['partido']}** - {pick['desc']} (Value: {pick['value']*100:.1f}%)")
        else:
            st.info("No hay picks descartados")

elif st.session_state.todos_picks:
    st.header("📊 PICKS GENERADOS (sin debate aún)")
    st.info("Haz click en 'DEBATIR PICKS' para que los agentes analicen estas opciones")
    
    # Mostrar algunos picks de ejemplo
    for pick in st.session_state.todos_picks[:10]:
        st.markdown(f"- {pick['partido']}: {pick['desc']} ({pick['prob']*100:.0f}%)")
else:
    st.info("👈 Haz click en ACTUALIZAR PARTIDOS para comenzar")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption(f"🤖 Agentes activos: {len(st.session_state.debate.agentes)} | ⚡ Modelo Rényi Entropy")
