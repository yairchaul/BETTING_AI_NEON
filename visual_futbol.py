"""
Visual específico para fútbol - CON REGLAS Y PICKS
"""
import streamlit as st
from typing import Dict, Any, Optional

class VisualFutbol:
    def __init__(self):
        self.deporte = "FUTBOL"
        self.colores = {
            'local': '#2E86AB',
            'empate': '#F24236',
            'visitante': '#A23B72',
            'fondo': '#F5F5F5',
            'texto': '#333333'
        }
    
    def render(self, evento, idx: int, tracker: Any):
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            # Cabecera
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div style='text-align: center; background-color: {self.colores["fondo"]}; 
                            padding: 10px; border-radius: 10px; margin-bottom: 15px;'>
                    <h3 style='color: {self.colores["texto"]}; margin: 0;'>
                        ⚽ {evento.equipo_local} vs {evento.equipo_visitante}
                    </h3>
                    <p style='color: #666; margin: 5px 0 0 0;'>{evento.competencia}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 3 columnas principales
            cols = st.columns(3)
            
            with cols[0]:
                self._render_equipo(
                    nombre=evento.equipo_local,
                    cuota_decimal=evento.odds_local,
                    color=self.colores['local'],
                    posicion="LOCAL"
                )
            
            with cols[1]:
                self._render_equipo(
                    nombre="EMPATE",
                    cuota_decimal=evento.odds_empate if evento.odds_empate else 0,
                    color=self.colores['empate'],
                    posicion="EMPATE"
                )
            
            with cols[2]:
                self._render_equipo(
                    nombre=evento.equipo_visitante,
                    cuota_decimal=evento.odds_visitante,
                    color=self.colores['visitante'],
                    posicion="VISITANTE"
                )
            
            # Estadísticas GF
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            stats = evento.stats if hasattr(evento, 'stats') else {}
            
            with col1:
                gf_local = stats.get('gf_local', 1.5)
                st.metric(f"⚽ {evento.equipo_local[:15]} GF", f"{gf_local:.2f}")
            with col2:
                st.markdown("<div style='text-align: center;'>📊 PROMEDIO DE GOLES</div>", unsafe_allow_html=True)
            with col3:
                gf_visitante = stats.get('gf_visitante', 1.3)
                st.metric(f"⚽ {evento.equipo_visitante[:15]} GF", f"{gf_visitante:.2f}")
            
            # Mercados adicionales
            mercados = evento.mercados if hasattr(evento, 'mercados') else {}
            if mercados:
                st.markdown("#### 📈 Mercados Adicionales")
                cols = st.columns(3)
                
                filas = [
                    ('over_3', 'Over 1.5'),
                    ('over_5', 'Over 2.5'),
                    ('over_7', 'Over 3.5'),
                    ('btts_si', 'BTTS Sí'),
                    ('btts_no', 'BTTS No'),
                    ('over_1_5_1t', 'Over 1.5 1T'),
                    ('prob_local', f'Gana {evento.equipo_local[:10]}'),
                    ('prob_empate', 'Empate'),
                    ('prob_visitante', f'Gana {evento.equipo_visitante[:10]}')
                ]
                
                for i, (key, label) in enumerate(filas):
                    col_idx = i % 3
                    with cols[col_idx]:
                        valor = mercados.get(key, 0)
                        if isinstance(valor, float):
                            st.metric(label, f"{valor*100:.1f}%")
            
            # PICKS SEGÚN REGLAS
            if hasattr(evento, 'value_bets') and evento.value_bets:
                st.markdown("#### 🎯 Picks según reglas:")
                
                for pick in evento.value_bets:
                    nivel = pick.get('nivel', 1)
                    desc = pick.get('descripcion', pick.get('mercado', 'Value bet'))
                    prob = pick.get('probabilidad', 0) * 100
                    odds = pick.get('odds', 0)
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.markdown(f"Nivel {nivel}: {desc}")
                    with col2:
                        st.markdown(f"{prob:.1f}%")
                    with col3:
                        st.markdown(f"{odds:.2f}")
                    with col4:
                        if st.button("➕", key=f"pick_{idx}_{desc}"):
                            tracker.agregar_pick({
                                'evento': f"{evento.equipo_local} vs {evento.equipo_visitante}",
                                'mercado': desc,
                                'cuota': odds,
                                'probabilidad': prob,
                                'nivel': nivel
                            })
                            st.success("✓")
    
    def _render_equipo(self, nombre: str, cuota_decimal: float, color: str, posicion: str):
        cuota_americana = self._decimal_to_american(cuota_decimal)
        st.markdown(f"""
        <div style='
            background-color: {color}20;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid {color};
            text-align: center;
            height: 150px;
        '>
            <div style='font-size: 1.2em; font-weight: bold; color: {color};'>{posicion}</div>
            <div style='font-size: 1.5em; font-weight: bold;'>{nombre}</div>
            <div style='font-size: 1.3em; color: {color};'>
                {cuota_americana} ({cuota_decimal:.2f})
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _decimal_to_american(self, decimal: float) -> str:
        if decimal <= 1:
            return "N/A"
        if decimal >= 2:
            return f"+{int((decimal - 1) * 100)}"
        else:
            return f"-{int(100 / (decimal - 1))}"

def render_futbol(evento, idx, tracker):
    visual = VisualFutbol()
    visual.render(evento, idx, tracker)
