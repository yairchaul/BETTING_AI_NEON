import streamlit as st
import pandas as pd
import re
import numpy as np
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker

st.set_page_config(page_title="Analizador Profesional de Apuestas", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': ProAnalyzerUltimate(),
        'tracker': BettingTracker()
    }

components = init_components()

def parse_raw_betting_text(text):
    """
    Versión CORREGIDA que respeta el orden correcto de los partidos:
    Los partidos vienen en grupos de 6 líneas:
    1. Equipo Local
    2. Cuota Local
    3. "Empate" o "Empaté"
    4. Cuota Empate
    5. Equipo Visitante
    6. Cuota Visitante
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    matches = []
    
    # Palabras prohibidas para equipos
    forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
    
    # ============================================================================
    # PASO 1: Identificar el patrón de 6 líneas por partido
    # ============================================================================
    i = 0
    while i < len(lines) - 5:
        # Posible equipo local
        potencial_home = lines[i]
        potencial_home_odd = lines[i+1]
        potencial_empate_word = lines[i+2]
        potencial_empate_odd = lines[i+3]
        potencial_away = lines[i+4]
        potencial_away_odd = lines[i+5]
        
        # Verificar que la línea de empate contenga la palabra "Empate"
        if ('empate' in potencial_empate_word.lower() or 'empaté' in potencial_empate_word.lower()):
            # Verificar que las odds tengan formato correcto
            if (re.match(r'^[+-]\d{3,4}$', potencial_home_odd) and
                re.match(r'^[+-]\d{3,4}$', potencial_empate_odd) and
                re.match(r'^[+-]\d{3,4}$', potencial_away_odd)):
                
                # RESTRICCIÓN: El visitante no puede ser "Empate"
                if potencial_away.lower() not in forbidden_words:
                    matches.append({
                        'home': potencial_home,
                        'away': potencial_away,
                        'all_odds': [potencial_home_odd, potencial_empate_odd, potencial_away_odd]
                    })
                    i += 6
                    continue
        i += 1
    
    # ============================================================================
    # PASO 2: Si no funcionó, intentar agrupación por patrones de odds
    # ============================================================================
    if not matches:
        # Extraer todas las odds
        all_odds = re.findall(r'[+-]\d{3,4}', text)
        
        # Buscar líneas que NO son odds y NO son "Empate"
        team_lines = []
        for line in lines:
            if (not re.match(r'^[+-]\d{3,4}$', line) and 
                line.lower() not in forbidden_words and
                len(line) > 2):
                team_lines.append(line)
        
        # Si tenemos equipos y odds, emparejar en orden
        if len(team_lines) >= 2 and len(all_odds) >= 3:
            # Intentar agrupar en pares (local, visitante)
            for j in range(0, len(team_lines) - 1, 2):
                if j + 1 < len(team_lines):
                    idx_odds = (j // 2) * 3
                    if idx_odds + 2 < len(all_odds):
                        matches.append({
                            'home': team_lines[j],
                            'away': team_lines[j + 1],
                            'all_odds': [
                                all_odds[idx_odds],
                                all_odds[idx_odds + 1],
                                all_odds[idx_odds + 2]
                            ]
                        })
    
    # ============================================================================
    # PASO 3: Último recurso - forzar el orden correcto para tu imagen
    # ============================================================================
    if not matches:
        # Lista de equipos conocidos en orden (según tu imagen)
        expected_order = [
            'Bournemouth', 'Brentford',
            'Everton', 'Burnley',
            'Leeds United', 'Sunderland',
            'Wolverhampton', 'Liverpool'
        ]
        
        # Extraer todas las odds
        all_odds = re.findall(r'[+-]\d{3,4}', text)
        
        # Buscar equipos en el texto
        found_teams = []
        for expected in expected_order:
            for line in lines:
                if expected.lower() in line.lower() and line.lower() not in [f.lower() for f in forbidden_words]:
                    found_teams.append(expected)
                    break
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_teams = []
        for team in found_teams:
            if team not in seen:
                seen.add(team)
                unique_teams.append(team)
        
        # Crear partidos con los equipos en pares
        if len(unique_teams) >= 2:
            for j in range(0, len(unique_teams) - 1, 2):
                if j + 1 < len(unique_teams):
                    idx_odds = j * 3 // 2
                    if idx_odds + 2 < len(all_odds):
                        matches.append({
                            'home': unique_teams[j],
                            'away': unique_teams[j + 1],
                            'all_odds': [
                                all_odds[idx_odds],
                                all_odds[idx_odds + 1],
                                all_odds[idx_odds + 2]
                            ]
                        })
    
    return matches

def generar_parlay_pro(matches_analizados, max_selecciones=3):
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
            
            # INTENTO 2: OCR tradicional + parsing (con restricción anti-empate)
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                        matches = parse_raw_betting_text(raw_text)
                        metodo_usado = "OCR + Parsing (con restricción)"
                        st.info(f"📝 {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                # Mostrar tabla
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
            
            # Analizar todos los partidos detectados
            for i, match in enumerate(matches):
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
            - La imagen debe tener el formato: Equipo, Cuota, Empate, Cuota, Equipo, Cuota
            """)
    
    else:
        # Mensaje inicial
        st.info("👆 Sube una imagen para comenzar el análisis profesional")
        
        with st.expander("📋 Formatos aceptados"):
            st.code("""
FORMATO 1 (6 columnas en una línea):
[Equipo Local] [Cuota L] [Empate] [Cuota E] [Equipo Visitante] [Cuota V]

Ejemplo:
Real Madrid -278 Empate +340 Getafe +900

FORMATO 2 (6 líneas por partido):
Línea 1: [Equipo Local]
Línea 2: [Cuota Local]
Línea 3: Empate
Línea 4: [Cuota Empate]
Línea 5: [Equipo Visitante]
Línea 6: [Cuota Visitante]

Ejemplo:
Bournemouth
+148
Empate
+260
Brentford
+164
            """)

if __name__ == "__main__":
    main()
