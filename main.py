import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.analyzer import MatchAnalyzer
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker
from modules.team_matcher import TeamMatcher
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache para mejorar rendimiento"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", "")),
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
            default=["1X2", "Totales", "Primer Tiempo", "BTTS"],
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
                st.success("⚽ API")
            else:
                st.warning("⚽ No API")
        
        with col_api2:
            if st.secrets.get("GROQ_API_KEY"):
                st.success("🤖 Groq")
            else:
                st.warning("🤖 No Groq")
        
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
            metodo_usado = "OCR Tradicional"
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
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
            
            # ============================================================================
            # INTENTO 3: Fallback al método tradicional del vision_reader
            # ============================================================================
            if not matches:
                matches = components['vision'].process_image(img_bytes)
                metodo_usado = "Vision Reader Tradicional"

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
            # ANÁLISIS POR PARTIDO Y EV ENGINE
            # ============================================================================
            st.divider()
            st.subheader("3. Análisis de IA y Valor Esperado")
            
            all_picks_for_ev = []
            all_picks_simple = []
            
            for i, match in enumerate(matches):
                home = match.get('home', match.get('local', ''))
                away = match.get('away', match.get('visitante', ''))
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    # Mostrar cuotas
                    if odds and odds[0] != 'N/A':
                        st.caption(f"🎲 **Cuotas:** Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Analizar el partido
                    analysis = components['analyzer'].analyze_match(home, away, "")
                    
                    # Mostrar resultados de búsqueda
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ Local encontrado: {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ Local: {home} (no encontrado en API)")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ Visitante encontrado: {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ Visitante: {away} (no encontrado en API)")
                    
                    # Filtrar mercados
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    if markets_filtered:
                        # Mostrar estadísticas generales
                        st.caption(f"📊 Goles promedio esperados: {analysis['probabilidades']['goles_promedio']:.2f}")
                        
                        # Crear DataFrame para mostrar mercados
                        market_df = pd.DataFrame([{
                            'Mercado': m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:8]])
                        
                        st.dataframe(market_df, use_container_width=True, hide_index=True)
                        
                        # Guardar para parlays simples
                        best = markets_filtered[0]
                        st.success(f"✨ **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        all_picks_simple.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                        
                        # Preparar picks para EV Engine
                        for m in markets_filtered[:3]:
                            # Lógica simple de conversión de cuota para EV
                            try:
                                if 'Local' in m['name'] and odds[0] != 'N/A':
                                    o_val = int(odds[0])
                                    decimal_odd = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                elif 'Visitante' in m['name'] and odds[2] != 'N/A':
                                    o_val = int(odds[2])
                                    decimal_odd = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                else:
                                    decimal_odd = 2.0
                                
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
                            except:
                                pass
            
            # ============================================================================
            # GENERACIÓN DE PARLAYS
            # ============================================================================
            st.divider()
            
            col_parlay1, col_parlay2 = st.columns(2)
            
            with col_parlay1:
                st.subheader("🎯 Parlays Simples")
                if all_picks_simple:
                    from modules.parlay_builder import show_parlay_options as show_simple_parlays
                    show_simple_parlays(all_picks_simple, components['tracker'])
                else:
                    st.info("ℹ️ No hay suficientes picks para generar parlays simples")
            
            with col_parlay2:
                st.subheader("📈 Parlay Inteligente (EV+)")
                if all_picks_for_ev:
                    smart = build_smart_parlay(all_picks_for_ev)
                    if smart:
                        with st.container(border=True):
                            st.markdown(f"**Cuota Total:** {smart['total_odd']} | **EV:** {smart['total_ev']:.2%}")
                            st.markdown(f"**Probabilidad Combinada:** {smart['combined_prob']:.1%}")
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

if __name__ == "__main__":
    main()
