# -*- coding: utf-8 -*-
"""
VISUAL UFC FINAL - Con conversión automática pulgadas a cm
Versión unificada para local y cloud
"""

import streamlit as st
import sqlite3
import logging

logger = logging.getLogger(__name__)

class VisualUFCFinal:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
    
    def _pulgadas_a_cm(self, valor):
        """Convierte pulgadas a cm automáticamente"""
        if not valor or valor == 'N/A' or valor == 'None':
            return 0
        try:
            num = float(valor)
            if 50 <= num <= 90:  # pulgadas
                return int(num * 2.54)
            elif 150 <= num <= 220:  # ya cm
                return int(num)
            else:
                return 0
        except:
            return 0
    
    def _obtener_datos_peleador(self, nombre):
        """Obtiene todos los datos del peleador desde BD"""
        if not nombre:
            return {'record': 'N/A', 'altura': 'N/A', 'alcance': 'N/A', 'ko_rate': 0, 'odds': 'N/A'}
        
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
                    'altura': row[1] if row[1] else 'N/A',
                    'alcance': row[2] if row[2] else 'N/A',
                    'ko_rate': int(float(row[3]) * 100) if row[3] else 0,
                    'odds': row[4] if row[4] else 'N/A'
                }
            return {'record': 'N/A', 'altura': 'N/A', 'alcance': 'N/A', 'ko_rate': 0, 'odds': 'N/A'}
        except Exception as e:
            logger.debug(f"Error obteniendo datos de {nombre}: {e}")
            return {'record': 'N/A', 'altura': 'N/A', 'alcance': 'N/A', 'ko_rate': 0, 'odds': 'N/A'}
    
    def render(self, partido, idx, tracker, analisis=None):
        """Renderiza combate UFC con estilo NEON"""
        
        p1_nombre = partido.get('peleador1', {}).get('nombre', '') if isinstance(partido.get('peleador1'), dict) else partido.get('peleador1', '')
        p2_nombre = partido.get('peleador2', {}).get('nombre', '') if isinstance(partido.get('peleador2'), dict) else partido.get('peleador2', '')
        
        datos_p1 = self._obtener_datos_peleador(p1_nombre)
        datos_p2 = self._obtener_datos_peleador(p2_nombre)
        
        # Convertir alturas y alcances automáticamente
        altura1_cm = self._pulgadas_a_cm(datos_p1.get('altura', 'N/A'))
        altura2_cm = self._pulgadas_a_cm(datos_p2.get('altura', 'N/A'))
        alcance1_cm = self._pulgadas_a_cm(datos_p1.get('alcance', 'N/A'))
        alcance2_cm = self._pulgadas_a_cm(datos_p2.get('alcance', 'N/A'))
        
        # Mostrar tarjeta con estilo NEON
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
                    <p style='color: #00ff41; font-size: 18px; font-weight: bold; margin: 5px 0;'>🎲 {datos_p1.get('odds', 'N/A')}</p>
                </div>
                <div style='text-align: center; flex: 0.5;'>
                    <h1 style='color: #00ff41; text-shadow: 0 0 10px #00ff41; margin: 0;'>VS</h1>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <h2 style='color: #fff; margin: 0;'>{p2_nombre or 'Peleador 2'}</h2>
                    <p style='color: #00ff41; font-size: 18px; font-weight: bold; margin: 5px 0;'>🎲 {datos_p2.get('odds', 'N/A')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Datos detallados
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔴 {p1_nombre or 'Peleador 1'}**")
            st.caption(f"📊 Record: {datos_p1.get('record', 'N/A')}")
            st.caption(f"📏 Altura: {altura1_cm} cm" if altura1_cm > 0 else "📏 Altura: N/A")
            st.caption(f"📏 Alcance: {alcance1_cm} cm" if alcance1_cm > 0 else "📏 Alcance: N/A")
            st.caption(f"💥 KO Rate: {datos_p1.get('ko_rate', 0)}%")
        
        with col2:
            st.markdown(f"**🔵 {p2_nombre or 'Peleador 2'}**")
            st.caption(f"📊 Record: {datos_p2.get('record', 'N/A')}")
            st.caption(f"📏 Altura: {altura2_cm} cm" if altura2_cm > 0 else "📏 Altura: N/A")
            st.caption(f"📏 Alcance: {alcance2_cm} cm" if alcance2_cm > 0 else "📏 Alcance: N/A")
            st.caption(f"💥 KO Rate: {datos_p2.get('ko_rate', 0)}%")
        
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
            edge = analisis.get('edge', 0)
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
                st.success(f"🔥 PICK DE ALTA CONFIANZA - Edge: {edge:.2f}")
        
        return None
