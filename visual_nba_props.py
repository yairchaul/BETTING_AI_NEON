"""
VISUAL NBA PROPS - Visualización de props de triples
"""
import streamlit as st

class VisualNBAProps:
    def __init__(self):
        pass
    
    def render(self, analisis, partido_info=""):
        """Renderiza análisis de props"""
        
        if not analisis or not analisis.get('jugadores'):
            st.info("No hay datos de props disponibles")
            return
        
        st.markdown("### 🏀 PROPS DE TRIPLES")
        
        for jugador in analisis.get('jugadores', []):
            nombre = jugador.get('nombre', '')
            triples = jugador.get('triples', 0)
            prob = jugador.get('probabilidad', 0)
            rec = jugador.get('recomendacion', '')
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{nombre}**")
            with col2:
                st.write(f"Promedio: {triples} triples")
            with col3:
                if prob >= 65:
                    st.success(f"🎯 {rec} ({prob}%)")
                else:
                    st.warning(f"⚠️ {rec} ({prob}%)")
