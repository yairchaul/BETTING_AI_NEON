import streamlit as st
import pandas as pd
import re
import numpy as np
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.odds_integrator import OddsIntegrator
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
        'odds': OddsIntegrator(),
        'tracker': BettingTracker()
    }

components = init_components()

def parse_raw_betting_text(text):
    """
    Versión para formato de 6 líneas por partido:
    Línea 1: Equipo Local
    Línea 2: Cuota Local
    Línea 3: "Empate" (o variante)
    Línea 4: Cuota Empate
    Línea 5: Equipo Visitante
    Línea 6: Cuota Visitante
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    matches = []
    
    forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
    
    # Formato de 6 líneas
    i = 0
    while i < len(lines) - 5:
        potencial_home = lines[i]
        potencial_home_odd = lines[i+1]
        potencial_empate_word = lines[i+2]
        potencial_empate_odd = lines[i+3]
        potencial_away = lines[i+4]
        potencial_away_odd = lines[i+5]
        
        if ('empate' in potencial_empate_word.lower() or 'empaté' in potencial_empate_word.lower()):
            if (re.match(r'^[+-]\d{3,4}$', potencial_home_odd) and
                re.match(r'^[+-]\d{3,4}$', potencial_empate_odd) and
                re.match(r'^[+-]\d{3,4}$', potencial_away_odd)):
                
                if (potencial_home.lower() not in forbidden_words and 
                    potencial_away.lower() not in forbidden_words):
                    matches.append({
                        'home': potencial_home,
                        'away': potencial_away,
                        'all_odds': [potencial_home_odd, potencial_empate_odd, potencial_away_odd]
                    })
                    i += 6
                    continue
        i += 1
    
    return matches

def parse_complex_betting_text(text):
    """
    NUEVA FUNCIÓN: Para formato complejo de bloques:
    [Liga]
    [+número] (opcional)
    [Equipo Local]
    [Equipo Visitante]
    [Fecha Hora]
    [1] [+número] (cuota local)
    [2] [+número] (cuota empate)
    [3] [+número] (cuota visitante)
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    matches = []
    
    i = 0
    while i < len(lines):
        # Buscar patrón de bloque de partido
        # La línea actual puede ser el nombre de la liga
        liga = lines[i]
        
        # Verificar si la siguiente línea es un número con signo (opcional)
        offset = 0
        if i+1 < len(lines) and re.match(r'^[+-]\d+$', lines[i+1]):
            offset = 1
        
        # Después de la liga (y posible número), deben venir dos líneas que son equipos
        if i+offset+3 < len(lines):
            potencial_home = lines[i+offset+0]
            potencial_away = lines[i+offset+1]
            fecha_hora = lines[i+offset+2]
            
            # Buscar las cuotas en las siguientes líneas
            odds = []
            j = i+offset+3
            while j < len(lines) and len(odds) < 3:
                # Buscar patrón de "1 +XXX", "2 +XXX", "3 +XXX"
                match = re.match(r'^(\d)\s+([+-]\d+)$', lines[j])
                if match:
                    odds.append(match.group(2))
                j += 1
            
            # Si encontramos 3 cuotas, tenemos un partido
            if len(odds) >= 3 and potencial_home and potencial_away:
                # Limpiar nombres de equipos (quitar (W), (R), etc.)
                home_clean = re.sub(r'\s*\([^)]*\)', '', potencial_home).strip()
                away_clean = re.sub(r'\s*\([^)]*\)', '', potencial_away).strip()
                
                matches.append({
                    'home': home_clean,
                    'away': away_clean,
                    'all_odds': odds[:3],
                    'liga': liga,
                    'fecha': fecha_hora
                })
                # Avanzar al siguiente bloque
                i = j
                continue
        
        i += 1
    
    return matches

