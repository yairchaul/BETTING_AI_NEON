# -*- coding: utf-8 -*-
"""
VISUAL FÚTBOL MEJORADO - Sin mostrar código HTML
"""

import streamlit as st
import sqlite3

class VisualFutbolTriple:
    def __init__(self):
        self.db_path = 'data/betting_stats.db'
    
    def _obtener_datos_mock(self, equipo):
        """Genera datos mock basados en fuerza percibida"""
        equipos_fuertes = ["Manchester", "Liverpool", "Arsenal", "Chelsea", "Barcelona", 
                          "Real Madrid", "Bayern", "PSG", "Juventus", "Milan", "Inter"]
        
        if any(fuerte in equipo for fuerte in equipos_fuertes):
            return {
                'goles_favor': [3, 2, 4, 1, 3],
                'goles_contra': [1, 1, 2, 1, 0],
                'victorias': 4,
                'promedio': 2.6
            }
        else:
            return {
                'goles_favor': [1, 0, 1, 1, 0],
                'goles_contra': [2, 1, 2, 1, 2],
                'victorias': 1,
                'promedio': 0.8
            }
    
    def obtener_ultimos_5_detalle(self, equipo):
        """Obtiene últimos 5 partidos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT puntos_favor, puntos_contra, fecha 
                FROM historial_equipos 
                WHERE nombre_equipo = ? AND deporte = 'futbol'
                ORDER BY fecha DESC LIMIT 5
            ''', (equipo,))
            rows = cursor.fetchall()
            conn.close()
            
            if rows and len(rows) >= 3:
                partidos = []
                for r in rows:
                    partidos.append({
                        'goles_favor': int(r[0]),
                        'goles_contra': int(r[1]),
                        'fecha': r[2][4:6] + '/' + r[2][6:8] if r[2] else 'N/A'
                    })
                return partidos
        except:
            pass
        
        mock = self._obtener_datos_mock(equipo)
        partidos = []
        for i in range(5):
            partidos.append({
                'goles_favor': mock['goles_favor'][i],
                'goles_contra': mock['goles_contra'][i],
                'fecha': 'Mock'
            })
        return partidos
    
    def render(self, partido, idx, liga, tracker, stats_data=None, 
               analisis_heurístico=None, analisis_gemini=None, analisis_premium=None):
        
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        fecha = partido.get('fecha', '')
        
        racha_local = self.obtener_ultimos_5_detalle(local)
        racha_visit = self.obtener_ultimos_5_detalle(visitante)
        
        # Tarjeta NEON
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f0f1a 0%, #1a1f2a 100%); 
                    border-radius: 15px; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border: 1px solid #00ff41;'>
            <div style='display: flex; justify-content: space-between;'>
                <div style='text-align: center; flex: 1;'>
                    <h2>{local}</h2>
                    <p style='color: #ff6600;'>{liga}</p>
                </div>
                <div style='text-align: center; flex: 0.5;'>
                    <h1 style='color: #00ff41;'>VS</h1>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <h2>{visitante}</h2>
                    <p style='color: #ff6600;'>{liga}</p>
                </div>
            </div>
            <div style='text-align: center; margin-top: 8px;'>
                <span style='color: #888;'>📅 {fecha[:10] if fecha else 'Fecha por definir'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Últimos 5 partidos - SIN HTML LITERAL
        st.markdown("### 📊 ÚLTIMOS 5 PARTIDOS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔴 {local}**")
            if racha_local:
                # Mostrar como texto plano, no HTML
                resultados = " | ".join([f"{p['goles_favor']}-{p['goles_contra']}" for p in racha_local])
                st.write(f"📈 {resultados}")
                
                goles_favor = [p['goles_favor'] for p in racha_local]
                st.caption(f"⚽ Promedio: {sum(goles_favor)/len(goles_favor):.1f} goles")
                victorias = sum(1 for p in racha_local if p['goles_favor'] > p['goles_contra'])
                st.caption(f"📈 Racha: {victorias}W / {5-victorias}L")
            else:
                st.caption("📊 Datos no disponibles")
        
        with col2:
            st.markdown(f"**🔵 {visitante}**")
            if racha_visit:
                resultados = " | ".join([f"{p['goles_favor']}-{p['goles_contra']}" for p in racha_visit])
                st.write(f"📈 {resultados}")
                
                goles_favor = [p['goles_favor'] for p in racha_visit]
                st.caption(f"⚽ Promedio: {sum(goles_favor)/len(goles_favor):.1f} goles")
                victorias = sum(1 for p in racha_visit if p['goles_favor'] > p['goles_contra'])
                st.caption(f"📈 Racha: {victorias}W / {5-victorias}L")
            else:
                st.caption("📊 Datos no disponibles")
        
        # Botón ANALIZAR
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 ANALIZAR FÚTBOL", key=f"fut_analizar_{liga}_{idx}", use_container_width=True):
                return "analizar"
        
        # Mostrar resultados
        if analisis_heurístico:
            st.markdown("---")
            recomendacion = analisis_heurístico.get('recomendacion', 'N/A')
            confianza = analisis_heurístico.get('confianza', 0)
            total_proyectado = analisis_heurístico.get('total_proyectado', 0)
            
            st.markdown(f"""
            <div style='background: #1a1f2a; border-radius: 12px; padding: 15px; border-left: 4px solid #00ff41;'>
                <span style='color: #888;'>RECOMENDACIÓN</span>
                <h3 style='color: #00ff41;'>⚽ {recomendacion}</h3>
                <span style='color: #888;'>CONFIANZA: {confianza}% | GOLES IA: {total_proyectado}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(confianza / 100)
        
        if analisis_gemini:
            st.markdown("### 🤖 GEMINI - DECISOR FINAL")
            st.info(analisis_gemini)
        
        return None
