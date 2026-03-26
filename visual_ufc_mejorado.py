# -*- coding: utf-8 -*-
"""
VISUAL UFC MEJORADO - Con estilo NEON y Gemini decisor final
"""

import streamlit as st
import sqlite3

class VisualUFCMejorado:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
    
    def obtener_datos_peleador(self, nombre):
        """Obtiene datos REALES del peleador desde SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling
                FROM peleadores_ufc 
                WHERE nombre LIKE ? OR nombre = ?
                LIMIT 1
            """, (f"%{nombre}%", nombre))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'nombre': row[0],
                    'record': row[1] if row[1] else '0-0-0',
                    'altura': row[2] if row[2] else 'N/A',
                    'peso': row[3] if row[3] else 'N/A',
                    'alcance': row[4] if row[4] else 'N/A',
                    'postura': row[5] if row[5] else 'Desconocida',
                    'ko_rate': row[6] if row[6] else 0.5,
                    'grappling': row[7] if row[7] else 0.5
                }
            return None
        except Exception as e:
            return None
    
    def render(self, partido, idx, tracker, datos_peleador1=None, datos_peleador2=None, 
               analisis_heurístico=None, analisis_gemini=None, analisis_premium=None):
        """Renderiza una tarjeta de combate UFC con estilo NEON"""
        
        p1_nombre = partido.get('peleador1', {}).get('nombre', '')
        p2_nombre = partido.get('peleador2', {}).get('nombre', '')
        
        # Intentar obtener datos reales de la DB si no vienen
        if not datos_peleador1 and p1_nombre:
            datos_peleador1 = self.obtener_datos_peleador(p1_nombre)
        if not datos_peleador2 and p2_nombre:
            datos_peleador2 = self.obtener_datos_peleador(p2_nombre)
        
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
                    <h2 style='color: #fff; text-shadow: 0 0 5px #ff6600; margin: 0;'>{p1_nombre}</h2>
                </div>
                <div style='text-align: center; flex: 0.5;'>
                    <h1 style='color: #00ff41; text-shadow: 0 0 10px #00ff41; margin: 0;'>VS</h1>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff; text-shadow: 0 0 5px #ff6600; margin: 0;'>{p2_nombre}</h2>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Datos de peleadores
        if datos_peleador1 and datos_peleador2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🔴 {p1_nombre}**")
                st.caption(f"📊 Record: {datos_peleador1.get('record', 'N/A')}")
                st.caption(f"📏 Altura: {datos_peleador1.get('altura', 'N/A')}")
                st.caption(f"📏 Alcance: {datos_peleador1.get('alcance', 'N/A')}")
                st.caption(f"💥 KO Rate: {int(datos_peleador1.get('ko_rate', 0) * 100)}%")
                st.caption(f"🤼 Grappling: {int(datos_peleador1.get('grappling', 0) * 100)}%")
            
            with col2:
                st.markdown(f"**🔵 {p2_nombre}**")
                st.caption(f"📊 Record: {datos_peleador2.get('record', 'N/A')}")
                st.caption(f"📏 Altura: {datos_peleador2.get('altura', 'N/A')}")
                st.caption(f"📏 Alcance: {datos_peleador2.get('alcance', 'N/A')}")
                st.caption(f"💥 KO Rate: {int(datos_peleador2.get('ko_rate', 0) * 100)}%")
                st.caption(f"🤼 Grappling: {int(datos_peleador2.get('grappling', 0) * 100)}%")
        
        # Boton ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR UFC", key=f"ufc_analizar_{idx}", use_container_width=True):
                return "analizar"
        
        # Mostrar analisis si existe
        if analisis_heurístico:
            st.markdown("---")
            
            recomendacion = analisis_heurístico.get('recomendacion', 'N/A')
            confianza = analisis_heurístico.get('confianza', 0)
            metodo = analisis_heurístico.get('metodo', 'Decision')
            factor_clave = analisis_heurístico.get('factor_clave', '')
            etiqueta_verde = analisis_heurístico.get('etiqueta_verde', False)
            
            color_resultado = "#00ff41" if "GANA" in recomendacion else "#ff6600"
            icono = "🏆" if "GANA" in recomendacion else "🥊"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a1f2a 0%, #0f1419 100%); 
                        border-radius: 12px; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-left: 4px solid {color_resultado};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='color: #888; font-size: 12px;'>RECOMENDACION</span>
                        <h3 style='color: {color_resultado}; margin: 0;'>{icono} {recomendacion}</h3>
                        <p style='color: #888; font-size: 11px; margin: 5px 0 0;'>{factor_clave}</p>
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
        
        # Gemini IA
        if analisis_gemini:
            st.markdown("---")
            st.markdown("### 🤖 GEMINI - DECISOR FINAL")
            st.info(analisis_gemini)
        
        return None
