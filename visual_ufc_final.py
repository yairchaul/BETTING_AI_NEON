# -*- coding: utf-8 -*-
"""
VISUAL UFC FINAL - Versión limpia y definitiva
Muestra datos de peleadores desde BD
"""

import streamlit as st
import sqlite3
import logging

logger = logging.getLogger(__name__)

class VisualUFCFinal:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
    
    def _obtener_datos_peleador(self, nombre):
        """Obtiene datos del peleador desde BD"""
        if not nombre:
            return {'record': 'N/A', 'altura': 0, 'alcance': 0, 'ko_rate': 0, 'odds': 'N/A'}
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT record, altura, alcance, ko_rate, odds 
                FROM peleadores_ufc 
                WHERE nombre = ? OR nombre LIKE ?
                LIMIT 1
            """, (nombre, f"%{nombre}%"))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'record': row[0] if row[0] else 'N/A',
                    'altura': int(row[1]) if row[1] else 0,
                    'alcance': int(row[2]) if row[2] else 0,
                    'ko_rate': int(float(row[3]) * 100) if row[3] else 0,
                    'odds': row[4] if row[4] else 'N/A'
                }
            return {'record': 'N/A', 'altura': 0, 'alcance': 0, 'ko_rate': 0, 'odds': 'N/A'}
        except Exception as e:
            logger.debug(f"Error obteniendo {nombre}: {e}")
            return {'record': 'N/A', 'altura': 0, 'alcance': 0, 'ko_rate': 0, 'odds': 'N/A'}
    
    def render(self, partido, idx, tracker, analisis=None):
        """Renderiza combate UFC con estilo NEON"""
        
        # Extraer nombres del partido
        p1_nombre = ''
        p2_nombre = ''
        
        if isinstance(partido, dict):
            p1_data = partido.get('peleador1', {})
            p2_data = partido.get('peleador2', {})
            
            if isinstance(p1_data, dict):
                p1_nombre = p1_data.get('nombre', '')
            else:
                p1_nombre = str(p1_data)
            
            if isinstance(p2_data, dict):
                p2_nombre = p2_data.get('nombre', '')
            else:
                p2_nombre = str(p2_data)
        
        # Obtener datos de BD
        datos_p1 = self._obtener_datos_peleador(p1_nombre)
        datos_p2 = self._obtener_datos_peleador(p2_nombre)
        
        # Mostrar tarjeta NEON
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f0f1a 0%, #1a1f2a 100%); 
                    border-radius: 15px; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border: 1px solid #00ff41;
                    box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff; margin: 0;'>{p1_nombre or 'Peleador 1'}</h2>
                    <p style='color: #00ff41; font-size: 18px; font-weight: bold; margin: 5px 0;'>🎲 {datos_p1['odds']}</p>
                </div>
                <div style='text-align: center; flex: 0.5;'>
                    <h1 style='color: #00ff41; text-shadow: 0 0 10px #00ff41; margin: 0;'>VS</h1>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff; margin: 0;'>{p2_nombre or 'Peleador 2'}</h2>
                    <p style='color: #00ff41; font-size: 18px; font-weight: bold; margin: 5px 0;'>🎲 {datos_p2['odds']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Datos detallados
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔴 {p1_nombre or 'Peleador 1'}**")
            st.caption(f"📊 Record: {datos_p1['record']}")
            if datos_p1['altura'] > 0:
                st.caption(f"📏 Altura: {datos_p1['altura']} cm")
            else:
                st.caption("📏 Altura: N/A")
            if datos_p1['alcance'] > 0:
                st.caption(f"📏 Alcance: {datos_p1['alcance']} cm")
            else:
                st.caption("📏 Alcance: N/A")
            st.caption(f"💥 KO Rate: {datos_p1['ko_rate']}%")
        
        with col2:
            st.markdown(f"**🔵 {p2_nombre or 'Peleador 2'}**")
            st.caption(f"📊 Record: {datos_p2['record']}")
            if datos_p2['altura'] > 0:
                st.caption(f"📏 Altura: {datos_p2['altura']} cm")
            else:
                st.caption("📏 Altura: N/A")
            if datos_p2['alcance'] > 0:
                st.caption(f"📏 Alcance: {datos_p2['alcance']} cm")
            else:
                st.caption("📏 Alcance: N/A")
            st.caption(f"💥 KO Rate: {datos_p2['ko_rate']}%")
        
        # Botón ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR UFC", key=f"ufc_analizar_{idx}", use_container_width=True):
                return "analizar"
        
        # Resultados del análisis
        if analisis:
            st.markdown("---")
            
            recomendacion = analisis.get('recomendacion', 'N/A')
            confianza = analisis.get('confianza', 0)
            metodo = analisis.get('metodo', 'Decisión')
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
                        <span style='color: #888; font-size: 12px;'>RECOMENDACIÓN</span>
                        <h3 style='color: {color}; margin: 0;'>{icono} {recomendacion}</h3>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>CONFIANZA</span>
                        <h3 style='color: #00ff41; margin: 0;'>{confianza}%</h3>
                    </div>
                    <div style='text-align: center;'>
                        <span style='color: #888; font-size: 12px;'>MÉTODO</span>
                        <h3 style='color: #ff6600; margin: 0;'>{metodo}</h3>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(confianza / 100)
            
            if etiqueta_verde:
                st.success("🔥 PICK DE ALTA CONFIANZA - Valor positivo detectado")
        
        return None
