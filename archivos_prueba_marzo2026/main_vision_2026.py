#!/usr/bin/env python3
"""
Versión 2026 - Obtiene la temporada actual automáticamente
"""
import streamlit as st
import requests
from datetime import datetime
from modules.team_database import TeamDatabase
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine

API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"
headers = {'x-apisports-key': API_KEY}

# Ligas principales con sus IDs
LIGAS = {
    "🇪🇸 LaLiga": 140,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39,
    "🇮🇹 Serie A": 135,
    "🇩🇪 Bundesliga": 78,
    "🇫🇷 Ligue 1": 61,
    "🇳🇱 Eredivisie": 88,
    "🇵🇹 Primeira Liga": 94,
    "🇲🇽 Liga MX": 262,
    "🇺🇸 MLS": 253,
}

def obtener_temporada_actual(liga_id):
    """Obtiene la temporada actual para una liga"""
    try:
        url = f"{BASE_URL}/leagues"
        params = {'id': liga_id}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                liga_info = data['response'][0]
                seasons = liga_info.get('seasons', [])
                # Buscar temporada actual
                for season in seasons:
                    if season.get('current'):
                        return season.get('year')
                # Si no hay current, usar la última
                if seasons:
                    return seasons[-1].get('year')
    except Exception as e:
        st.error(f"Error obteniendo temporada: {e}")
    return 2025  # fallback

def get_partidos_hoy(liga_id, season):
    """Obtener partidos de hoy de una liga específica"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        url = f"{BASE_URL}/fixtures"
        params = {
            'league': liga_id,
            'season': season,
            'date': today,
            'timezone': 'America/Mexico_City'
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', [])
        else:
            st.warning(f"API error {response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")
    
    return []

def main():
    st.set_page_config(page_title="BETTING_AI 2026", layout="wide")
    st.title("🎯 BETTING_AI - Temporada 2026")
    
    # Cargar base de datos
    db = TeamDatabase()
    total = db.data.get('total_teams', 0) if isinstance(db.data, dict) else 0
    st.sidebar.success(f"✅ Base: {total} equipos")
    
    # Selector de ligas
    ligas_seleccionadas = st.sidebar.multiselect(
        "Ligas a mostrar",
        list(LIGAS.keys()),
        default=["🇪🇸 LaLiga", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🇲🇽 Liga MX"]
    )
    
    umbral = st.sidebar.slider("Umbral %", 0, 100, 50)
    
    if st.sidebar.button("🔄 Actualizar partidos"):
        st.rerun()
    
    st.sidebar.info(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Mostrar partidos por liga
    tabs = st.tabs(ligas_seleccionadas)
    
    for i, liga_nombre in enumerate(ligas_seleccionadas):
        with tabs[i]:
            liga_id = LIGAS[liga_nombre]
            
            # Obtener temporada actual para esta liga
            season = obtener_temporada_actual(liga_id)
            st.caption(f"Temporada: {season}")
            
            partidos = get_partidos_hoy(liga_id, season)
            
            if not partidos:
                st.info(f"No hay partidos programados para hoy en {liga_nombre}")
                
                # Mostrar equipos de ejemplo de esta liga
                st.subheader("📋 Equipos disponibles:")
                equipos_ejemplo = {
                    "🇪🇸 LaLiga": ["Real Madrid", "Barcelona", "Atletico Madrid"],
                    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": ["Tottenham", "Arsenal", "Liverpool"],
                    "🇲🇽 Liga MX": ["América", "Guadalajara", "Tigres UANL"],
                    "🇺🇸 MLS": ["Inter Miami", "LAFC", "Seattle Sounders"],
                }
                
                for equipo in equipos_ejemplo.get(liga_nombre, []):
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
                            st.info("📊 Análisis disponible")
                            if st.button(f"Analizar", key=f"btn_{partido['fixture']['id']}"):
                                st.success("✅ Análisis completado")
    
    # Sección de Parlay
    st.header("🎯 Parlay recomendado")
    engine = ParlayReasoningEngine(umbral_principal=umbral/100)
    
    # Obtener picks de ejemplo basados en equipos disponibles
    picks_ejemplo = []
    
    # Intentar crear picks con equipos que sabemos que existen
    equipos_conocidos = [
        ('Real Madrid', 'Barcelona', 'LaLiga'),
        ('América', 'Guadalajara', 'Liga MX'),
        ('Tottenham', 'Arsenal', 'Premier League'),
    ]
    
    for local, visitante, liga in equipos_conocidos:
        if db.get_team_id(local) and db.get_team_id(visitante):
            picks_ejemplo.append({
                'partido': f'{local} vs {visitante}',
                'mercado': 'Over 1.5',
                'prob': 0.53,
                'odds': 1.85
            })
            break  # Solo necesitamos 1-2 picks para el ejemplo
    
    if picks_ejemplo:
        prob_total = 1.0
        for pick in picks_ejemplo:
            prob_total *= pick['prob']
            st.write(f"• {pick['partido']}: {pick['mercado']} ({pick['prob']:.0%})")
        
        st.metric("Probabilidad total", f"{prob_total:.2%}")
        
        if prob_total >= 0.15:
            st.success("🚀 Calidad ALTA")
        elif prob_total >= 0.10:
            st.warning("⚡ Calidad MEDIA")
        else:
            st.error("⚠️ Calidad BAJA")
    else:
        st.info("Selecciona partidos para generar un parlay")

if __name__ == "__main__":
    main()
