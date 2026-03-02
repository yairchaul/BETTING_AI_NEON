import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker
from modules.team_matcher import TeamMatcher
from modules.ev_engine import build_smart_parlay
from modules.real_analyzer import RealAnalyzer

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache para mejorar rendimiento"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': RealAnalyzer(),
        'tracker': BettingTracker(),
        'matcher': TeamMatcher(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

def parse_raw_betting_text(text):
    """
    Separa el texto raw pegado usando expresiones regulares avanzadas.
    Efectivo para casos como: 'Real Madrid-278 Empate+340Getafe+900'
    """
    # Regex optimizada:
    # ([a-zA-Z\s]+?) -> Nombre Local (non-greedy para no comerse números)
    # ([-+]\d+)      -> Cuota Local
    # \s*Empate\s*   -> Palabra clave Empate
    # ([-+]\d+)      -> Cuota Empate
    # ([a-zA-Z\s]+?) -> Nombre Visitante
    # ([-+]\d+)      -> Cuota Visitante
    pattern = r"([a-zA-Z\s]+?)([-+]\d+)\s*Empate\s*([-+]\d+)([a-zA-Z\s]+?)([-+]\d+)"
    
    matches_found = re.findall(pattern, text)
    
    clean_list = []
    for m in matches_found:
        clean_list.append({
            'home': m[0].strip(),
            'away': m[3].strip(),
            'all_odds': [m[1], m[2], m[4]]
        })
    return clean_list

def main():
    st.title("🎯 Analizador Universal de Partidos")
    st.markdown("Sube una captura y analizo **partido por partido**")
    
    # ============================================================================
    # SIDEBAR CON CONFIGURACIÓN AVANZADA
    # ============================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        prob_minima = st.slider(
            "Probabilidad mínima", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.5, 
            step=0.05,
            help="Solo muestra mercados con probabilidad mayor a este valor"
        )
        
        st.divider()
        
        st.subheader("🎲 Mercados a mostrar")
        categorias = st.multiselect(
            "Selecciona categorías",
            ["1X2", "Doble Oportunidad", "Totales", "Primer Tiempo", 
             "BTTS", "Handicap", "Goleador", "Combinado", "Totales (Especial)"],
            default=["1X2", "Totales", "Primer Tiempo", "BTTS", "Totales (Especial)"],
            help="Selecciona qué tipos de mercados quieres ver"
        )
        
        show_high_scoring = st.checkbox(
            "⚽ Enfatizar equipos goleadores", 
            value=True,
            help="Resalta mercados de Over 4.5 y Over 5.5 goles"
        )
        
        st.divider()
        
        # Configuración de EV Engine
        st.subheader("📈 Valor Esperado (EV)")
        ev_minimo = st.number_input(
            "EV mínimo para considerar",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
            step=0.01,
            format="%.2f",
            help="Solo picks con EV > este valor serán considerados"
        )
        
        max_picks_parlay = st.slider(
            "Máximo picks por parlay",
            min_value=2,
            max_value=6,
            value=5,
            help="Número máximo de selecciones en un parlay"
        )
        
        st.divider()
        
        # Estado de las APIs
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            if st.secrets.get("FOOTBALL_API_KEY"):
                st.success("⚽ API Football")
            else:
                st.warning("⚽ No API Football")
        
        with col_api2:
            if st.secrets.get("GROQ_API_KEY"):
                st.success("🤖 Groq AI")
            else:
                st.warning("🤖 No Groq")
        
        # Mostrar estado de otras APIs
        if st.secrets.get("GOOGLE_API_KEY") and st.secrets.get("GOOGLE_CSE_ID"):
            st.success("🔍 Google CSE")
        else:
            st.warning("🔍 No Google CSE")
            
        if st.secrets.get("ODDS_API_KEY"):
            st.success("📊 Odds API")
        else:
            st.warning("📊 No Odds API")
        
        debug_mode = st.checkbox("🔧 Mostrar debug OCR", value=True)
        components['tracker'].show_tracker_ui()
    
    # ============================================================================
    # ÁREA PRINCIPAL
    # ============================================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader(
            "Selecciona imagen", 
            type=['png', 'jpg', 'jpeg'],
            help="Sube una captura de pantalla con partidos y cuotas"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Extrayendo datos y limpiando texto..."):
            img_bytes = uploaded_file.getvalue()
            matches = []
            metodo_usado = "Ninguno"
            raw_text = ""
            
            # ============================================================================
            # INTENTO 1: Usar Groq Vision (si está disponible)
            # ============================================================================
            if components['groq_vision']:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    metodo_usado = "Groq Vision AI"
                    st.success(f"✅ Usando {metodo_usado}")
                except Exception as e:
                    st.warning(f"⚠️ Groq falló: {e}")
            
            # ============================================================================
            # INTENTO 2: Usar tu función parse_raw_betting_text (si Groq falló o no está)
            # ============================================================================
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                        matches = parse_raw_betting_text(raw_text)
                        metodo_usado = "Parseo Regex (tu función)"
                        st.info(f"📝 Usando {metodo_usado}")
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
            
            # ============================================================================
            # INTENTO 3: Fallback al método tradicional del vision_reader
            # ============================================================================
            if not matches:
                matches = components['vision'].process_image(img_bytes)
                metodo_usado = "Vision Reader Tradicional"
                st.info(f"🔄 Usando {metodo_usado}")

        # ============================================================================
        # TABLA DE 6 COLUMNAS (ESTILO IMAGEN REQUERIDA)
        # ============================================================================
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                # Construcción del DataFrame para visualización limpia
                df_view = []
                for m in matches:
                    odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    df_view.append({
                        'LOCAL': m.get('home', m.get('local', 'N/A')),
                        'CUOTA L': odds[0],
                        'EMPATE': 'Empate',
                        'CUOTA E': odds[1],
                        'VISITANTE': m.get('away', m.get('visitante', 'N/A')),
                        'CUOTA V': odds[2]
                    })
                
                # Mostramos la tabla formateada (6 columnas)
                st.dataframe(pd.DataFrame(df_view), use_container_width=True, hide_index=True)

            # ============================================================================
            # DEBUG: Mostrar información de detección
            # ============================================================================
            if debug_mode:
                with st.expander("🔧 Debug OCR - Información de detección", expanded=True):
                    st.write(f"**Método utilizado:** {metodo_usado}")
                    st.write(f"**Partidos detectados:** {len(matches)}")
                    
                    if matches:
                        st.write("**Detalle de detecciones:**")
                        
                        # Crear tabla HTML para mejor visualización
                        html_matches = "<table style='width:100%; border-collapse: collapse;'>"
                        html_matches += "<tr style='background-color: #2196F3; color: white;'>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>#</th>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>Local</th>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>Cuota L</th>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>Empate</th>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>Cuota E</th>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>Visitante</th>"
                        html_matches += "<th style='padding: 8px; border: 1px solid #ddd;'>Cuota V</th>"
                        html_matches += "</tr>"
                        
                        for i, m in enumerate(matches):
                            odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                            home = m.get('home', m.get('local', 'N/A'))
                            away = m.get('away', m.get('visitante', 'N/A'))
                            
                            html_matches += "<tr>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>{i+1}</td>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>{home}</td>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>{odds[0]}</td>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>Empate</td>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>{odds[1]}</td>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>{away}</td>"
                            html_matches += f"<td style='padding: 8px; border: 1px solid #ddd;'>{odds[2]}</td>"
                            html_matches += "</tr>"
                        
                        html_matches += "</table>"
                        st.markdown(html_matches, unsafe_allow_html=True)
                    
                    if raw_text:
                        st.write("**Texto raw detectado (primeros 500 caracteres):**")
                        st.code(raw_text[:500])

            # ============================================================================
            # ANÁLISIS POR PARTIDO CON REAL ANALYZER (basado en últimos 5 partidos)
            # ============================================================================
            st.divider()
            st.subheader("3. Análisis basado en últimos 5 partidos (IA + Estadísticas)")
            
            all_picks_for_ev = []
            all_picks_simple = []
            
            for i, match in enumerate(matches):
                home = match.get('home', match.get('local', ''))
                away = match.get('away', match.get('visitante', ''))
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    # Mostrar cuotas
                    if odds and odds[0] != 'N/A':
                        st.caption(f"🎲 **Cuotas reales de la imagen:** Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Analizar el partido con REAL ANALYZER (basado en últimos 5 partidos)
                    analysis = components['analyzer'].analyze_match(home, away)
                    
                    # Mostrar resultados de búsqueda de equipos
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ {analysis['home_team']} encontrado en API - Analizando últimos 5 partidos")
                            if 'stats' in analysis:
                                st.caption(f"   ⚽ Promedio goles: {analysis['stats']['home_goals_for']:.2f} GF | {analysis['stats']['home_goals_against']:.2f} GC")
                        else:
                            st.warning(f"⚠️ {home} (no encontrado en API - usando estadísticas genéricas)")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ {analysis['away_team']} encontrado en API - Analizando últimos 5 partidos")
                            if 'stats' in analysis:
                                st.caption(f"   ⚽ Promedio goles: {analysis['stats']['away_goals_for']:.2f} GF | {analysis['stats']['away_goals_against']:.2f} GC")
                        else:
                            st.warning(f"⚠️ {away} (no encontrado en API - usando estadísticas genéricas)")
                    
                    # Mostrar estadísticas generales
                    st.caption(f"📊 Goles promedio esperados: {analysis['probabilidades']['goles_promedio']:.2f}")
                    
                    # Filtrar mercados por categoría y probabilidad mínima
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    # Resaltar mercados especiales (Over 4.5+)
                    if show_high_scoring:
                        for m in markets_filtered:
                            if 'Over 4.5' in m['name'] or 'Over 5.5' in m['name']:
                                m['highlight'] = True
                    
                    if markets_filtered:
                        # Crear DataFrame para mostrar mercados
                        market_df = pd.DataFrame([{
                            'Mercado': ("🔴 " if m.get('highlight') else "") + m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:10]])
                        
                        st.dataframe(market_df, use_container_width=True, hide_index=True)
                        
                        # Mejor opción
                        best = markets_filtered[0]
                        best_emoji = "🔴" if best.get('highlight') else "✨"
                        st.success(f"{best_emoji} **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        # Guardar para parlays simples
                        all_picks_simple.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                        
                        # Preparar picks para EV Engine (usando cuotas reales de la imagen)
                        for m in markets_filtered[:3]:
                            try:
                                # Determinar qué odds usar según el mercado
                                if 'Local' in m['name'] and odds[0] != 'N/A':
                                    o_val = int(odds[0])
                                    decimal_odd = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                elif 'Visitante' in m['name'] and odds[2] != 'N/A':
                                    o_val = int(odds[2])
                                    decimal_odd = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                elif 'Empate' in m['name'] and odds[1] != 'N/A':
                                    o_val = int(odds[1])
                                    decimal_odd = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                else:
                                    # Si no hay odds específicas, usar probabilidad inversa
                                    decimal_odd = (1 / m['prob']) * 0.95
                                
                                ev = (m['prob'] * decimal_odd) - 1
                                
                                if ev > ev_minimo:
                                    all_picks_for_ev.append({
                                        'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                                        'selection': m['name'],
                                        'probability': m['prob'],
                                        'odd': decimal_odd,
                                        'ev': ev,
                                        'category': m['category']
                                    })
                            except Exception as e:
                                if debug_mode:
                                    st.caption(f"Nota: No se pudo calcular EV para {m['name']}")
                    
                    else:
                        st.info("📭 No hay mercados con los filtros seleccionados")
            
            # ============================================================================
            # GENERACIÓN DE PARLAYS
            # ============================================================================
            st.divider()
            
            col_parlay1, col_parlay2 = st.columns(2)
            
            with col_parlay1:
                st.subheader("🎯 Parlays Simples (Mejores opciones)")
                if all_picks_simple:
                    from modules.parlay_builder import show_parlay_options as show_simple_parlays
                    show_simple_parlays(all_picks_simple, components['tracker'])
                else:
                    st.info("ℹ️ No hay suficientes picks para generar parlays simples")
            
            with col_parlay2:
                st.subheader("📈 Parlay Inteligente (Basado en EV+)")
                if all_picks_for_ev:
                    smart = build_smart_parlay(all_picks_for_ev)
                    if smart:
                        with st.container(border=True):
                            st.markdown(f"**Cuota Total:** {smart['total_odd']}")
                            st.markdown(f"**Probabilidad Combinada:** {smart['combined_prob']:.1%}")
                            st.markdown(f"**Valor Esperado (EV):** {smart['total_ev']:.2%}")
                            
                            # Color según EV
                            if smart['total_ev'] > 0.2:
                                st.markdown("🟢 **EV Alto - Muy Recomendado**")
                            elif smart['total_ev'] > 0.1:
                                st.markdown("🟡 **EV Moderado - Recomendado**")
                            elif smart['total_ev'] > 0.05:
                                st.markdown("🟠 **EV Bajo - Considerar riesgo**")
                            else:
                                st.markdown("🔴 **EV Negativo - No recomendado**")
                            
                            st.markdown("**Selecciones:**")
                            for m in smart['matches']:
                                st.markdown(f"• {m}")
                            
                            if st.button("📝 Registrar este parlay", key="register_smart"):
                                components['tracker'].add_bet({
                                    'matches': smart['matches'],
                                    'total_odds': smart['total_odd'],
                                    'total_prob': smart['combined_prob']
                                }, stake=100)
                                st.success("✅ Parlay registrado!")
                                st.rerun()
                    else:
                        st.info("📭 No se encontraron parlays con EV positivo")
                        
                        # Mostrar top picks con mejor EV
                        if all_picks_for_ev:
                            st.caption("**Top picks individuales con mejor EV:**")
                            top_ev_picks = sorted(all_picks_for_ev, key=lambda x: x['ev'], reverse=True)[:5]
                            for p in top_ev_picks:
                                ev_color = "🟢" if p['ev'] > 0.1 else "🟡" if p['ev'] > 0.05 else "🟠"
                                st.markdown(f"{ev_color} {p['match']}: {p['selection']} (EV: {p['ev']:.2%})")
                else:
                    st.info("ℹ️ No hay picks con EV suficiente")
        
        else:
            st.error("❌ No se detectaron partidos en la imagen")
            st.info("""
            **Sugerencias para mejorar la detección:**
            - Asegúrate que la imagen tenga buena resolución
            - Los nombres de equipos deben ser legibles
            - La imagen debe contener cuotas en formato americano (+120, -150)
            - Activa el debug para ver qué texto detectó el OCR
            """)
    
    else:
        st.info("👆 Sube una imagen para comenzar el análisis")
        
        with st.expander("📋 Formato esperado (ejemplo)"):
            st.code("""
[Equipo Local] [Cuota Local] [Empate] [Cuota Empate] [Equipo Visitante] [Cuota Visitante]

Ejemplos:
Real Madrid -278 Empate +340 Getafe +900
Rayo Vallecano -145 Empate +265 Real Oviedo +410
Celta de Vigo +330 Empate +290 Real Madrid -132
Osasuna -132 Empate +245 RCD Mallorca +390
Levante +178 Empate +235 Girona +150
            """)
        
        with st.expander("ℹ️ Cómo funciona"):
            st.markdown("""
            ### 🎯 Flujo de análisis:
            
            1. **Subes una captura** de cualquier casa de apuestas
            2. **Google Vision OCR** o **Groq Vision AI** detectan los datos
            3. **Extraemos equipos y cuotas** en formato de 6 columnas
            4. **Buscamos cada equipo** en múltiples APIs (Football API, Google CSE, Odds API)
            5. **Obtenemos últimos 5 partidos** de cada equipo
            6. **Calculamos estadísticas reales**: promedios de goles, BTTS, overs
            7. **Generamos 20+ mercados** basados en datos reales
            8. **Seleccionamos la mejor opción** para cada partido
            9. **Creamos parlays optimizados** con Valor Esperado (EV) positivo
            10. **Registramos apuestas** y tracking de resultados
            
            ### 📊 Mercados analizados:
            - ✅ Resultado Final (1X2)
            - ✅ Ambos Equipos Anotan (BTTS)
            - ✅ Over/Under 1.5, 2.5, 3.5, 4.5, 5.5
            - ✅ 1ra Mitad (goles y BTTS)
            - ✅ Combinados (Local + Over, Visitante + Over, BTTS + Over)
            - ✅ Handicaps y goleadas
            
            ### 🔍 Motores de búsqueda utilizados:
            - **Football API Sports** → Base de datos principal
            - **Google Custom Search** → Búsqueda de IDs cuando falla la API
            - **Odds API** → Información adicional de partidos
            - **Groq Vision AI** → Interpretación inteligente de imágenes
            """)

if __name__ == "__main__":
    main()
