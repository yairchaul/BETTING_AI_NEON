import streamlit as st
import pandas as pd
import re
import numpy as np
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate  # <-- NUEVO
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker

st.set_page_config(page_title="Analizador Profesional de Apuestas", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': ProAnalyzerUltimate(),  # <-- CAMBIADO
        'tracker': BettingTracker()
    }

components = init_components()

def parse_raw_betting_text(text):
    """
    Versión mejorada que separa correctamente los equipos
    """
    lines = text.split('\n')
    matches = []
    i = 0
    
    # Lista de palabras que NO son equipos
    non_team_words = ['empate', 'draw', 'vs', '+', '-', 'fc', 'cf', 'sc', 'ac', 'cd', 'ud', 'sd']
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Buscar patrones de cuotas
        odds = re.findall(r'[+-]\d{3,4}', line)
        
        # Si la línea tiene cuotas, intentar extraer
        if odds:
            # Limpiar la línea de cuotas
            clean_line = line
            for odd in odds:
                clean_line = clean_line.replace(odd, '')
            
            # Separar por espacios y filtrar palabras vacías
            parts = [p for p in clean_line.split() if p and p.lower() not in non_team_words]
            
            if len(parts) >= 2:
                # Heurística: los primeros elementos son el local, los últimos el visitante
                mid = len(parts) // 2
                home_parts = parts[:mid]
                away_parts = parts[mid:]
                
                home = ' '.join(home_parts).strip()
                away = ' '.join(away_parts).strip()
                
                # Validar que sean nombres válidos
                if len(home) > 2 and len(away) > 2:
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': odds[:3] if len(odds) >= 3 else ['N/A', 'N/A', 'N/A']
                    })
                    i += 1
                    continue
        
        i += 1
    
    # Si no encontró con el método anterior, usar el original
    if not matches:
        pattern = r"([a-zA-Z\s]+?)([-+]\d+)\s*Empate\s*([-+]\d+)([a-zA-Z\s]+?)([-+]\d+)"
        matches_found = re.findall(pattern, text)
        
        for m in matches_found:
            matches.append({
                'home': m[0].strip(),
                'away': m[3].strip(),
                'all_odds': [m[1], m[2], m[4]]
            })
    
    return matches

def generar_parlay_pro(matches_analizados, max_selecciones=4):
    """
    Genera parlay con las mejores opciones (limitado a max_selecciones)
    """
    if len(matches_analizados) < 2:
        return None
    
    # Ordenar por probabilidad descendente
    selecciones_ordenadas = []
    for match in matches_analizados:
        best = match.get('best_bet', {})
        if best and best.get('probability', 0) > 0.55:  # Umbral mínimo
            selecciones_ordenadas.append({
                'partido': f"{match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}",
                'apuesta': best.get('market', 'Over 1.5 goles'),
                'prob': best.get('probability', 0.7),
                'confianza': best.get('confidence', 'MEDIA'),
                'liga': match.get('liga', 'Desconocida'),
                'razon': best.get('reason', '')
            })
    
    # Ordenar por probabilidad (mayor a menor)
    selecciones_ordenadas.sort(key=lambda x: x['prob'], reverse=True)
    
    # Tomar las mejores N
    selecciones = selecciones_ordenadas[:max_selecciones]
    
    if len(selecciones) >= 2:
        prob_total = np.prod([s['prob'] for s in selecciones])
        
        # Determinar nivel de confianza del parlay
        confianzas = [s['confianza'] for s in selecciones]
        if 'ALTA' in confianzas and len([c for c in confianzas if c == 'ALTA']) >= 2:
            nivel_confianza = 'ALTO'
        elif 'BAJA' in confianzas and len([c for c in confianzas if c == 'BAJA']) >= 2:
            nivel_confianza = 'BAJO'
        else:
            nivel_confianza = 'MEDIO'
        
        return {
            'selecciones': selecciones,
            'probabilidad_total': prob_total,
            'cuota_estimada': round(1 / prob_total * 0.9, 2),
            'nivel_confianza': nivel_confianza
        }
    return None

