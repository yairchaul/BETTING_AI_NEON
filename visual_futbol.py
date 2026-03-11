"""
Visual de fútbol - SOLO CAMBIAMOS COLORES, MISMA ESTRUCTURA
"""
import streamlit as st
from rule_engine import RuleEngine
from stats_engine_renyi import RényiPredictor

class VisualFutbol:
    def __init__(self):
        self.predictor = RényiPredictor()
        self.rule_engine = RuleEngine()
    
    def render(self, partido, idx, tracker=None):
        """Renderiza un partido de fútbol - SOLO COLORES AJUSTADOS"""
        
        probs = self.predictor.predecir_partido_futbol(partido)
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            # Cabecera (IGUAL)
            st.markdown(f"### 📍 {partido['local']} vs {partido['visitante']}")
            st.caption(f"🏆 {partido['liga']}")
            
            # TRES COLUMNAS - SOLO CAMBIAMOS COLORES DE FONDO
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: #1A1A1A; border-left: 4px solid #FF6B35; border-radius: 5px;">
                    <h4 style="color: #FF6B35; margin: 0;">🏠 LOCAL</h4>
                    <h3 style="color: #FFFFFF; margin: 10px 0;">{partido['local']}</h3>
                    <h2 style="color: #FF6B35; margin: 5px 0;">{probs['odds_local_americano']}</h2>
                    <p style="color: #888888; margin: 0;">({partido['odds_local']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: #1A1A1A; border-left: 4px solid #666666; border-radius: 5px;">
                    <h4 style="color: #AAAAAA; margin: 0;">⚖️ EMPATE</h4>
                    <h3 style="color: #FFFFFF; margin: 10px 0;">Empate</h3>
                    <h2 style="color: #AAAAAA; margin: 5px 0;">{probs['odds_empate_americano']}</h2>
                    <p style="color: #888888; margin: 0;">({partido['odds_empate']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: #1A1A1A; border-left: 4px solid #0066CC; border-radius: 5px;">
                    <h4 style="color: #0066CC; margin: 0;">🚀 VISITANTE</h4>
                    <h3 style="color: #FFFFFF; margin: 10px 0;">{partido['visitante']}</h3>
                    <h2 style="color: #0066CC; margin: 5px 0;">{probs['odds_visit_americano']}</h2>
                    <p style="color: #888888; margin: 0;">({partido['odds_visitante']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            # RESTO IGUAL - SIN CAMBIOS
            st.markdown(f"**📊 Goles Esperados:** {partido['local']}: {probs['gf_local']:.2f} GF | {partido['visitante']}: {probs['gf_visit']:.2f} GF")
            
            st.markdown("**📈 Mercados Adicionales:**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Over 1.5", f"{probs['over_1_5']*100:.1f}%")
                st.metric("Over 2.5", f"{probs['over_2_5']*100:.1f}%")
                st.metric("Over 3.5", f"{probs['over_3_5']*100:.1f}%")
            with col_m2:
                st.metric("BTTS Sí", f"{probs['btts_si']*100:.1f}%")
                st.metric("BTTS No", f"{probs['btts_no']*100:.1f}%")
                st.metric("Over 1.5 1T", f"{probs['over_1_5_1t']*100:.1f}%")
            with col_m3:
                st.metric(f"Gana {partido['local']}", f"{probs['prob_local']*100:.1f}%")
                st.metric("Empate", f"{probs['prob_empate']*100:.1f}%")
                st.metric(f"Gana {partido['visitante']}", f"{probs['prob_visit']*100:.1f}%")
            
            # REGLAS (IGUAL)
            recomendacion = self.rule_engine.aplicar_reglas(probs, partido)
            
            st.markdown("---")
            st.markdown("### 🎯 RECOMENDACIÓN SEGÚN 7 REGLAS")
            
            if recomendacion['value'] > 0.1:
                color = "#00CC00"
            elif recomendacion['value'] > 0:
                color = "#DDDD00"
            else:
                color = "#FF5500"
            
            st.markdown(f"""
            <div style="border-left:5px solid {color}; padding:15px; background-color:#1A1A1A; border-radius:5px;">
                <h4 style="color:#FFFFFF;">REGLA {recomendacion['regla']}: {recomendacion['descripcion']}</h4>
                <p style="color:#CCCCCC;"><b>Probabilidad:</b> {recomendacion['probabilidad']*100:.1f}%</p>
                <p style="color:#CCCCCC;"><b>Cuota:</b> {recomendacion['cuota_americana']} ({recomendacion['cuota_decimal']:.2f})</p>
                <p style="color:{color};"><b>VALUE: {recomendacion['value']*100:.1f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
