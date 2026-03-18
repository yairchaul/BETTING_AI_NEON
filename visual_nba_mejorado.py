"""
VISUAL NBA MEJORADO - Diseño exacto como la imagen
"""
import streamlit as st

class VisualNBAMejorado:
    def __init__(self):
        self.colores = {
            'local': '#FF6B35',
            'visitante': '#0066CC',
            'over': '#4CAF50',
            'under': '#f44336',
            'green': '#4CAF50',
            'yellow': '#FFC107',
            'blue': '#2196F3',
            'red': '#f44336'
        }
    
    def render(self, partido, idx, tracker=None, 
               analisis_heurístico=None, 
               analisis_gemini=None, 
               analisis_premium=None):
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            local = partido.get('local', 'Local')
            visitante = partido.get('visitante', 'Visitante')
            hora = partido.get('hora', '20:00')
            odds = partido.get('odds', {})
            records = partido.get('records', {})
            
            # ============================================
            # ENCABEZADO (NBA | HORA | EQUIPOS)
            # ============================================
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 15px; border-radius: 10px 10px 0 0; border-left: 5px solid #FF6B35;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #FF6B35; font-weight: bold; font-size: 20px;">🏀 NBA</span>
                    <span style="color: #888;">{hora}</span>
                </div>
                <h2 style="color: white; text-align: center; margin: 10px 0; font-size: 28px;">
                    {local} <span style="color: #FFA500;">({records.get('local', '0-0')})</span> 
                    <span style="color: #666;">VS</span> 
                    {visitante} <span style="color: #FFA500;">({records.get('visitante', '0-0')})</span>
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            # ============================================
            # TÍTULOS DE SECCIONES (MONEYLINE | SPREAD | OVER/UNDER)
            # ============================================
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.markdown("<h3 style='text-align: center; color: #FFD700;'>💰 MONEYLINE</h3>", unsafe_allow_html=True)
            with col_t2:
                st.markdown("<h3 style='text-align: center; color: #FFD700;'>📊 SPREAD</h3>", unsafe_allow_html=True)
            with col_t3:
                st.markdown("<h3 style='text-align: center; color: #FFD700;'>🎯 OVER/UNDER</h3>", unsafe_allow_html=True)
            
            # ============================================
            # FILA PRINCIPAL (MONEYLINE CENTRAL + SPREAD/TOTALES)
            # ============================================
            col1, col2, col3 = st.columns([1.2, 1, 1])
            
            # Columna 1: Moneyline (centrado)
            with col1:
                cuota_local = odds.get('moneyline', {}).get('local', 'N/A')
                cuota_visit = odds.get('moneyline', {}).get('visitante', 'N/A')
                
                # Local (arriba)
                color_local = '#4CAF50' if str(cuota_local).startswith('+') else '#FF6B35'
                st.markdown(f"<p style='font-size: 18px; margin-bottom: 0;'>{local}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 42px; font-weight: bold; color: {color_local}; text-align: center; margin-top: -5px;'>{cuota_local}</p>", unsafe_allow_html=True)
                
                # Visitante (abajo)
                color_visit = '#4CAF50' if str(cuota_visit).startswith('+') else '#0066CC'
                st.markdown(f"<p style='font-size: 18px; margin-top: 20px; margin-bottom: 0;'>{visitante}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 42px; font-weight: bold; color: {color_visit}; text-align: center; margin-top: -5px;'>{cuota_visit}</p>", unsafe_allow_html=True)
            
            # Columna 2: Spread
            with col2:
                spread_valor = odds.get('spread', {}).get('valor', 0)
                spread_local_odds = odds.get('spread', {}).get('local_odds', 'N/A')
                spread_visit_odds = odds.get('spread', {}).get('visitante_odds', 'N/A')
                
                st.markdown(f"<p style='font-size: 18px; margin-bottom: 5px;'><span style='color: #FF6B35;'>{local}:</span> {spread_valor:+g}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 24px; font-weight: bold; margin-top: -5px;'>{spread_local_odds}</p>", unsafe_allow_html=True)
                
                st.markdown(f"<p style='font-size: 18px; margin-top: 30px; margin-bottom: 5px;'><span style='color: #0066CC;'>{visitante}:</span> {-spread_valor:+g}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 24px; font-weight: bold; margin-top: -5px;'>{spread_visit_odds}</p>", unsafe_allow_html=True)
            
            # Columna 3: Totales
            with col3:
                total_linea = odds.get('totales', {}).get('linea', 0)
                over_odds = odds.get('totales', {}).get('over_odds', 'N/A')
                under_odds = odds.get('totales', {}).get('under_odds', 'N/A')
                
                st.markdown(f"<p style='font-size: 18px; margin-bottom: 5px;'><span style='color: #4CAF50;'>OVER</span> {total_linea}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 24px; font-weight: bold; margin-top: -5px;'>{over_odds}</p>", unsafe_allow_html=True)
                
                st.markdown(f"<p style='font-size: 18px; margin-top: 30px; margin-bottom: 5px;'><span style='color: #f44336;'>UNDER</span> {total_linea}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 24px; font-weight: bold; margin-top: -5px;'>{under_odds}</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ============================================
            # ANÁLISIS: HEURÍSTICO | PREMIUM | GEMINI
            # ============================================
            col_a1, col_a2, col_a3 = st.columns(3)
            
            # HEURÍSTICO
            with col_a1:
                st.markdown("<h4 style='color: #FFD700;'>📊 HEURÍSTICO</h4>", unsafe_allow_html=True)
                if analisis_heurístico:
                    apuesta = analisis_heurístico.get('apuesta', 'N/A')
                    confianza = analisis_heurístico.get('confianza', 0)
                    st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>{apuesta}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p>Confianza: {confianza}%</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p>Pendiente</p>", unsafe_allow_html=True)
            
            # PREMIUM ANALYTICS
            with col_a2:
                st.markdown("<h4 style='color: #FFD700;'>🔬 PREMIUM ANALYTICS</h4>", unsafe_allow_html=True)
                if analisis_premium:
                    edge = analisis_premium.get('edge_rating', 0)
                    public = analisis_premium.get('public_money', 0)
                    sharps = analisis_premium.get('sharps_action', 'N/A')
                    
                    st.markdown(f"<p><b>Edge Rating:</b> {edge}</p>", unsafe_allow_html=True)
                    estrellas = "★" * int(edge) + "☆" * (10 - int(edge))
                    st.markdown(f"<p>{estrellas}</p>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p><b>Public Money:</b> {public}% {local if public > 50 else visitante}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><b>Sharps Action:</b> {sharps}</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p>Pendiente</p>", unsafe_allow_html=True)
            
            # GEMINI IA
            with col_a3:
                st.markdown("<h4 style='color: #FFD700;'>🤖 GEMINI IA</h4>", unsafe_allow_html=True)
                if analisis_gemini:
                    recomendacion = analisis_gemini.get('recomendacion', 'N/A')
                    confianza = analisis_gemini.get('confianza', 0)
                    st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>{recomendacion}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p>Confianza: {confianza}%</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p>Pendiente</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ============================================
            # BOTONES DE ACCIÓN
            # ============================================
            col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)
            
            with col_b1:
                if st.button(f"🔍 ANALIZAR", key=f"analizar_{idx}"):
                    return "analizar"
            with col_b2:
                if st.button(f"➕ HANDICAP", key=f"h_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"HANDICAP {local} {odds['spread']['valor']:+g}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓")
            with col_b3:
                if st.button(f"➕ OVER", key=f"o_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"OVER {odds['totales']['linea']}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓")
            with col_b4:
                if st.button(f"➕ UNDER", key=f"u_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"UNDER {odds['totales']['linea']}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓")
            with col_b5:
                if st.button(f"➕ ML", key=f"ml_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"GANA {local}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓")
            with col_b6:
                if st.button(f"➕ PROPS", key=f"props_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"PROPS",
                            'cuota': 2.0,
                            'deporte': 'NBA'
                        })
                        st.success("✓")
            
            st.markdown("---")
