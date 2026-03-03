# pages/2_Train_Model.py
import streamlit as st
import pandas as pd
from modules.data_collector import DataCollector
from modules.ml_predictor import MLPredictor
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate

st.set_page_config(page_title="Entrenar Modelo ML", layout="wide")

st.title("🧠 Entrenamiento del Modelo ML")
st.markdown("Recolecta datos históricos y entrena el modelo XGBoost para mejorar las predicciones.")

# Inicializar componentes
if 'data_collector' not in st.session_state:
    st.session_state.data_collector = DataCollector()
if 'ml_predictor' not in st.session_state:
    st.session_state.ml_predictor = MLPredictor()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ProAnalyzerUltimate()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Recolectar Datos")
    
    ligas_comunes = [
        "Premier League", "LaLiga", "Bundesliga", "Serie A", "Ligue 1",
        "Liga MX", "Argentina Liga Profesional", "Brazil Serie A"
    ]
    
    liga_seleccionada = st.selectbox("Selecciona una liga", ligas_comunes)
    season = st.selectbox("Temporada", ["2024", "2023", "2022", "2021"])
    limite = st.slider("Número de partidos", 100, 1000, 500)
    
    if st.button("🔍 Recolectar Datos"):
        with st.spinner("Recolectando datos históricos..."):
            league_id = st.session_state.data_collector.get_league_id(liga_seleccionada)
            if league_id:
                matches = st.session_state.data_collector.get_historical_matches(
                    league_id, season, limite
                )
                st.session_state.raw_matches = matches
                st.success(f"✅ {len(matches)} partidos recolectados")
            else:
                st.error("No se encontró la liga")

with col2:
    st.subheader("🤖 Entrenar Modelo")
    
    if 'raw_matches' in st.session_state and st.session_state.raw_matches:
        st.write(f"Partidos disponibles: {len(st.session_state.raw_matches)}")
        
        if st.button("🎯 Entrenar Modelo"):
            with st.spinner("Entrenando modelo XGBoost..."):
                # Preparar datos para entrenamiento
                historical_data = []
                
                for match in st.session_state.raw_matches[:limite]:
                    # Simular estadísticas (en producción deberían ser reales)
                    home_stats = {
                        'home_goals_for': match['home_goals'],
                        'home_goals_against': match['away_goals'],
                        'home_btts_pct': 50 if (match['home_goals'] > 0 and match['away_goals'] > 0) else 0,
                        'home_wins_pct': 100 if match['resultado'] == 0 else 0
                    }
                    away_stats = {
                        'away_goals_for': match['away_goals'],
                        'away_goals_against': match['home_goals'],
                        'away_btts_pct': 50 if (match['home_goals'] > 0 and match['away_goals'] > 0) else 0,
                        'away_wins_pct': 100 if match['resultado'] == 2 else 0
                    }
                    league_data = {'goles_promedio': 2.5, 'local_ventaja': 55, 'btts_pct': 50}
                    
                    features = st.session_state.ml_predictor.prepare_features(
                        home_stats, away_stats, league_data
                    ).flatten().tolist()
                    
                    historical_data.append({
                        'features': features,
                        'resultado': match['resultado']
                    })
                
                # Entrenar
                success = st.session_state.ml_predictor.train(historical_data)
                
                if success:
                    st.balloons()
                    st.success("✅ Modelo entrenado y guardado!")
                    
                    # Mostrar importancia de características
                    importance = st.session_state.ml_predictor.get_feature_importance()
                    if importance:
                        st.subheader("📊 Importancia de Características")
                        df_importance = pd.DataFrame(importance, columns=['Característica', 'Importancia'])
                        st.bar_chart(df_importance.set_index('Característica'))
    else:
        st.info("Primero recolecta datos históricos")

# Estado actual del modelo
st.divider()
st.subheader("📈 Estado del Modelo")

col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    if st.session_state.ml_predictor.is_trained:
        st.success("✅ Modelo entrenado")
    else:
        st.warning("⏳ Modelo no entrenado")

with col_status2:
    if 'raw_matches' in st.session_state:
        st.info(f"📊 {len(st.session_state.raw_matches)} partidos en memoria")

with col_status3:
    st.caption("Versión 1.0 - XGBoost Classifier")