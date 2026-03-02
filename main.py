import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.analyzer import MatchAnalyzer
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker
from modules.team_matcher import TeamMatcher
from modules.montecarlo import run_simulation

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache para mejorar rendimiento"""
    return {
        'vision': ImageParser(),
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", "")),
        'tracker': BettingTracker(),
        'matcher': TeamMatcher(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

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
        
        if st.secrets.get("FOOTBALL_API_KEY"):
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ Modo simulación")
        
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
        # ============================================================================
        # DIAGNÓSTICO: VER MÉTODOS DISPONIBLES EN ImageParser
        # ============================================================================
        if debug_mode:
            with st.expander("🔧 DIAGNÓSTICO - Métodos de ImageParser", expanded=False):
                st.write("**Inspeccionando objeto vision_reader.ImageParser...**")
                
                # Listar todos los métodos y atributos
                all_attrs = dir(components['vision'])
                methods = [attr for attr in all_attrs if not attr.startswith('_')]
                st.write("**Métodos públicos disponibles:**")
                st.write(methods)
                
                # Verificar específicamente process_image
                if hasattr(components['vision'], 'process_image'):
                    st.success("✅ El método 'process_image' SÍ existe")
                else:
                    st.error("❌ El método 'process_image' NO existe")
                    
                    # Buscar métodos similares
                    similar = [m for m in methods if 'image' in m.lower() or 'process' in m.lower() or 'parse' in m.lower()]
                    if similar:
                        st.write("**Métodos similares encontrados:**")
                        st.write(similar)
        
        # ============================================================================
        # NUEVA LÓGICA DE PROCESAMIENTO COMPATIBLE (CON TU CÓDIGO)
        # ============================================================================
        with st.spinner("🔍 Procesando imagen con Google Vision..."):
            # Usamos .getvalue() en lugar de .read() para evitar que el archivo se "vacíe"
            img_bytes = uploaded_file.getvalue()
            
            # Variable para almacenar resultados
            matches = []
            method_used = None
            raw_text = ""
            
            # INTENTO 1: Llamar directamente al método process_image (tu código original)
            try:
                if hasattr(components['vision'], 'process_image'):
                    matches = components['vision'].process_image(img_bytes)
                    method_used = 'process_image (directo)'
                    st.success(f"✅ Usando método: {method_used}")
            except Exception as e:
                if debug_mode:
                    st.warning(f"⚠️ process_image falló: {e}")
            
            # INTENTO 2: Si el primero falló, probar con otros métodos comunes
            if not matches:
                possible_methods = ['parse_image', 'analyze_image', 'detect_matches', 'extract_matches', 'smart_parse']
                
                for method_name in possible_methods:
                    if hasattr(components['vision'], method_name):
                        try:
                            method = getattr(components['vision'], method_name)
                            
                            # Algunos métodos esperan bytes, otros texto
                            if method_name == 'smart_parse':
                                # Primero obtener texto
                                from google.cloud import vision
                                image = vision.Image(content=img_bytes)
                                response = components['vision'].client.text_detection(image=image)
                                if response.text_annotations:
                                    text = response.text_annotations[0].description
                                    result = method(text)
                                else:
                                    result = []
                            else:
                                # La mayoría espera bytes
                                result = method(img_bytes)
                            
                            if result:
                                matches = result
                                method_used = method_name
                                st.success(f"✅ Método alternativo funcionando: {method_name}")
                                break
                        except Exception as e:
                            if debug_mode:
                                st.warning(f"❌ Método {method_name} falló: {e}")
                            continue
            
            # INTENTO 3: Acceso directo al cliente de Vision
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        text = response.text_annotations[0].description
                        
                        # Usar smart_parse si existe
                        if hasattr(components['vision'], 'smart_parse'):
                            matches = components['vision'].smart_parse(text)
                            method_used = 'smart_parse (vía cliente directo)'
                        else:
                            # Fallback básico: asumir que los equipos están en líneas alternadas
                            lines = text.split('\n')
                            clean_lines = [l.strip() for l in lines if len(l.strip()) > 3]
                            matches = []
                            for i in range(0, len(clean_lines)-1, 2):
                                if i+1 < len(clean_lines):
                                    matches.append({
                                        'home': clean_lines[i],
                                        'away': clean_lines[i+1]
                                    })
                            method_used = 'fallback básico (líneas alternadas)'
                except Exception as e:
                    if debug_mode:
                        st.error(f"Error en acceso directo: {e}")
            
            # Obtener texto raw para debug (siempre intentar)
            try:
                from google.cloud import vision
                image = vision.Image(content=img_bytes)
                response = components['vision'].client.text_detection(image=image)
                if response.text_annotations:
                    raw_text = response.text_annotations[0].description
                    
                    # Detección de partido en vivo
                    if re.search(r"\d{1,2}['′]", raw_text) or re.search(r"\d+\s*-\s*\d+", raw_text):
                        st.info("🏟️ **Partido en tiempo real detectado** - Analizando con condiciones actuales")
            except Exception as e:
                if debug_mode:
                    st.warning(f"Nota: No se pudo obtener texto raw: {e}")
        
        # ============================================================================
        # MOSTRAR DEBUG
        # ============================================================================
        if debug_mode:
            with st.expander("🔧 Debug OCR - Información de detección", expanded=True):
                st.write(f"**Método utilizado:** {method_used or 'Ninguno'}")
                st.write(f"**Partidos detectados:** {len(matches)}")
                
                if matches:
                    st.write("**Detalle de detecciones:**")
                    for i, m in enumerate(matches):
                        home = m.get('home', m.get('local', 'N/A'))
                        away = m.get('away', m.get('visitante', 'N/A'))
                        odds = m.get('all_odds', m.get('odds', ['N/A']))
                        st.write(f"{i+1}. {home} vs {away} → Odds: {odds}")
                
                if raw_text:
                    st.write("**Texto raw detectado (primeros 500 caracteres):**")
                    st.text(raw_text[:500])
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df_data = []
                for m in matches:
                    home = m.get('home', m.get('local', 'N/A'))
                    away = m.get('away', m.get('visitante', 'N/A'))
                    odds = m.get('all_odds', m.get('odds', ['N/A', 'N/A', 'N/A']))
                    df_data.append({
                        'Local': home,
                        'Visitante': away,
                        'Cuota L': odds[0] if len(odds) > 0 else 'N/A',
                        'Cuota E': odds[1] if len(odds) > 1 else 'N/A',
                        'Cuota V': odds[2] if len(odds) > 2 else 'N/A'
                    })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
            
            st.divider()
            st.subheader("3. Análisis partido por partido")
            
            all_picks = []
            for i, match in enumerate(matches):
                home = match.get('home', match.get('local', ''))
                away = match.get('away', match.get('visitante', ''))
                odds = match.get('all_odds', match.get('odds', ['N/A', 'N/A', 'N/A']))
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    # Mostrar cuotas si están disponibles
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
                    
                    # Resaltar mercados especiales
                    if show_high_scoring:
                        for m in markets_filtered:
                            if 'Over 4.5' in m['name'] or 'Over 5.5' in m['name']:
                                m['highlight'] = True
                    
                    if markets_filtered:
                        st.caption(f"📊 Goles promedio esperados: {analysis['probabilidades']['goles_promedio']:.2f}")
                        
                        market_df = pd.DataFrame([{
                            'Mercado': ("🔴 " if m.get('highlight') else "") + m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:10]])
                        
                        st.dataframe(market_df, use_container_width=True, hide_index=True)
                        
                        best = markets_filtered[0]
                        best_emoji = "🔴" if best.get('highlight') else "✨"
                        st.success(f"{best_emoji} **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        all_picks.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                    else:
                        st.info("📭 No hay mercados con los filtros seleccionados")
            
            if all_picks:
                show_parlay_options(all_picks, components['tracker'])
            else:
                st.info("ℹ️ No hay suficientes picks para generar parlays")
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
            """)
        
        with st.expander("ℹ️ Cómo funciona"):
            st.markdown("""
            ### 🎯 Flujo de análisis:
            
            1. **Subes una captura** de cualquier casa de apuestas
            2. **Google Vision OCR** detecta palabras con coordenadas
            3. **Algoritmo inteligente** busca patrón: EQUIPO + 3 ODDS + EQUIPO
            4. **Buscamos los equipos** en API-Sports
            5. **Simulación Monte Carlo** (20,000 iteraciones)
            6. **Analizamos 20+ mercados** por partido
            7. **Generamos parlays** con valor esperado positivo
            8. **Registramos apuestas** y tracking de resultados
            """)

if __name__ == "__main__":
    main()