def main():
    st.title("🎯 Analizador Profesional de Apuestas")
    st.markdown("**Piensa como un apostador profesional** - Analiza cualquier partido del mundo")
    
    # ============================================================================
    # SIDEBAR CONFIGURACIÓN
    # ============================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        prob_minima = st.slider(
            "Probabilidad mínima", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.55, 
            step=0.05,
            help="Solo muestra mercados con probabilidad mayor a este valor"
        )
        
        st.subheader("🎲 Mercados")
        categorias = st.multiselect(
            "Categorías",
            ["1X2", "Totales", "Primer Tiempo", "BTTS", "Combinado"],
            default=["1X2", "Totales", "BTTS"]
        )
        
        # Límite de selecciones para parlay
        max_parlay = st.slider("Máximo selecciones por parlay", 2, 5, 3, 1)
        
        st.divider()
        
        # Estado de APIs
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
        
        debug_mode = st.checkbox("🔧 Modo debug", value=True)
        
        # Mostrar tracker de apuestas
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
            st.image(uploaded_file, use_container_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Procesando imagen..."):
            img_bytes = uploaded_file.getvalue()
            matches = []
            raw_text = ""
            metodo_usado = "Ninguno"
            
            # INTENTO 1: Groq Vision (si está disponible)
            if components['groq_vision']:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    if matches:
                        metodo_usado = "Groq Vision AI"
                        st.success(f"✅ {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    if debug_mode:
                        st.warning(f"Groq Vision falló: {e}")
            
            # INTENTO 2: OCR tradicional + parsing
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                        matches = parse_raw_betting_text(raw_text)
                        metodo_usado = "OCR + Parsing"
                        st.info(f"📝 {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                # Mostrar tabla (primeros 8 para no saturar)
                df_view = []
                for m in matches[:8]:
                    odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    df_view.append({
                        'LOCAL': m.get('home', 'N/A')[:20],
                        'CUOTA L': odds[0],
                        'EMPATE': 'Empate',
                        'CUOTA E': odds[1],
                        'VISITANTE': m.get('away', 'N/A')[:20],
                        'CUOTA V': odds[2]
                    })
                
                if df_view:
                    st.dataframe(pd.DataFrame(df_view), use_container_width=True, hide_index=True)
                    
                    if len(matches) > 8:
                        st.caption(f"... y {len(matches)-8} partidos más")
            
            # Debug info
            if debug_mode and raw_text:
                with st.expander("🔬 Ver texto raw detectado"):
                    st.code(raw_text[:500])
            
            st.divider()
            st.subheader("3. Análisis Profesional (como apostador real)")
            
            matches_analizados = []
            
            # Limitar análisis a primeros 6 partidos para no saturar APIs
            for i, match in enumerate(matches[:6]):
                home = match.get('home', 'Unknown')
                away = match.get('away', 'Unknown')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    st.caption(f"🎲 Cuotas: Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Análisis con ProAnalyzerUltimate
                    with st.spinner("🤔 Analizando..."):
                        analysis = components['analyzer'].analyze_match(home, away, odds)
                    
                    if analysis:
                        # Mostrar liga detectada
                        liga = analysis.get('liga', 'Desconocida')
                        st.info(f"🏆 Liga detectada: **{liga}**")
                        
                        # Mostrar reglas aplicadas (debug)
                        if debug_mode and analysis.get('reglas_aplicadas'):
                            with st.expander("📋 Reglas aplicadas"):
                                for r in analysis['reglas_aplicadas']:
                                    st.caption(f"• {r}")
                        
                        # Mostrar mejor apuesta
                        best = analysis.get('best_bet', {})
                        if best:
                            # Determinar color según confianza
                            conf_color = {
                                'ALTA': '🟢',
                                'MEDIA': '🟡',
                                'BAJA': '🔴'
                            }.get(best.get('confidence', 'MEDIA'), '⚪')
                            
                            with st.container(border=True):
                                st.markdown(f"### {conf_color} RECOMENDACIÓN DEL EXPERTO")
                                st.markdown(f"**{best.get('market', 'Over 1.5 goles')}** - {best.get('probability', 0.7):.1%}")
                                st.markdown(f"📌 *{best.get('reason', 'Análisis basado en contexto de liga')}*")
                                st.caption(f"Confianza: {best.get('confidence', 'MEDIA')}")
                        
                        # Mostrar mercados disponibles (filtrados)
                        markets_filtered = [
                            m for m in analysis.get('markets', []) 
                            if m.get('prob', 0) >= prob_minima and m.get('category', '') in categorias
                        ]
                        
                        if markets_filtered:
                            with st.expander("📊 Todos los mercados analizados"):
                                df_markets = pd.DataFrame([{
                                    'Mercado': m['name'],
                                    'Prob': f"{m['prob']:.1%}",
                                    'Tipo': m['category']
                                } for m in markets_filtered[:10]])
                                st.dataframe(df_markets, use_container_width=True, hide_index=True)
                        
                        matches_analizados.append(analysis)
            
            # ============================================================================
            # PARLAY PROFESIONAL
            # ============================================================================
            if matches_analizados:
                st.divider()
                st.subheader("🎯 Parlay Recomendado por el Experto")
                
                parlay_pro = generar_parlay_pro(matches_analizados, max_parlay)
                
                if parlay_pro:
                    with st.container(border=True):
                        # Métricas principales
                        col_p1, col_p2, col_p3 = st.columns(3)
                        with col_p1:
                            st.metric("Cuota Estimada", parlay_pro['cuota_estimada'])
                        with col_p2:
                            prob_pct = parlay_pro['probabilidad_total'] * 100
                            st.metric("Probabilidad Total", f"{prob_pct:.1f}%")
                        with col_p3:
                            conf_emoji = {
                                'ALTO': '🟢', 
                                'MEDIO': '🟡', 
                                'BAJO': '🔴'
                            }.get(parlay_pro['nivel_confianza'], '⚪')
                            st.metric("Confianza", f"{conf_emoji} {parlay_pro['nivel_confianza']}")
                        
                        # Selecciones
                        st.markdown("**Selecciones del parlay:**")
                        for s in parlay_pro['selecciones']:
                            conf_emoji = '🟢' if s['confianza'] == 'ALTA' else '🟡' if s['confianza'] == 'MEDIA' else '🔴'
                            st.markdown(f"{conf_emoji} **{s['partido']}**: {s['apuesta']} ({s['prob']:.1%})")
                            if s.get('razon'):
                                st.caption(f"   📌 {s['razon']}")
                        
                        # Botón para registrar
                        if st.button("📝 Registrar este parlay", key="register_pro"):
                            components['tracker'].add_bet({
                                'matches': [f"{s['partido']}: {s['apuesta']}" for s in parlay_pro['selecciones']],
                                'total_odds': parlay_pro['cuota_estimada'],
                                'total_prob': parlay_pro['probabilidad_total']
                            }, stake=100)
                            st.success("✅ Parlay registrado! Buena suerte!")
                            st.rerun()
                else:
                    st.info("No hay suficientes partidos con alta probabilidad para formar un parlay")
                    st.caption("Prueba con una probabilidad mínima más baja o más partidos")
        
        else:
            st.error("❌ No se detectaron partidos en la imagen")
            st.info("""
            **Sugerencias:**
            - Asegúrate que la imagen tenga buena resolución
            - Los nombres de equipos deben ser legibles
            - La imagen debe contener el formato: Equipo, Cuota, Empate, Cuota, Equipo, Cuota
            """)
    
    else:
        # Mensaje inicial
        st.info("👆 Sube una imagen para comenzar el análisis profesional")
        
        with st.expander("📋 Formato esperado (ejemplo)"):
            st.code("""
[Equipo Local] [Cuota L] [Empate] [Cuota E] [Equipo Visitante] [Cuota V]

Ejemplo real de Liga Argentina:
Estudiantes de La Plata +132 Empate +174 Velez Sarsfield +280
Deportivo Riestra +174 Empate +152 Platense +235
Independiente Rivadavia +200 Empate +205 River Plate +148
Banfield -103 Empate +210 Aldosivi +335
            """)
        
        with st.expander("ℹ️ Cómo funciona el análisis profesional"):
            st.markdown("""
            ### 🧠 Nuestro sistema piensa como un apostador real:
            
            1. **Detecta la liga** automáticamente (Argentina, Premier, Bundesliga, etc.)
            2. **Conoce el contexto** de cada liga (goles promedio, ventaja local)
            3. **Identifica equipos TOP** (River, PSG, Bayern, etc.)
            4. **Aplica reglas de experto** para TODAS las ligas del mundo:
               - En Argentina → Under 2.5 (pocos goles)
               - En Bundesliga → Over 2.5 (muchos goles)
               - Local TOP vs débil → Gana local
               - Visitante TOP vs débil → Gana visitante
               - Y muchas más...
            5. **Recomienda la mejor apuesta** con explicación
            
            ### 🌍 Cobertura global:
            - ✅ 100+ ligas de todo el mundo
            - ✅ Sudamérica: Argentina, Brasil, Chile, Colombia, etc.
            - ✅ Europa: Premier, LaLiga, Bundesliga, Serie A, etc.
            - ✅ Asia: Japón, Corea, China, Arabia, etc.
            - ✅ África: Egipto, Sudáfrica
            - ✅ Concacaf: México, MLS, Costa Rica, etc.
            """)

if __name__ == "__main__":
    main()
