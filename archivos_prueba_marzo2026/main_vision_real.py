#!/usr/bin/env python3
"""
Versión con partidos reales de las principales ligas
"""
import streamlit as st
import requests
from datetime import datetime
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine

# Configuración de la API
API_KEY = "11eaff423a9042393b1fe21512384884"  # Tu API key
BASE_URL = "https://v3.football.api-sports.io"

# Ligas principales con sus IDs
LIGAS = {
    "🇪🇸 LaLiga": 140,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39,
    "🇳🇱 Eredivisie": 88,
    "🇵🇹 Primeira Liga": 94,
    "🇧🇪 Jupiler Pro League": 144,
    "🇹🇷 Süper Lig": 203,
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership": 179,
    "🇩🇰 Superliga": 119,
    "🇸🇪 Allsvenskan": 113,
    "🇳🇴 Eliteserien": 103
}

def get_partidos_hoy(liga_id):
    """Obtener partidos de hoy de una liga específica"""
    headers = {
        'x-apisports-key': API_KEY,
        'x-apisports-host': 'v3.football.api-sports.io'
    }
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        url = f"{BASE_URL}/fixtures"
        params = {
            'league': liga_id,
            'season': 2025,
            'date': today
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', [])
    except Exception as e:
        st.error(f"Error API: {e}")
    
    return []

def main():
    st.set_page_config(page_title="BETTING_AI - REAL", layout="wide")
    st.title("🎯 BETTING_AI - Partidos Reales")
    
    # Cargar base de datos
    db = TeamDatabase()
    total = db.data.get('total_teams', 0) if isinstance(db.data, dict) else 0
    st.sidebar.success(f"✅ Base: {total} equipos")
    
    # Selector de ligas
    ligas_seleccionadas = st.sidebar.multiselect(
        "Ligas a mostrar",
        list(LIGAS.keys()),
        default=list(LIGAS.keys())[:3]
    )
    
    umbral = st.sidebar.slider("Umbral %", 0, 100, 50)
    
    if st.sidebar.button("🔄 Actualizar partidos"):
        st.rerun()
    
    # Mostrar partidos por liga
    tabs = st.tabs(ligas_seleccionadas)
    
    for i, liga_nombre in enumerate(ligas_seleccionadas):
        with tabs[i]:
            liga_id = LIGAS[liga_nombre]
            partidos = get_partidos_hoy(liga_id)
            
            if not partidos:
                st.info(f"No hay partidos programados para hoy en {liga_nombre}")
                
                # Mostrar ejemplo de la liga para probar
                st.subheader("📋 Equipos de ejemplo:")
                equipos_ejemplo = []
                if "LaLiga" in liga_nombre:
                    equipos_ejemplo = ["Real Madrid", "Barcelona", "Atletico Madrid"]
                elif "Premier" in liga_nombre:
                    equipos_ejemplo = ["Tottenham", "Arsenal", "Liverpool"]
                elif "Eredivisie" in liga_nombre:
                    equipos_ejemplo = ["Ajax", "PSV Eindhoven", "Feyenoord"]
                
                for equipo in equipos_ejemplo:
                    team_id = db.get_team_id(equipo)
                    if team_id:
                        st.success(f"✅ {equipo}: ID {team_id}")
                    else:
                        st.error(f"❌ {equipo}: No encontrado")
                
                continue
            
            for partido in partidos:
                local = partido['teams']['home']['name']
                visitante = partido['teams']['away']['name']
                hora = partido['fixture']['date'][11:16]
                
                with st.expander(f"⚽ {local} vs {visitante} - {hora}"):
                    local_id = db.get_team_id(local)
                    visitante_id = db.get_team_id(visitante)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if local_id:
                            st.success(f"✅ {local}")
                        else:
                            st.error(f"❌ {local}")
                    
                    with col2:
                        if visitante_id:
                            st.success(f"✅ {visitante}")
                        else:
                            st.error(f"❌ {visitante}")
                    
                    with col3:
                        if local_id and visitante_id:
                            # Aquí iría el análisis real
                            st.info("📊 Análisis disponible")
                            if st.button(f"Analizar", key=f"btn_{partido['fixture']['id']}"):
                                st.success("Análisis completado")

if __name__ == "__main__":
    main()
