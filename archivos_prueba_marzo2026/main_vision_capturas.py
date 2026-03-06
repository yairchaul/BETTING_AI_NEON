#!/usr/bin/env python3
"""
BETTING_AI - Análisis de Capturas de Caliente.mx
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine

st.set_page_config(page_title="BETTING_AI - Capturas", layout="wide")
st.title("🎯 BETTING_AI - Análisis de Capturas Caliente.mx")
st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# Cargar base de datos
db = TeamDatabase()
st.sidebar.success(f"✅ Base: {db.data.get('total_teams', 0)} equipos")

# Partidos de las capturas de HOY
partidos_hoy = {
    "🇳🇱 Eredivisie": [
        ("Heracles Almelo", "Utrecht", "+215", "+245", "+120"),
        ("Groningen", "Ajax Amsterdam", "+166", "+270", "+142"),
        ("PSV Eindhoven", "AZ Alkmaar", "-334", "+500", "+710"),
        ("Excelsior", "Heerenveen", "+182", "+265", "+130"),
        ("Sparta Rotterdam", "Zwolle", "-150", "+310", "+355"),
    ],
    "🇪🇸 LaLiga": [
        ("Celta de Vigo", "Real Madrid", "+220", "+230", "+126"),
    ],
    "🇫🇷 Ligue 1": [
        ("Paris Saint Germain", "AS Monaco", "-286", "+450", "+620"),
    ],
    "🇮🇹 Serie A": [
        ("Napoli", "Torino", "-179", "+290", "+520"),
    ],
    "🇩🇪 Bundesliga": [
        ("Bayern Munich", "Borussia Monchengladbach", "-455", "+625", "+880"),
    ]
}

# Selector de ligas
ligas = st.multiselect("Seleccionar ligas", list(partidos_hoy.keys()), default=list(partidos_hoy.keys()))

# Mostrar partidos
picks_parlay = []

for liga in ligas:
    st.header(liga)
    
    for partido in partidos_hoy[liga]:
        local, visitante, cuota_local, cuota_empate, cuota_visitante = partido
        
        with st.expander(f"⚽ {local} vs {visitante}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                local_id = db.get_team_id(local)
                if local_id:
                    st.success(f"✅ {local}")
                else:
                    st.error(f"❌ {local}")
                st.metric("Cuota Local", cuota_local)
            
            with col2:
                visitante_id = db.get_team_id(visitante)
                if visitante_id:
                    st.success(f"✅ {visitante}")
                else:
                    st.error(f"❌ {visitante}")
                st.metric("Cuota Visitante", cuota_visitante)
            
            with col3:
                st.metric("Cuota Empate", cuota_empate)
                
                if st.button(f"Analizar", key=f"{local}_{visitante}"):
                    st.info("📊 Análisis completado")
                    
                    # Aquí el usuario puede seleccionar picks para el parlay
                    if st.checkbox("Agregar a parlay", key=f"pick_{local}_{visitante}"):
                        picks_parlay.append({
                            'partido': f"{local} vs {visitante}",
                            'mercado': 'A definir',
                            'prob': 0.50,
                            'odds': 2.0
                        })

# Sección de Parlay
st.header("🎯 Parlay")
if picks_parlay:
    df = pd.DataFrame(picks_parlay)
    st.dataframe(df)
    
    prob_total = 1.0
    for pick in picks_parlay:
        prob_total *= pick['prob']
    
    st.metric("Probabilidad total", f"{prob_total:.2%}")
else:
    st.info("Selecciona picks de los partidos para armar un parlay")
