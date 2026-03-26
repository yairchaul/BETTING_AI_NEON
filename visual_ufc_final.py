# -*- coding: utf-8 -*-
"""
VISUAL UFC FINAL - Muestra EV, odds y factor clave
"""

import streamlit as st

class VisualUFCFinal:
    def __init__(self):
        pass
    
    def render(self, partido, idx, tracker, analisis=None):
        """Renderiza combate UFC con estilo NEON"""
        
        p1_nombre = partido.get('peleador1', {}).get('nombre', '')
        p2_nombre = partido.get('peleador2', {}).get('nombre', '')
        
        st.markdown(f"### 🥊 {p1_nombre} vs {p2_nombre}")
        
        if analisis:
            stats1 = analisis.get('stats_p1', {})
            stats2 = analisis.get('stats_p2', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🔴 {p1_nombre}**")
                st.caption(f"📊 Record: {stats1.get('record', 'N/A')}")
                st.caption(f"📏 Altura: {stats1.get('altura_cm', 0)} cm")
                st.caption(f"📏 Alcance: {stats1.get('alcance_cm', 0)} cm")
                st.caption(f"💥 KO Rate: {stats1.get('ko_rate', 0)}%")
                st.caption(f"🎲 Odds: {analisis.get('odds_p1', 'N/A')}")
                if analisis.get('ev_p1', 0) > 0:
                    st.caption(f"📈 EV: +{analisis.get('ev_p1', 0)}%")
            
            with col2:
                st.markdown(f"**🔵 {p2_nombre}**")
                st.caption(f"📊 Record: {stats2.get('record', 'N/A')}")
                st.caption(f"📏 Altura: {stats2.get('altura_cm', 0)} cm")
                st.caption(f"📏 Alcance: {stats2.get('alcance_cm', 0)} cm")
                st.caption(f"💥 KO Rate: {stats2.get('ko_rate', 0)}%")
                st.caption(f"🎲 Odds: {analisis.get('odds_p2', 'N/A')}")
                if analisis.get('ev_p2', 0) > 0:
                    st.caption(f"📈 EV: +{analisis.get('ev_p2', 0)}%")
            
            st.markdown("---")
            
            recomendacion = analisis.get('recomendacion', 'N/A')
            confianza = analisis.get('confianza', 0)
            metodo = analisis.get('metodo', 'Decision')
            factor_clave = analisis.get('factor_clave', '')
            factor_adicional = analisis.get('factor_adicional', '')
            etiqueta_verde = analisis.get('etiqueta_verde', False)
            
            color = "#00ff41" if "GANA" in recomendacion else "#ff6600"
            icono = "🏆" if "GANA" in recomendacion else "🥊"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a1f2a 0%, #0f1419 100%); 
                        border-radius: 12px; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-left: 4px solid {color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='color: #888; font-size: 12px;'>RECOMENDACION</span>
                        <h3 style='color: {color}; margin: 0;'>{icono} {recomendacion}</h3>
                        <p style='color: #888; font-size: 11px; margin: 5px 0 0;'>{factor_clave}</p>
                        <p style='color: #ff6600; font-size: 10px; margin: 3px 0 0;'>{factor_adicional}</p>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>CONFIANZA</span>
                        <h3 style='color: #00ff41; margin: 0;'>{confianza}%</h3>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>METODO</span>
                        <h3 style='color: #ff6600; margin: 0;'>{metodo}</h3>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(confianza / 100)
            
            if etiqueta_verde:
                st.success("🔥 PICK DE ALTA CONFIANZA - Valor positivo detectado")
        
        # Botón ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR UFC", key=f"ufc_analizar_{idx}", use_container_width=True):
                return "analizar"
        
        return None
