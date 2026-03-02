import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.pro_analyzer import ProAnalyzer
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker

st.set_page_config(page_title="Analizador Profesional de Apuestas", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': ProAnalyzer(),  # <-- NUEVO ANALIZADOR PROFESIONAL
        'tracker': BettingTracker()
    }

components = init_components()

def parse_raw_betting_text(text):
    """Extrae partidos del texto"""
    pattern = r"([a-zA-Z\s]+?)([-+]\d+)\s*Empate\s*([-+]\d+)([a-zA-Z\s]+?)([-+]\d+)"
    matches = re.findall(pattern, text)
    
    return [{
        'home': m[0].strip(),
        'away': m[3].strip(),
        'all_odds': [m[1], m[2], m[4]]
    } for m in matches]

def generar_parlay_pro(matches_analizados):
    """Genera parlay con las mejores opciones de cada partido"""
    if len(matches_analizados) < 2:
        return None
    
    selecciones = []
    prob_total = 1.0
    
    for match in matches_analizados:
        best = match.get('best_bet', {})
        if best and best.get('probability', 0) > 0.5:
            selecciones.append({
                'partido': f"{match['home_team']} vs {match['away_team']}",
                'apuesta': best['market'],
                'prob': best['probability'],
                'confianza': best.get('confidence', 'MEDIA')
            })
            prob_total *= best['probability']
    
    if len(selecciones) >= 2:
        return {
            'selecciones': selecciones,
            'probabilidad_total': prob_total,
            'cuota_estimada': round(1 / prob_total * 0.9, 2),
            'nivel_confianza': 'ALTO' if prob_total > 0.25 else 'MEDIO' if prob_total > 0.15 else 'BAJO'
        }
    return None

def main():
    st.title("🎯 Analizador Profesional de Apuestas")
    st.markdown("**Piensa como un apostador profesional** - Analiza cualquier partido del mundo")
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.5, 0.05)
        
        st.subheader("🎲 Mercados")
        categorias = st.multiselect(
            "Categorías",
            ["1X2", "Totales", "Primer Tiempo", "BTTS", "Combinado"],
            default=["1X2", "Totales", "BTTS"]
        )
        
        if st.secrets.get("GROQ_API_KEY"):
            st.success("🤖 Groq AI: CONECTADO")
        else:
            st.warning("🤖 Groq AI: NO CONECTADO")
        
        debug_mode = st.checkbox("🔧 Modo debug", value=True)
        components['tracker'].show_tracker_ui()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Procesando imagen..."):
            img_bytes = uploaded_file.getvalue()
            matches = []
            raw_text = ""
            
            # Intentar con Groq Vision primero
            if components['groq_vision']:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    st.success("✅ Groq Vision: OK")
                except:
                    pass
            
            # Fallback a OCR tradicional
            if not matches:
                from google.cloud import vision
                image = vision.Image(content=img_bytes)
                response = components['vision'].client.text_detection(image=image)
                if response.text_annotations:
                    raw_text = response.text_annotations[0].description
                    matches = parse_raw_betting_text(raw_text)
                    st.info("📝 Usando OCR tradicional")
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df_view = [{
                    'LOCAL': m['home'],
                    'CUOTA L': m['all_odds'][0],
                    'EMPATE': 'Empate',
                    'CUOTA E': m['all_odds'][1],
                    'VISITANTE': m['away'],
                    'CUOTA V': m['all_odds'][2]
                } for m in matches]
                st.dataframe(pd.DataFrame(df_view), use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("3. Análisis Profesional (como apostador real)")
            
            matches_analizados = []
            
            for i, match in enumerate(matches):
                home = match['home']
                away = match['away']
                odds = match['all_odds']
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    st.caption(f"🎲 Cuotas: Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Análisis profesional
                    analysis = components['analyzer'].analyze_match(home, away, odds)
                    
                    # Mostrar fuente del análisis
                    st.info(f"📚 Fuente: {analysis['source']}")
                    
                    # Mostrar mejor apuesta según el profesional
                    best = analysis['best_bet']
                    
                    # Tarjeta de recomendación
                    with st.container(border=True):
                        conf_color = {
                            'ALTA': '🟢',
                            'MEDIA': '🟡',
                            'BAJA': '🔴'
                        }.get(best.get('confidence', 'MEDIA'), '⚪')
                        
                        st.markdown(f"### {conf_color} RECOMENDACIÓN DEL EXPERTO")
                        st.markdown(f"**{best['market']}** - {best['probability']:.1%} probabilidad")
                        st.markdown(f"📌 *{best['reason']}*")
                    
                    # Mostrar mercados disponibles
                    markets_filtered = [m for m in analysis['markets'] 
                                       if m['prob'] >= prob_minima and m['category'] in categorias]
                    
                    if markets_filtered:
                        st.caption("📊 Todos los mercados analizados:")
                        df_markets = pd.DataFrame([{
                            'Mercado': m['name'],
                            'Prob': f"{m['prob']:.1%}",
                            'Tipo': m['category']
                        } for m in markets_filtered[:8]])
                        st.dataframe(df_markets, use_container_width=True, hide_index=True)
                    
                    matches_analizados.append(analysis)
            
            # ============================================================================
            # PARLAY PROFESIONAL
            # ============================================================================
            st.divider()
            st.subheader("🎯 Parlay Recomendado por el Experto")
            
            parlay_pro = generar_parlay_pro(matches_analizados)
            
            if parlay_pro:
                with st.container(border=True):
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("Cuota Estimada", parlay_pro['cuota_estimada'])
                    with col_p2:
                        st.metric("Probabilidad Total", f"{parlay_pro['probabilidad_total']:.1%}")
                    with col_p3:
                        st.metric("Confianza", parlay_pro['nivel_confianza'])
                    
                    st.markdown("**Selecciones:**")
                    for s in parlay_pro['selecciones']:
                        conf_emoji = '🟢' if s['confianza'] == 'ALTA' else '🟡' if s['confianza'] == 'MEDIA' else '🔴'
                        st.markdown(f"{conf_emoji} {s['partido']}: **{s['apuesta']}** ({s['prob']:.1%})")
                    
                    if st.button("📝 Registrar este parlay", key="register_pro"):
                        components['tracker'].add_bet({
                            'matches': [f"{s['partido']}: {s['apuesta']}" for s in parlay_pro['selecciones']],
                            'total_odds': parlay_pro['cuota_estimada'],
                            'total_prob': parlay_pro['probabilidad_total']
                        }, stake=100)
                        st.success("✅ Parlay registrado!")
                        st.rerun()
            else:
                st.info("No hay suficientes partidos con alta probabilidad para un parlay")
        
        else:
            st.error("❌ No se detectaron partidos en la imagen")
    
    else:
        st.info("👆 Sube una imagen para comenzar el análisis profesional")

if __name__ == "__main__":
    main()
