#!/usr/bin/env python3
"""
Versión funcional de main_vision.py - Corregida
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
        st.header("Configuración")
        umbral = st.slider("Umbral de probabilidad", 0, 100, 50)
        st.info(f"Usando umbral: {umbral}%")
    
    # Cargar base de datos
    db = TeamDatabase()
    st.success(f"✅ Base de datos cargada: {db.data.get('total_teams', 0)} equipos")
    
    # Área principal
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Partidos del día")
        partidos = [
            ("Tottenham", "Arsenal"),
            ("Real Madrid", "Barcelona"),
            ("Liverpool", "Manchester United"),
            ("Ajax", "PSV Eindhoven"),
            ("Benfica", "Porto"),
            ("Celtic", "Rangers")
        ]
        
        for local, visitante in partidos:
            with st.expander(f"{local} vs {visitante}"):
                local_id = db.get_team_id(local)
                visitante_id = db.get_team_id(visitante)
                
                if local_id and visitante_id:
                    st.success(f"✅ IDs: {local}={local_id}, {visitante}={visitante_id}")
                    st.info(f"📈 Análisis disponible (umbral {umbral}%)")
                else:
                    st.error(f"❌ Equipos no encontrados en base de datos")
    
    with col2:
        st.subheader("🎯 Parlay recomendado")
        
        # Ejemplo de picks para parlay
        engine = ParlayReasoningEngine(umbral_principal=umbral/100)
        
        picks_ejemplo = [
            {'partido': 'Tottenham vs Arsenal', 'mercado': 'Over 1.5', 'prob': 0.53, 'odds': 1.85},
            {'partido': 'Liverpool vs Man Utd', 'mercado': 'BTTS Sí', 'prob': 0.52, 'odds': 1.90},
            {'partido': 'Ajax vs PSV', 'mercado': 'Over 2.5', 'prob': 0.54, 'odds': 1.88}
        ]
        
        prob_total = 1.0
        for pick in picks_ejemplo:
            prob_total *= pick['prob']
            st.write(f"• {pick['partido']}: {pick['mercado']} ({pick['prob']:.0%})")
        
        st.metric("Probabilidad total", f"{prob_total:.2%}")
        st.metric("Calidad", "ALTA" if prob_total >= 0.15 else "MEDIA" if prob_total >= 0.10 else "BAJA")

if __name__ == "__main__":
    main()
