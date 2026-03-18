"""
VISUAL FUTBOL - Muestra partidos de fútbol
"""
import streamlit as st

class VisualFutbol:
    def render(self, partido, idx, liga, tracker=None):
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            local = partido.get('local', 'Local')
            visitante = partido.get('visitante', 'Visitante')
            fecha = partido.get('fecha', 'Hoy')
            
            st.markdown(f"⚽ **{local}** vs **{visitante}**")
            st.markdown(f"📅 {fecha}")
            
            key_unica = f"futbol_{liga}_{idx}_{local}_{visitante}"
            
            if st.button(f"➕ AGREGAR", key=key_unica):
                if tracker:
                    tracker.agregar_pick({
                        'partido': f"{local} vs {visitante}",
                        'liga': liga,
                        'pick': f"Partido",
                        'cuota': 2.0,
                        'deporte': 'Fútbol'
                    })
                    st.success("✓ Agregado")
            
            st.markdown("---")
