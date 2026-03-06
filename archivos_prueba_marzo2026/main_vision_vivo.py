#!/usr/bin/env python3
"""
BETTING_AI - Con datos en vivo de Odds-API
"""
import streamlit as st
from datetime import datetime
from modules.team_database import TeamDatabase
from modules.hybrid_data_provider_v2 import HybridDataProviderV2
from modules.parlay_reasoning_engine import ParlayReasoningEngine

st.set_page_config(page_title="BETTING_AI - En Vivo", layout="wide")

st.title("🎯 BETTING_AI - Datos en Vivo 2026")
st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Inicializar proveedor y base
provider = HybridDataProviderV2()
db = TeamDatabase()

st.sidebar.success(f"✅ Base local: {db.data.get('total_teams', 0)} equipos")

# Verificar conexión Odds-API
partidos_vivo = provider.get_partidos_hoy()
if partidos_vivo:
    st.sidebar.success(f"✅ Odds-API: {len(partidos_vivo)} partidos disponibles")
else:
    st.sidebar.info("ℹ️ Odds-API: Sin partidos en vivo ahora")

# Tus capturas de HOY
capturas = {
    "🇳🇱 Eredivisie": [
        ("Heracles Almelo", "Utrecht", "+215", "+245", "+120"),
        ("Groningen", "Ajax Amsterdam", "+166", "+270", "+142"),
        ("PSV Eindhoven", "AZ Alkmaar", "-334", "+500", "+710"),
        ("Excelsior", "Heerenveen", "+182", "+265", "+130"),
        ("Sparta Rotterdam", "Zwolle", "-150", "+310", "+355"),
    ],
    "🇪🇸 LaLiga": [("Celta de Vigo", "Real Madrid", "+220", "+230", "+126")],
    "🇫🇷 Ligue 1": [("Paris Saint Germain", "AS Monaco", "-286", "+450", "+620")],
    "🇮🇹 Serie A": [("Napoli", "Torino", "-179", "+290", "+520")],
    "🇩🇪 Bundesliga": [("Bayern Munich", "Borussia Mönchengladbach", "-455", "+625", "+880")],
}

picks_parlay = []

for liga, partidos in capturas.items():
    st.header(liga)
    
    for local, visitante, cl, ce, cv in partidos:
        with st.expander(f"⚽ {local} vs {visitante}"):
            local_id = db.get_team_id(local)
            visitante_id = db.get_team_id(visitante)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if local_id:
                    st.success(f"✅ {local}")
                else:
                    st.error(f"❌ {local}")
                st.metric("Cuota Local", cl)
            
            with col2:
                st.metric("Empate", ce)
            
            with col3:
                if visitante_id:
                    st.success(f"✅ {visitante}")
                else:
                    st.error(f"❌ {visitante}")
                st.metric("Visitante", cv)
            
            # Intentar obtener odds en vivo
            if st.button(f"🔄 Buscar odds en vivo", key=f"live_{local}_{visitante}"):
                with st.spinner("Consultando Odds-API..."):
                    odds_vivos = provider.get_live_odds(local, visitante)
                    if odds_vivos:
                        st.success("✅ Odds en vivo encontrados!")
                        st.json(odds_vivos)
                    else:
                        st.info("ℹ️ Usando odds de captura")
            
            # Selector de picks
            pick = st.selectbox(
                "Pick", 
                ["Seleccionar", f"Gana {local}", "Empate", f"Gana {visitante}", "Over 1.5", "Over 2.5", "BTTS Sí"],
                key=f"pick_{local}_{visitante}"
            )
            
            if pick != "Seleccionar":
                picks_parlay.append({
                    'liga': liga,
                    'partido': f"{local} vs {visitante}",
                    'pick': pick,
                    'cuota': cl if "Gana" in pick and local in pick else ce if pick == "Empate" else cv
                })

# Parlay
st.header("🎯 Parlay")
if picks_parlay:
    for pick in picks_parlay:
        st.write(f"• {pick['partido']}: {pick['pick']}")
    
    if st.button("✅ Calcular Parlay"):
        prob_total = 0.5 ** len(picks_parlay)
        st.metric("Probabilidad estimada", f"{prob_total:.2%}")
else:
    st.info("Selecciona picks para armar tu parlay")
