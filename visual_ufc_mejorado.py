"""
Visual UFC - Con análisis completo y colores oscuros
"""
import streamlit as st
from ufc_analysis_engine import UFCAnalysisEngine

class VisualUFC:
    def __init__(self):
        self.analyzer = UFCAnalysisEngine()
    
    def render(self, combate, idx):
        """Muestra combate con análisis"""
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            if idx == 0:
                st.markdown(f"## 🥊 {combate['evento']}")
                st.markdown(f"📅 {combate.get('fecha', 'Próximamente')}")
                st.markdown("---")
            
            # Tarjeta (Principal/Preliminar)
            tarjeta_color = "#FF6B35" if combate['tipo_tarjeta'] == 'Principal' else "#888888"
            st.markdown(f"<h4 style='color: {tarjeta_color};'>{combate['tipo_tarjeta']}</h4>", unsafe_allow_html=True)
            
            # Dos columnas con fondo oscuro y bordes naranja
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="padding: 15px; background-color: #1A1A1A; border-left: 4px solid #FF6B35; border-radius: 5px;">
                    <h3 style="color: #FF6B35;">🔴 {combate['peleador1']['nombre']}</h3>
                    <p style="color: #CCCCCC;">📊 Récord: {combate['peleador1']['record']}</p>
                    <p style="color: #CCCCCC;">🌍 País: {combate['peleador1']['pais']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding: 15px; background-color: #1A1A1A; border-left: 4px solid #0066CC; border-radius: 5px;">
                    <h3 style="color: #0066CC;">🔵 {combate['peleador2']['nombre']}</h3>
                    <p style="color: #CCCCCC;">📊 Récord: {combate['peleador2']['record']}</p>
                    <p style="color: #CCCCCC;">🌍 País: {combate['peleador2']['pais']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Botón de análisis
            if st.button(f"🤖 ANALIZAR COMBATE", key=f"ufc_analyze_{idx}"):
                with st.spinner("Analizando con simulación Monte Carlo..."):
                    analisis = self.analyzer.analizar_combate(combate)
                    
                    # Determinar favorito
                    p1_nombre = combate['peleador1']['nombre']
                    p2_nombre = combate['peleador2']['nombre']
                    prob_p1 = analisis['ganador'][p1_nombre]
                    prob_p2 = analisis['ganador'][p2_nombre]
                    
                    favorito = p1_nombre if prob_p1 > prob_p2 else p2_nombre
                    prob_favorito = max(prob_p1, prob_p2)
                    
                    st.success("✅ ANÁLISIS COMPLETADO")
                    
                    # Resultados en columnas
                    col_a1, col_a2, col_a3 = st.columns(3)
                    
                    with col_a1:
                        st.metric("🥇 GANADOR PROBABLE", favorito, f"{prob_favorito*100:.1f}%")
                    
                    with col_a2:
                        st.metric("👊 MÉTODO PROBABLE", analisis['metodo_mas_probable'])
                    
                    with col_a3:
                        st.metric("🔢 ROUND PROBABLE", analisis['round_mas_probable'])
                    
                    # Probabilidad de finalización
                    prob_fin = analisis['probabilidad_finalizacion'] * 100
                    color_fin = "#00CC00" if prob_fin > 70 else "#DDDD00"
                    st.markdown(f"""
                    <div style="background-color:#1A1A1A; padding:10px; border-radius:5px; text-align:center;">
                        <h4 style="color:{color_fin};">⚡ FINALIZACIÓN ANTES DEL LÍMITE: {prob_fin:.1f}%</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Detalle de métodos
                    with st.expander("📊 Ver distribución completa"):
                        st.json(analisis['detalle'])
