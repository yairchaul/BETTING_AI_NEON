#!/usr/bin/env python3
"""
BETTING_AI - Análisis de Capturas Reales de Caliente.mx
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine

st.set_page_config(page_title="BETTING_AI - Capturas Reales", layout="wide")

# Título
st.title("🎯 BETTING_AI - Análisis de Capturas Caliente.mx")
st.caption(f"📅 Partidos del {datetime.now().strftime('%d/%m/%Y')}")

# Cargar base de datos
db = TeamDatabase()
st.sidebar.success(f"✅ Base de datos: {db.data.get('total_teams', 0)} equipos")

# Tus capturas de HOY
capturas = {
    "🇳🇱 Eredivisie (Holanda)": [
        {"local": "Heracles Almelo", "visitante": "Utrecht", "cuota_local": "+215", "cuota_empate": "+245", "cuota_visitante": "+120"},
        {"local": "Groningen", "visitante": "Ajax Amsterdam", "cuota_local": "+166", "cuota_empate": "+270", "cuota_visitante": "+142"},
        {"local": "PSV Eindhoven", "visitante": "AZ Alkmaar", "cuota_local": "-334", "cuota_empate": "+500", "cuota_visitante": "+710"},
        {"local": "Excelsior", "visitante": "Heerenveen", "cuota_local": "+182", "cuota_empate": "+265", "cuota_visitante": "+130"},
        {"local": "Sparta Rotterdam", "visitante": "Zwolle", "cuota_local": "-150", "cuota_empate": "+310", "cuota_visitante": "+355"},
    ],
    "🇪🇸 LaLiga": [
        {"local": "Celta de Vigo", "visitante": "Real Madrid", "cuota_local": "+220", "cuota_empate": "+230", "cuota_visitante": "+126"},
    ],
    "🇫🇷 Ligue 1": [
        {"local": "Paris Saint Germain", "visitante": "AS Monaco", "cuota_local": "-286", "cuota_empate": "+450", "cuota_visitante": "+620"},
    ],
    "🇮🇹 Serie A": [
        {"local": "Napoli", "visitante": "Torino", "cuota_local": "-179", "cuota_empate": "+290", "cuota_visitante": "+520"},
    ],
    "🇩🇪 Bundesliga": [
        {"local": "Bayern Munich", "visitante": "Borussia Mönchengladbach", "cuota_local": "-455", "cuota_empate": "+625", "cuota_visitante": "+880"},
    ],
}

# Selector de ligas
ligas = st.multiselect("Seleccionar ligas", list(capturas.keys()), default=list(capturas.keys()))

picks_parlay = []

# Mostrar cada liga
for liga in ligas:
    st.header(liga)
    
    # Crear columnas para los partidos
    cols = st.columns(2)
    
    for i, partido in enumerate(capturas[liga]):
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(f"⚽ {partido['local']} vs {partido['visitante']}")
                
                # Verificar IDs
                local_id = db.get_team_id(partido['local'])
                visitante_id = db.get_team_id(partido['visitante'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if local_id:
                        st.success(f"✅ {partido['local']}")
                    else:
                        st.error(f"❌ {partido['local']}")
                    st.metric("Local", partido['cuota_local'])
                
                with col2:
                    st.metric("Empate", partido['cuota_empate'])
                
                with col3:
                    if visitante_id:
                        st.success(f"✅ {partido['visitante']}")
                    else:
                        st.error(f"❌ {partido['visitante']}")
                    st.metric("Visitante", partido['cuota_visitante'])
                
                # Selector de picks
                opciones = ["Seleccionar pick", f"Gana {partido['local']}", "Empate", f"Gana {partido['visitante']}", "Over 1.5", "Over 2.5", "BTTS Sí"]
                pick = st.selectbox("Pick", opciones, key=f"pick_{liga}_{i}")
                
                if pick != "Seleccionar pick":
                    picks_parlay.append({
                        'liga': liga,
                        'partido': f"{partido['local']} vs {partido['visitante']}",
                        'pick': pick,
                        'cuota': "2.0"  # Placeholder
                    })

# Sección de Parlay
st.header("🎯 Parlay construido")
if picks_parlay:
    df = pd.DataFrame(picks_parlay)
    st.dataframe(df)
    
    # Calcular probabilidad (simulada)
    prob_total = 0.5 ** len(picks_parlay)
    st.metric("Probabilidad estimada", f"{prob_total:.2%}")
    
    if st.button("✅ Confirmar parlay"):
        st.success("Parlay registrado exitosamente!")
else:
    st.info("Selecciona picks de los partidos para construir tu parlay")

# Botón para actualizar
if st.sidebar.button("🔄 Actualizar capturas"):
    st.rerun()
