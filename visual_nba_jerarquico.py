"""
Visual NBA - Con jerarquía Spread > Totals > Moneyline
"""
import streamlit as st
from nba_probability_engine import NBAProbabilityEngine

class VisualNBA:
    def __init__(self):
        self.engine = NBAProbabilityEngine()
    
    def render(self, partido, idx):
        """Renderiza partido NBA con recomendaciones jerárquicas"""
        
        with st.container():
            st.markdown(f"### 🏀 {partido['local']} vs {partido['visitante']}")
            
            odds = partido.get('odds', {})
            
            # Columnas con datos
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="padding: 10px; background-color: #1A1A1A; border-left: 4px solid #FF6B35; border-radius: 5px;">
                    <h4 style="color:#FF6B35;">🏠 LOCAL</h4>
                    <h3 style="color:#FFFFFF;">{partido['local']}</h3>
                    <p style="color:#FF6B35;">{odds.get('h2h', {}).get(partido['local'], 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding: 10px; background-color: #1A1A1A; border-left: 4px solid #0066CC; border-radius: 5px;">
                    <h4 style="color:#0066CC;">🚀 VISITANTE</h4>
                    <h3 style="color:#FFFFFF;">{partido['visitante']}</h3>
                    <p style="color:#0066CC;">{odds.get('h2h', {}).get(partido['visitante'], 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="padding: 10px; background-color: #1A1A1A; border-left: 4px solid #888888; border-radius: 5px;">
                    <h4 style="color:#888888;">📊 SPREADS</h4>
                """, unsafe_allow_html=True)
                if 'spreads' in odds:
                    sp_local = odds['spreads'][partido['local']]
                    sp_visit = odds['spreads'][partido['visitante']]
                    st.markdown(f"<p>{partido['local']} {sp_local['point']:+g} <span style='color:#888;'>{sp_local['price']:.2f}</span></p>", unsafe_allow_html=True)
                    st.markdown(f"<p>{partido['visitante']} {sp_visit['point']:+g} <span style='color:#888;'>{sp_visit['price']:.2f}</span></p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Totales
            if 'totals' in odds:
                st.markdown("**🔥 TOTALES**")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.metric("OVER", f"{odds['totals']['Over']['point']}", f"{odds['totals']['Over']['price']:.2f}")
                with col_t2:
                    st.metric("UNDER", f"{odds['totals']['Under']['point']}", f"{odds['totals']['Under']['price']:.2f}")
            
            # ANÁLISIS JERÁRQUICO
            if st.button(f"📊 ANALIZAR OPCIONES", key=f"nba_analyze_{idx}"):
                with st.spinner("Calculando probabilidades..."):
                    recomendaciones = self.engine.analizar_partido(partido)
                    
                    if recomendaciones:
                        st.success("✅ ANÁLISIS COMPLETADO - JERARQUÍA: SPREAD > TOTALES > MONEYLINE")
                        
                        for i, rec in enumerate(recomendaciones[:3]):
                            nivel_texto = {1: "🥇 NIVEL 1 (SPREAD)", 2: "🥈 NIVEL 2 (TOTALES)", 3: "🥉 NIVEL 3 (MONEYLINE)"}
                            color = "#00CC00" if rec['value'] > 0.05 else "#DDDD00"
                            
                            st.markdown(f"""
                            <div style="border-left:5px solid {color}; padding:10px; background-color:#1A1A1A; margin:5px 0;">
                                <h4>{nivel_texto[rec['nivel']]}</h4>
                                <p><b>{rec['desc']}</b></p>
                                <p>Prob: {rec['probabilidad']*100:.1f}% | Cuota: {rec['cuota']:.2f} | Value: {rec['value']*100:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No se encontraron opciones con value positivo")
