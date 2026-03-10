import streamlit as st
from .models import SoccerModel
from .rules import SoccerRules

class SoccerProcessor:
    # Procesador específico para fútbol
    
    def __init__(self):
        self.model = SoccerModel()
        self.rules = SoccerRules()
    
    def process_match(self, home, away, odds, liga='Liga'):
        home_stats = self.model.get_team_power(home)
        away_stats = self.model.get_team_power(away)
        
        prediccion = self.model.predict_match(home, away, liga, home_stats, away_stats)
        picks = self.rules.aplicar_reglas(prediccion['markets'], prediccion['probs'], home, away)
        
        return {
            'prediccion': prediccion,
            'picks': picks
        }
    
    def render_match(self, idx, home, away, odds, liga='Liga'):
        with st.expander(f"**⚽ {home} vs {away}**", expanded=(idx == 0)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"### 🏠 **{home}**")
                st.metric(
                    label="Cuota",
                    value=f"{odds[0]}",
                    delta=f"{self._american_to_decimal(odds[0]):.2f}"
                )
            with col2:
                st.markdown(f"### ⚖️ **Empate**")
                st.metric(
                    label="Cuota",
                    value=f"{odds[1]}",
                    delta=f"{self._american_to_decimal(odds[1]):.2f}"
                )
            with col3:
                st.markdown(f"### 🚀 **{away}**")
                st.metric(
                    label="Cuota",
                    value=f"{odds[2]}",
                    delta=f"{self._american_to_decimal(odds[2]):.2f}"
                )
            
            result = self.process_match(home, away, odds, liga)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric('Over 1.5', f"{result['prediccion']['markets']['over_1_5']:.1%}")
            with col_m2:
                st.metric('Over 2.5', f"{result['prediccion']['markets']['over_2_5']:.1%}")
            with col_m3:
                st.metric('Over 3.5', f"{result['prediccion']['markets']['over_3_5']:.1%}")
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric('BTTS Sí', f"{result['prediccion']['markets']['btts']:.1%}")
            with col_p2:
                st.metric('Gana Local', f"{result['prediccion']['probs']['home']:.1%}")
            with col_p3:
                st.metric('Gana Visitante', f"{result['prediccion']['probs']['away']:.1%}")
            
            st.markdown('**🎯 Picks según reglas:**')
            return result['picks']
    
    def _american_to_decimal(self, odds):
        if not odds or odds == 'N/A':
            return 2.0
        try:
            odds = str(odds).replace('+', '')
            odds = int(odds)
            if odds > 0:
                return round(1 + (odds / 100), 2)
            else:
                return round(1 + (100 / abs(odds)), 2)
        except:
            return 2.0
