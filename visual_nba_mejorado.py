# -*- coding: utf-8 -*-
import streamlit as st

class VisualNBAMejorado:
    def __init__(self):
        pass
    
    def render(self, partido, idx, tracker, analisis_heuristico=None, analisis_gemini=None, analisis_premium=None):
        """Renderiza partido NBA con estilo NEON"""
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        odds = partido.get('odds', {})
        records = partido.get('records', {})
        
        # Extraer datos
        spread_local = odds.get('spread', {}).get('local', 'N/A')
        spread_visit = odds.get('spread', {}).get('visitante', 'N/A')
        over_under = odds.get('over_under', 'N/A')
        ml_local = odds.get('moneyline', {}).get('local', 'N/A')
        ml_visit = odds.get('moneyline', {}).get('visitante', 'N/A')
        
        # Estilo de tarjeta
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
                    <span style='color: #888; font-size: 12px;'>SPREAD</span>
                    <p style='color: #fff; margin: 0;'>{local}: {spread_local} | {visitante}: {spread_visit}</p>
                </div>
                <div style='text-align: center;'>
                    <span style='color: #888; font-size: 12px;'>OVER/UNDER</span>
                    <p style='color: #fff; margin: 0;'>OVER {over_under} / UNDER {over_under}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR CON MOTOR + GEMINI", key=f"analyze_nba_{idx}", use_container_width=True):
                return "analizar"
        
        # Mostrar resultados si existen
        if analisis_heuristico:
            st.markdown("---")
            
            recomendacion = analisis_heuristico.get('recomendacion', 'N/A')
            ev = analisis_heuristico.get('ev_mejor', 0)
            confianza = analisis_heuristico.get('confianza', 0)
            total_proyectado = analisis_heuristico.get('total_proyectado', 0)
            detalle = analisis_heuristico.get('detalle', '')
            etiqueta_verde = analisis_heuristico.get('etiqueta_verde', False)
            
            color_resultado = "#00ff41" if "OVER" in recomendacion or "GANA" in recomendacion else "#ff6600"
            icono = "📈" if "OVER" in recomendacion else ("📉" if "UNDER" in recomendacion else "🎯")
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a1f2a 0%, #0f1419 100%); 
                        border-radius: 12px; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-left: 4px solid {color_resultado};
                        border-right: 1px solid #333;
                        border-top: 1px solid #333;
                        border-bottom: 1px solid #333;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='color: #888; font-size: 12px;'>RECOMENDACIÓN</span>
                        <h3 style='color: {color_resultado}; margin: 0; text-shadow: 0 0 5px {color_resultado};'>{icono} {recomendacion}</h3>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>VALOR ESPERADO (EV)</span>
                        <h3 style='color: {"#00ff41" if ev >= 5 else "#ff6600"}; margin: 0;'>{ev}%</h3>
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
                    <span style='color: #888; font-size: 11px;'>{detalle}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Barra de progreso de confianza
            st.progress(confianza / 100)
            
            if etiqueta_verde or ev >= 8:
                st.success("🔥 PICK DE ALTA CONFIANZA - Valor positivo detectado")
            
            if analisis_gemini:
                st.markdown("---")
                st.markdown("### 🤖 GEMINI - DECISOR FINAL")
                st.info(analisis_gemini)
            
            if analisis_premium:
                st.markdown("---")
                st.markdown("### 🔬 PREMIUM ANALYTICS")
                if isinstance(analisis_premium, dict):
                    st.write(analisis_premium.get('analisis', 'Pendiente'))
                else:
                    st.write(str(analisis_premium))
        
        return None

