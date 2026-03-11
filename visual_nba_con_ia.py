"""
Visual NBA - SOLO CAMBIAMOS COLORES
"""
import streamlit as st

class VisualNBAConIA:
    def __init__(self):
        pass
    
    def render(self, partido, idx, tracker=None):
        """Renderiza partido NBA - SOLO COLORES"""
        
        with st.container():
            st.markdown(f"### 🏀 {partido['local']} vs {partido['visitante']}")
            
            odds = partido.get('odds', {})
            
            # COLUMNAS CON FONDOS OSCUROS
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="padding: 10px; background-color: #1A1A1A; border-left: 4px solid #FF6B35; border-radius: 5px;">
                    <h4 style="color:#FF6B35;">🏠 LOCAL</h4>
                    <h3 style="color:#FFFFFF;">{partido['local']}</h3>
                    <p style="color:#FF6B35; font-size:1.3em;">{odds.get('h2h', {}).get(partido['local'], 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding: 10px; background-color: #1A1A1A; border-left: 4px solid #0066CC; border-radius: 5px;">
                    <h4 style="color:#0066CC;">🚀 VISITANTE</h4>
                    <h3 style="color:#FFFFFF;">{partido['visitante']}</h3>
                    <p style="color:#0066CC; font-size:1.3em;">{odds.get('h2h', {}).get(partido['visitante'], 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="padding: 10px; background-color: #1A1A1A; border-left: 4px solid #888888; border-radius: 5px;">
                    <h4 style="color:#888888;">📊 SPREADS</h4>
                """, unsafe_allow_html=True)
                if 'spreads' in odds and partido['local'] in odds['spreads']:
                    spread = odds['spreads'][partido['local']]
                    st.markdown(f"<p style='color:#FFFFFF;'>{partido['local']} {spread['point']:+g}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#888888;'>{spread['price']:.2f}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Totales (IGUAL)
            if 'totals' in odds:
                st.markdown("**🔥 TOTALES**")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.metric("OVER", f"{odds['totals']['Over']['point']}", f"{odds['totals']['Over']['price']:.2f}")
                with col_t2:
                    st.metric("UNDER", f"{odds['totals']['Under']['point']}", f"{odds['totals']['Under']['price']:.2f}")
            
            # Botón análisis
            if st.button(f"🤖 Analizar", key=f"nba_{idx}"):
                st.info("⚡ Análisis próximo...")
