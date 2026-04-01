# -*- coding: utf-8 -*-
"""
VISUAL UFC FINAL - Muestra datos desde BD
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
            logger.debug(f"Error: {e}")
            return {'record': 'N/A', 'altura': 0, 'alcance': 0, 'ko_rate': 0, 'odds': 'N/A'}
    
    def render(self, partido, idx, tracker, analisis=None):
        """Renderiza combate UFC"""
        
        # Extraer nombres
        if isinstance(partido, dict):
            p1_data = partido.get('peleador1', {})
            p2_data = partido.get('peleador2', {})
            p1_nombre = p1_data.get('nombre', '') if isinstance(p1_data, dict) else str(p1_data)
            p2_nombre = p2_data.get('nombre', '') if isinstance(p2_data, dict) else str(p2_data)
        else:
            p1_nombre = ''
            p2_nombre = ''
        
        datos_p1 = self._obtener_datos_peleador(p1_nombre)
        datos_p2 = self._obtener_datos_peleador(p2_nombre)
        
        # Mostrar tarjeta
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f0f1a 0%, #1a1f2a 100%); 
                    border-radius: 15px; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border: 1px solid #00ff41;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff;'>{p1_nombre or '?'}</h2>
                    <p style='color: #00ff41;'>🎲 {datos_p1['odds']}</p>
                </div>
                <div style='text-align: center; flex: 0.5;'>
                    <h1 style='color: #00ff41;'>VS</h1>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff;'>{p2_nombre or '?'}</h2>
                    <p style='color: #00ff41;'>🎲 {datos_p2['odds']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Datos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔴 {p1_nombre or 'Peleador 1'}**")
            st.caption(f"📊 Record: {datos_p1['record']}")
            if datos_p1['altura'] > 0:
                st.caption(f"📏 Altura: {datos_p1['altura']} cm")
            if datos_p1['alcance'] > 0:
                st.caption(f"📏 Alcance: {datos_p1['alcance']} cm")
            st.caption(f"💥 KO Rate: {datos_p1['ko_rate']}%")
        
        with col2:
            st.markdown(f"**🔵 {p2_nombre or 'Peleador 2'}**")
            st.caption(f"📊 Record: {datos_p2['record']}")
            if datos_p2['altura'] > 0:
                st.caption(f"📏 Altura: {datos_p2['altura']} cm")
            if datos_p2['alcance'] > 0:
                st.caption(f"📏 Alcance: {datos_p2['alcance']} cm")
            st.caption(f"💥 KO Rate: {datos_p2['ko_rate']}%")
        
        # Botón ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR UFC", key=f"ufc_analizar_{idx}", use_container_width=True):
                return "analizar"
        
        # Resultados
        if analisis:
            st.markdown("---")
            recomendacion = analisis.get('recomendacion', 'N/A')
            confianza = analisis.get('confianza', 0)
            metodo = analisis.get('metodo', 'Decisión')
            
            st.markdown(f"""
            <div style='background: #1a1f2a; border-radius: 12px; padding: 15px; border-left: 4px solid #00ff41;'>
                <span style='color: #888;'>RECOMENDACIÓN</span>
                <h3 style='color: #00ff41;'>🥊 {recomendacion}</h3>
                <span>CONFIANZA: {confianza}% | MÉTODO: {metodo}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(confianza / 100)
        
        return None
