# modules/ml_predictor.py
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import os
from datetime import datetime

class MLPredictor:
    """
    Predictor basado en Machine Learning (XGBoost)
    Aprende de datos históricos para predecir resultados
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = 'models/xgboost_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        
        # Cargar modelo si existe
        self._load_model()
    
    def _load_model(self):
        """Carga un modelo previamente entrenado"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                st.success("✅ Modelo ML cargado exitosamente")
        except:
            pass
    
    def _save_model(self):
        """Guarda el modelo entrenado"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
        except Exception as e:
            st.warning(f"No se pudo guardar el modelo: {e}")
    
    def prepare_features(self, home_team, away_team, home_stats, away_stats, league_data):
        """
        Prepara las características para el modelo
        """
        features = []
        
        # Características del equipo local
        features.append(home_stats.get('home_goals_for', 1.5))
        features.append(home_stats.get('home_goals_against', 1.2))
        features.append(home_stats.get('home_btts_pct', 50) / 100)
        features.append(home_stats.get('home_wins_pct', 50) / 100)
        
        # Características del equipo visitante
        features.append(away_stats.get('away_goals_for', 1.2))
        features.append(away_stats.get('away_goals_against', 1.4))
        features.append(away_stats.get('away_btts_pct', 48) / 100)
        features.append(away_stats.get('away_wins_pct', 40) / 100)
        
        # Características de la liga
        features.append(league_data.get('goles_promedio', 2.5))
        features.append(league_data.get('local_ventaja', 55) / 100)
        features.append(league_data.get('btts_pct', 50) / 100)
        
        return np.array(features).reshape(1, -1)
    
    def train(self, historical_data):
        """
        Entrena el modelo con datos históricos
        historical_data: lista de diccionarios con features y resultado
        """
        if len(historical_data) < 100:
            st.warning("Se necesitan al menos 100 partidos para entrenar")
            return False
        
        # Preparar datos
        X = []
        y = []
        
        for match in historical_data:
            X.append(match['features'])
            y.append(match['resultado'])  # 0: Local, 1: Empate, 2: Visitante
        
        X = np.array(X)
        y = np.array(y)
        
        # Escalar características
        X_scaled = self.scaler.fit_transform(X)
        
        # Dividir en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Entrenar modelo XGBoost
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='multi:softprob',
            num_class=3,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluar
        accuracy = self.model.score(X_test, y_test)
        st.success(f"✅ Modelo entrenado con precisión: {accuracy:.2%}")
        
        self.is_trained = True
        self._save_model()
        
        return True
    
    def predict(self, features):
        """
        Predice el resultado de un partido
        Devuelve probabilidades para [Local, Empate, Visitante]
        """
        if not self.is_trained:
            return None
        
        try:
            features_scaled = self.scaler.transform(features)
            probabilities = self.model.predict_proba(features_scaled)[0]
            return {
                'local': probabilities[0],
                'empate': probabilities[1],
                'visitante': probabilities[2]
            }
        except Exception as e:
            st.error(f"Error en predicción: {e}")
            return None
    
    def get_feature_importance(self):
        """Obtiene importancia de las características"""
        if not self.is_trained:
            return None
        
        feature_names = [
            'Goles local', 'Goles recibidos local', 'BTTS local', 'Victorias local',
            'Goles visitante', 'Goles recibidos visitante', 'BTTS visitante', 'Victorias visitante',
            'Goles liga', 'Ventaja local', 'BTTS liga'
        ]
        
        importance = self.model.feature_importances_
        
        return sorted(zip(feature_names, importance), key=lambda x: x[1], reverse=True)