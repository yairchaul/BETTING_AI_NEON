"""
VISUAL UFC - Muestra combates
"""
import streamlit as st

class VisualUFC:
    def render(self, combate, idx, tracker=None):
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            evento = combate.get('evento', 'UFC Event')
            fecha = combate.get('fecha', 'Próximamente')
            
            peleador1 = combate.get('peleador1', {})
            peleador2 = combate.get('peleador2', {})
            
            p1_nombre = peleador1.get('nombre', f'Peleador {idx+1}')
            p2_nombre = peleador2.get('nombre', f'Peleador {idx+2}')
            p1_record = peleador1.get('record', '0-0-0')
            p2_record = peleador2.get('record', '0-0-0')
            
            if idx == 0:
                st.markdown(f"### 🥊 {evento}")
                st.markdown(f"📅 {fecha}")
            
            st.markdown(f"**{p1_nombre}** ({p1_record}) vs **{p2_nombre}** ({p2_record})")
            
            if st.button(f"➕ AGREGAR", key=f"ufc_{idx}_{p1_nombre}"):
                if tracker:
                    tracker.agregar_pick({
                        'partido': f"{p1_nombre} vs {p2_nombre}",
                        'pick': f"Gana {p1_nombre}",
                        'cuota': 2.0,
                        'deporte': 'UFC'
                    })
                    st.success("✓ Agregado")
            
            st.markdown("---")
