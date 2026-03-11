"""
Visual de UFC - SOLO CAMBIAMOS COLORES, MISMA ESTRUCTURA
"""
import streamlit as st

class VisualUFC:
    """Renderizador visual para combates de UFC"""
    
    def render(self, combate, idx):
        """Muestra combate - SOLO COLORES AJUSTADOS"""
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            if idx == 0:
                st.markdown(f"## 🥊 {combate['evento']}")
                st.markdown(f"**📅 {combate.get('fecha', 'Próximamente')}**")
                st.markdown("---")
            
            # Color según tipo de tarjeta
            tarjeta_color = "#FF6B35" if combate['tipo_tarjeta'] == 'Principal' else "#888888"
            st.markdown(f"<h4 style='color: {tarjeta_color};'>{combate['tipo_tarjeta']}</h4>", unsafe_allow_html=True)
            
            # DOS COLUMNAS - SOLO COLORES DE FONDO
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="padding: 15px; background-color: #1A1A1A; border-left: 4px solid #FF6B35; border-radius: 5px;">
                    <h3 style="color: #FF6B35; margin: 0;">🔴 {combate['peleador1']['nombre']}</h3>
                    <p style="color: #CCCCCC; margin: 5px 0;"><strong>Récord:</strong> {combate['peleador1']['record']}</p>
                    <p style="color: #CCCCCC; margin: 5px 0;"><strong>País:</strong> {combate['peleador1']['pais']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding: 15px; background-color: #1A1A1A; border-left: 4px solid #0066CC; border-radius: 5px;">
                    <h3 style="color: #0066CC; margin: 0;">🔵 {combate['peleador2']['nombre']}</h3>
                    <p style="color: #CCCCCC; margin: 5px 0;"><strong>Récord:</strong> {combate['peleador2']['record']}</p>
                    <p style="color: #CCCCCC; margin: 5px 0;"><strong>País:</strong> {combate['peleador2']['pais']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Botón análisis (IGUAL)
            if st.button(f"🤖 Analizar combate", key=f"ufc_{idx}"):
                st.info("⚡ Análisis multi-agente próximo...")
            
            st.markdown("---")
