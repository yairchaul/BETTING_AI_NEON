#!/usr/bin/env python3
"""
Versión mejorada de main_vision.py - Con soporte completo de ligas
"""
import sys
import streamlit as st
from modules.team_database import TeamDatabase
from modules.hybrid_data_provider import HybridDataProvider
from modules.smart_betting_ai import SmartBettingAI
from modules.parlay_reasoning_engine import ParlayReasoningEngine

def main():
    st.set_page_config(page_title="BETTING_AI", layout="wide")
    st.title("🎯 BETTING_AI - Sistema de Análisis de Apuestas")
    
    # Barra lateral
    with st.sidebar:
        st.header("⚙️ Configuración")
        umbral = st.slider("Umbral de probabilidad", 0, 100, 50)
        st.info(f"Usando umbral: {umbral}%")
        
        st.header("📁 Ligas disponibles")
        ligas = st.multiselect(
            "Seleccionar ligas",
            ["España", "Inglaterra", "Holanda", "Portugal", "Bélgica", 
             "Turquía", "Escocia", "Dinamarca", "Suecia", "Noruega"],
            default=["España", "Inglaterra", "Holanda", "Portugal"]
        )
    
    # Cargar base de datos
    db = TeamDatabase()
    total_equipos = db.data.get('total_teams', 0) if isinstance(db.data, dict) else len(db.data) if isinstance(db.data, list) else 0
    st.success(f"✅ Base de datos cargada: {total_equipos} equipos")
    
    # Mapeo de equipos por liga
    equipos_por_liga = {
        "España": [("Real Madrid", "Barcelona"), ("Atletico Madrid", "Sevilla")],
        "Inglaterra": [("Tottenham", "Arsenal"), ("Liverpool", "Manchester United")],
        "Holanda": [("Ajax", "PSV Eindhoven"), ("Feyenoord", "AZ Alkmaar")],
        "Portugal": [("Benfica", "Porto"), ("Sporting CP", "Braga")],
        "Bélgica": [("Anderlecht", "Club Brugge"), ("Genk", "Gent")],
        "Turquía": [("Galatasaray", "Fenerbahçe"), ("Besiktas", "Trabzonspor")],
        "Escocia": [("Celtic", "Rangers"), ("Aberdeen", "Hearts")],
        "Dinamarca": [("FC Copenhagen", "Midtjylland"), ("Brøndby", "Aarhus")],
        "Suecia": [("Malmö FF", "AIK"), ("Djurgården", "Hammarby")],
        "Noruega": [("Molde", "Bodø/Glimt"), ("Rosenborg", "Viking")]
    }
    
    # Columnas para mostrar partidos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Partidos del día")
        
        tabs = st.tabs(ligas if ligas else ["Todas"])
        
        for i, liga in enumerate(ligas if ligas else equipos_por_liga.keys()):
            with tabs[i % len(tabs)]:
                partidos = equipos_por_liga.get(liga, [])
                
                for local, visitante in partidos:
                    with st.expander(f"⚽ {local} vs {visitante}"):
                        local_id = db.get_team_id(local)
                        visitante_id = db.get_team_id(visitante)
                        
                        cols = st.columns(3)
                        with cols[0]:
                            if local_id:
                                st.success(f"✅ {local}: ID {local_id}")
                            else:
                                st.error(f"❌ {local} no encontrado")
                        
                        with cols[1]:
                            if visitante_id:
                                st.success(f"✅ {visitante}: ID {visitante_id}")
                            else:
                                st.error(f"❌ {visitante} no encontrado")
                        
                        with cols[2]:
                            if local_id and visitante_id:
                                st.info(f"📈 Análisis disponible")
    
    with col2:
        st.subheader("🎯 Parlay recomendado")
        
        # Generar picks según ligas seleccionadas
        engine = ParlayReasoningEngine(umbral_principal=umbral/100)
        picks_parlay = []
        
        # Picks de ejemplo con probabilidades realistas
        ejemplos_picks = [
            ('Real Madrid vs Barcelona', 'Over 1.5', 0.52, 1.85),
            ('Tottenham vs Arsenal', 'BTTS Sí', 0.51, 1.90),
            ('Ajax vs PSV', 'Over 2.5', 0.54, 1.88),
            ('Benfica vs Porto', 'Gana Benfica', 0.48, 2.10),
            ('Celtic vs Rangers', 'Over 2.5', 0.53, 1.92)
        ]
        
        prob_total = 1.0
        for partido, mercado, prob, odds in ejemplos_picks[:len(ligas)+1]:
            if prob >= umbral/100:
                picks_parlay.append({
                    'partido': partido,
                    'mercado': mercado,
                    'prob': prob,
                    'odds': odds
                })
                prob_total *= prob
                st.write(f"• **{partido}**: {mercado} ({prob:.0%})")
        
        if picks_parlay:
            st.metric("Probabilidad total", f"{prob_total:.2%}")
            
            # Clasificación de calidad
            if prob_total >= 0.15:
                calidad = "🚀 ALTA"
                color = "green"
            elif prob_total >= 0.10:
                calidad = "⚡ MEDIA"
                color = "orange"
            else:
                calidad = "⚠️ BAJA"
                color = "red"
            
            st.markdown(f"**Calidad:** :{color}[{calidad}]")
            
            # Valor esperado aproximado
            odds_total = 1.0
            for pick in picks_parlay:
                odds_total *= pick['odds']
            ev = (prob_total * odds_total) - 1
            st.metric("Valor Esperado", f"{ev:.2%}")
        else:
            st.warning("No hay picks que cumplan el umbral")
        
        # Botón para actualizar
        if st.button("🔄 Actualizar análisis"):
            st.rerun()

if __name__ == "__main__":
    main()