def generar_parlay_pro(matches_analizados, max_selecciones=3):
    """Genera parlay con las mejores opciones"""
    if len(matches_analizados) < 2:
        return None
    
    selecciones_ordenadas = []
    for match in matches_analizados:
        best = match.get('best_bet', {})
        if best and best.get('probability', 0) > 0.55:
            selecciones_ordenadas.append({
                'partido': f"{match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}",
                'apuesta': best.get('market', 'Over 1.5 goles'),
                'prob': best.get('probability', 0.7),
                'confianza': best.get('confidence', 'MEDIA'),
                'liga': match.get('liga', 'Desconocida'),
                'razon': best.get('reason', '')
            })
    
    selecciones_ordenadas.sort(key=lambda x: x['prob'], reverse=True)
    selecciones = selecciones_ordenadas[:max_selecciones]
    
    if len(selecciones) >= 2:
        prob_total = np.prod([s['prob'] for s in selecciones])
        
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
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.55, 0.05)
        
        st.subheader("🎲 Mercados")
        categorias = st.multiselect(
            "Categorías",
            ["1X2", "Totales", "Primer Tiempo", "BTTS", "Combinado"],
            default=["1X2", "Totales", "BTTS"]
        )
        
        check_live_odds = st.checkbox("📡 Verificar odds en vivo", value=True)
        max_parlay = st.slider("Máximo selecciones por parlay", 2, 5, 3, 1)
        
        st.divider()
        
        col_api1, col_api2, col_api3 = st.columns(3)
        with col_api1:
            st.success("⚽ API") if st.secrets.get("FOOTBALL_API_KEY") else st.warning("⚽ No API")
        with col_api2:
            st.success("🤖 Groq") if st.secrets.get("GROQ_API_KEY") else st.warning("🤖 No Groq")
        with col_api3:
            st.success("📊 Odds") if st.secrets.get("ODDS_API_KEY") else st.warning("📊 No Odds")
        
        debug_mode = st.checkbox("🔧 Modo debug", value=True)
        components['tracker'].show_tracker_ui()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Procesando imagen..."):
            img_bytes = uploaded_file.getvalue()
            matches = []
            raw_text = ""
            metodo_usado = "Ninguno"
            
            # INTENTO 1: Groq Vision
            if components['groq_vision']:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    if matches:
                        metodo_usado = "Groq Vision AI"
                        st.success(f"✅ {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    if debug_mode:
                        st.warning(f"Groq Vision falló: {e}")
            
            # INTENTO 2: OCR tradicional con múltiples formatos
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                        
                        # Intentar formato complejo primero (nueva función)
                        matches = parse_complex_betting_text(raw_text)
                        if matches:
                            metodo_usado = "OCR + Parsing (formato complejo)"
                        else:
                            # Si no, intentar formato estándar de 6 líneas
                            matches = parse_raw_betting_text(raw_text)
                            metodo_usado = "OCR + Parsing (6 líneas)"
                        
                        st.info(f"📝 {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
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
            
            if debug_mode and raw_text:
                with st.expander("🔬 Ver texto raw detectado"):
                    st.code(raw_text[:500])
            
            st.divider()
            st.subheader("3. Análisis Profesional")
            
            matches_analizados = []
            
            for i, match in enumerate(matches):
                home = match.get('home', 'Unknown')
                away = match.get('away', 'Unknown')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                liga_info = match.get('liga', '')
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    if liga_info:
                        st.caption(f"🏆 {liga_info}")
                    st.caption(f"🎲 Cuotas: Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    analysis = components['analyzer'].analyze_match(home, away, odds)
                    
                    if analysis:
                        liga = analysis.get('liga', 'Desconocida')
                        st.info(f"🏆 Liga detectada: **{liga}**")
                        
                        if check_live_odds:
                            fixture_id = components['odds'].get_fixture_id(home, away, liga)
                            if fixture_id:
                                with st.spinner("📡 Consultando odds en vivo..."):
                                    live_odds = components['odds'].get_best_odds(fixture_id)
                                    if live_odds:
                                        st.success("📊 Odds en vivo encontradas:")
                                        col_odd1, col_odd2, col_odd3 = st.columns(3)
                                        with col_odd1:
                                            st.metric("Local", f"{live_odds['home']['value']}", 
                                                     f"{live_odds['home']['bookmaker'][:10]}")
                                        with col_odd2:
                                            st.metric("Empate", f"{live_odds['draw']['value']}", 
                                                     f"{live_odds['draw']['bookmaker'][:10]}")
                                        with col_odd3:
                                            st.metric("Visitante", f"{live_odds['away']['value']}", 
                                                     f"{live_odds['away']['bookmaker'][:10]}")
                        
                        if debug_mode and analysis.get('reglas_aplicadas'):
                            with st.expander("📋 Reglas aplicadas"):
                                for r in analysis['reglas_aplicadas']:
                                    st.caption(f"• {r}")
                        
                        best = analysis.get('best_bet', {})
                        if best:
                            conf_color = {'ALTA': '🟢', 'MEDIA': '🟡', 'BAJA': '🔴'}.get(best.get('confidence', 'MEDIA'), '⚪')
                            
                            with st.container(border=True):
                                st.markdown(f"### {conf_color} RECOMENDACIÓN DEL EXPERTO")
                                st.markdown(f"**{best.get('market', 'Over 1.5 goles')}** - {best.get('probability', 0.7):.1%}")
                                st.markdown(f"📌 *{best.get('reason', 'Análisis basado en contexto de liga')}*")
                                st.caption(f"Confianza: {best.get('confidence', 'MEDIA')}")
                        
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
            
            if matches_analizados:
                st.divider()
                st.subheader("🎯 Parlay Recomendado por el Experto")
                
                parlay_pro = generar_parlay_pro(matches_analizados, max_parlay)
                
                if parlay_pro:
                    with st.container(border=True):
                        col_p1, col_p2, col_p3 = st.columns(3)
                        with col_p1:
                            st.metric("Cuota Estimada", parlay_pro['cuota_estimada'])
                        with col_p2:
                            prob_pct = parlay_pro['probabilidad_total'] * 100
                            st.metric("Probabilidad Total", f"{prob_pct:.1f}%")
                        with col_p3:
                            conf_emoji = {'ALTO': '🟢', 'MEDIO': '🟡', 'BAJO': '🔴'}.get(parlay_pro['nivel_confianza'], '⚪')
                            st.metric("Confianza", f"{conf_emoji} {parlay_pro['nivel_confianza']}")
                        
                        st.markdown("**Selecciones del parlay:**")
                        for s in parlay_pro['selecciones']:
                            conf_emoji = '🟢' if s['confianza'] == 'ALTA' else '🟡' if s['confianza'] == 'MEDIA' else '🔴'
                            st.markdown(f"{conf_emoji} **{s['partido']}**: {s['apuesta']} ({s['prob']:.1%})")
                            if s.get('razon'):
                                st.caption(f"   📌 {s['razon']}")
                        
                        if st.button("📝 Registrar este parlay", key="register_pro"):
                            components['tracker'].add_bet({
                                'matches': [f"{s['partido']}: {s['apuesta']}" for s in parlay_pro['selecciones']],
                                'total_odds': parlay_pro['cuota_estimada'],
                                'total_prob': parlay_pro['probabilidad_total']
                            }, stake=100)
                            st.success("✅ Parlay registrado!")
                            st.rerun()
                else:
                    st.info("No hay suficientes partidos con alta probabilidad")
        
        else:
            st.error("❌ No se detectaron partidos")
            if raw_text:
                st.code(raw_text)
    
    else:
        st.info("👆 Sube una imagen para comenzar")

if __name__ == "__main__":
    main()