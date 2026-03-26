# -*- coding: utf-8 -*-
"""
VISUAL MLB MEJORADO - Estilo NEON similar a NBA
Muestra spread (run line), over/under, y resultados con el mismo diseño
"""

import streamlit as st

class VisualMLB:
    def __init__(self):
        pass
    
    def render(self, partido, idx, tracker, analisis=None, stats_local=None, stats_visit=None):
        """Renderiza partido MLB con estilo NEON"""
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        odds = partido.get('odds', {})
        records = partido.get('records', {})
        hora = partido.get('hora', '')
        lanzadores = partido.get('lanzadores', '')
        
        # Extraer datos MLB
        runline_local = odds.get('spread', {}).get('local', 'N/A')
        runline_visit = odds.get('spread', {}).get('visitante', 'N/A')
        over_under = odds.get('over_under', 'N/A')
        ml_local = odds.get('moneyline', {}).get('local', 'N/A')
        ml_visit = odds.get('moneyline', {}).get('visitante', 'N/A')
        
        # Tarjeta NEON
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f0f1a 0%, #1a1f2a 100%); 
                    border-radius: 15px; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border: 1px solid #00ff41;
                    box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff; text-shadow: 0 0 5px #ff6600; margin: 0;'>{local}</h2>
                    <p style='color: #ff6600; margin: 0;'>{records.get('local', '0-0')}</p>
                    <p style='color: #00ff41; font-size: 14px;'>ML: {ml_local}</p>
                </div>
                <div style='text-align: center; flex: 0.5;'>
                    <h1 style='color: #00ff41; text-shadow: 0 0 10px #00ff41; margin: 0;'>VS</h1>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff; text-shadow: 0 0 5px #ff6600; margin: 0;'>{visitante}</h2>
                    <p style='color: #ff6600; margin: 0;'>{records.get('visitante', '0-0')}</p>
                    <p style='color: #00ff41; font-size: 14px;'>ML: {ml_visit}</p>
                </div>
            </div>
            <div style='display: flex; justify-content: center; gap: 30px; margin-top: 15px; padding-top: 10px; border-top: 1px solid #333;'>
                <div style='text-align: center;'>
                    <span style='color: #888; font-size: 12px;'>RUN LINE</span>
                    <p style='color: #fff; margin: 0;'>{local}: {runline_local} | {visitante}: {runline_visit}</p>
                </div>
                <div style='text-align: center;'>
                    <span style='color: #888; font-size: 12px;'>OVER/UNDER</span>
                    <p style='color: #fff; margin: 0;'>OVER {over_under} / UNDER {over_under}</p>
                </div>
            </div>
            <div style='display: flex; justify-content: center; gap: 20px; margin-top: 8px;'>
                <span style='color: #888; font-size: 11px;'>⚾ {lanzadores}</span>
                <span style='color: #888; font-size: 11px;'>🕐 {hora}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Boton ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR MLB", key=f"mlb_analizar_{idx}", use_container_width=True):
                return "analizar"
        
        # Mostrar resultados si existen
        if analisis:
            st.markdown("---")
            
            recomendacion = analisis.get('recomendacion', 'N/A')
            confianza = analisis.get('confianza', 0)
            total_proyectado = analisis.get('total_proyectado', 0)
            proyeccion_local = analisis.get('proyeccion_local', 0)
            proyeccion_visitante = analisis.get('proyeccion_visitante', 0)
            etiqueta_verde = analisis.get('etiqueta_verde', False)
            
            if "OVER" in recomendacion:
                icono = "📈"
                color_resultado = "#00ff41"
            elif "UNDER" in recomendacion:
                icono = "📉"
                color_resultado = "#ff6600"
            elif "Run Line" in recomendacion or "run line" in recomendacion.lower():
                icono = "🎯"
                color_resultado = "#00ff41"
            else:
                icono = "⚾"
                color_resultado = "#ff6600"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a1f2a 0%, #0f1419 100%); 
                        border-radius: 12px; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-left: 4px solid {color_resultado};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='color: #888; font-size: 12px;'>RECOMENDACION</span>
                        <h3 style='color: {color_resultado}; margin: 0; text-shadow: 0 0 5px {color_resultado};'>{icono} {recomendacion}</h3>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>CONFIANZA</span>
                        <h3 style='color: #00ff41; margin: 0;'>{confianza}%</h3>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>TOTAL IA</span>
                        <h3 style='color: #ff6600; margin: 0;'>{total_proyectado}</h3>
                    </div>
                </div>
                <div style='margin-top: 10px;'>
                    <span style='color: #888; font-size: 11px;'>Proyeccion: {proyeccion_local:.1f} - {proyeccion_visitante:.1f} carreras</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(confianza / 100)
            
            if etiqueta_verde:
                st.success("🔥 PICK DE ALTA CONFIANZA - Valor positivo detectado")
            
            # Gemini decisor final
            if analisis.get('gemini_decision'):
                st.markdown("---")
                st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                st.info(analisis['gemini_decision'])
        
        return None
