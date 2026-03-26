"""
VISUAL UFC KO - Visualización de análisis de KO
"""
import streamlit as st

class VisualUFCKO:
    def __init__(self):
        pass
    
    def render(self, analisis_ko, analisis_metodo, p1_nombre, p2_nombre):
        """Renderiza análisis de KO"""
        
        st.markdown("### 💥 ANÁLISIS DE KO")
        
        if analisis_ko:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Probabilidad de KO", f"{analisis_ko.get('probabilidad_ko', 0):.0f}%")
                st.caption(analisis_ko.get('recomendacion', ''))
            
            with col2:
                if analisis_ko.get('etiqueta_verde', False):
                    st.success("🔥 ALERTA KO DETECTADA")
                else:
                    st.info("Probabilidad de KO moderada")
        
        if analisis_metodo:
            st.markdown("### 🎯 MÉTODO PROBABLE")
            st.write(f"**{analisis_metodo.get('metodo', 'Decisión')}**")
            st.progress(analisis_metodo.get('confianza', 50) / 100)
