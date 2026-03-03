import streamlit as st
import pandas as pd
import numpy as np
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.universal_parser import UniversalParser
from modules.smart_searcher import SmartSearcher
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.odds_integrator import OddsIntegrator
from modules.value_detector import ValueDetector
from modules.ml_predictor import MLPredictor
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker

st.set_page_config(page_title="Analizador Profesional de Apuestas", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa todos los componentes"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser(),
        'parser': UniversalParser(),
        'searcher': SmartSearcher(),
        'analyzer': ProAnalyzerUltimate(),
        'odds': OddsIntegrator(),
        'tracker': BettingTracker(),
        'value_detector': ValueDetector(),
        'ml_predictor': MLPredictor()
    }

components = init_components()

def generar_parlay_pro(matches_analizados, max_selecciones=3):
    """Genera parlay con las mejores opciones"""
    if len(matches_analizados) < 2:
        return None
    
    selecciones = []
    for match in matches_analizados:
        best = match.get('best_bet', {})
        if best and best.get('probability', 0) > 0.55:
            selecciones.append({
                'partido': f"{match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}",
                'apuesta': best.get('market', 'Over 1.5 goles'),
                'prob': best.get('probability', 0.7),
                'confianza': best.get('confidence', 'MEDIA'),
                'liga': match.get('liga', 'Desconocida'),
                'razon': best.get('reason', '')
            })
    
    selecciones.sort(key=lambda x: x['prob'], reverse=True)
    selecciones = selecciones[:max_selecciones]
    
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
        
        # Umbral de valor para value betting
        value_threshold = st.slider("Umbral de valor (edge mínimo)", 0.0, 0.2, 0.05, 0.01, 
                                   help="Mínimo porcentaje de ventaja para considerar VALUE BET")
        
        # Opción para usar ML
        use_ml = st.checkbox("🧠 Usar predicción ML (si está entrenado)", value=True)
        
        st.divider()
        
        col_api1, col_api2, col_api3 = st.columns(3)
        with col_api1:
            if st.secrets.get("FOOTBALL_API_KEY"):
                st.success("⚽ API")
            else:
                st.warning("⚽ No API")
        with col_api2:
            if components['groq_vision'].is_available:
                st.success("🤖 Groq OK")
            else:
                st.warning("🤖 Groq No disponible")
        with col_api3:
            if st.secrets.get("ODDS_API_KEY"):
                st.success("📊 Odds")
            else:
                st.warning("📊 No Odds")
        
        # Estado del modelo ML
        if components['ml_predictor'].is_trained:
            st.success("🧠 ML: Entrenado")
        else:
            st.warning("🧠 ML: No entrenado (ve a la página de entrenamiento)")
        
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
            
            # INTENTO 1: Groq Vision (si está disponible)
            if components['groq_vision'].is_available:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    if matches:
                        metodo_usado = "Groq Vision AI"
                        st.success(f"✅ {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    if debug_mode:
                        st.warning(f"Groq Vision falló: {e}")
            
            # INTENTO 2: Google Vision + Parser Universal
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                        matches = components['parser'].parse(raw_text)
                        metodo_usado = "Google Vision + Parser Universal"
                        st.info(f"📝 {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
            
            # INTENTO 3: Google Vision con coordenadas
            if not matches and components['vision'].client:
                try:
                    matches = components['vision'].process_image(img_bytes)
                    metodo_usado = "Google Vision + Coordenadas"
                    st.info(f"📐 {metodo_usado}: {len(matches)} partidos")
                except Exception as e:
                    if debug_mode:
                        st.warning(f"Error en coordenadas: {e}")
        
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
                    st.code(raw_text[:2000])
            
            st.divider()
            st.subheader("3. Análisis Profesional")
            
            matches_analizados = []
            
            for i, match in enumerate(matches):
                home = match.get('home', 'Unknown')
                away = match.get('away', 'Unknown')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    st.caption(f"🎲 Cuotas: Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Análisis con reglas de experto
                    analysis = components['analyzer'].analyze_match(home, away, odds)
                    
                    if analysis:
                        liga = analysis.get('liga', 'Desconocida')
                        st.info(f"🏆 Liga detectada: **{liga}**")
                        
                        # Predicción ML (si está entrenado y activado)
                        if use_ml and components['ml_predictor'].is_trained:
                            with st.spinner("🧠 Prediciendo con ML..."):
                                # Preparar características (simplificado)
                                home_stats = {
                                    'home_goals_for': 1.5, 'home_goals_against': 1.2,
                                    'home_btts_pct': 50, 'home_wins_pct': 50
                                }
                                away_stats = {
                                    'away_goals_for': 1.2, 'away_goals_against': 1.4,
                                    'away_btts_pct': 48, 'away_wins_pct': 40
                                }
                                league_data = {
                                    'goles_promedio': 2.5, 'local_ventaja': 55, 'btts_pct': 50
                                }
                                
                                features = components['ml_predictor'].prepare_features(
                                    home_stats, away_stats, league_data
                                )
                                
                                ml_pred = components['ml_predictor'].predict(features)
                                
                                if ml_pred:
                                    st.info("🧠 Predicción ML vs Experto:")
                                    col_ml1, col_ml2, col_ml3 = st.columns(3)
                                    with col_ml1:
                                        st.metric("Local", 
                                                 f"{ml_pred['local']:.1%}", 
                                                 f"{ml_pred['local'] - analysis['probabilidades'].get('local_gana', 0):.1%}")
                                    with col_ml2:
                                        st.metric("Empate", 
                                                 f"{ml_pred['empate']:.1%}",
                                                 f"{ml_pred['empate'] - analysis['probabilidades'].get('empate', 0):.1%}")
                                    with col_ml3:
                                        st.metric("Visitante",
                                                 f"{ml_pred['visitante']:.1%}",
                                                 f"{ml_pred['visitante'] - analysis['probabilidades'].get('visitante_gana', 0):.1%}")
                        
                        # Verificar odds en vivo
                        if check_live_odds:
                            fixture_id = components['odds'].get_fixture_id(home, away, liga)
                            if fixture_id:
                                with st.spinner("📡 Consultando odds en vivo..."):
                                    live_odds = components['odds'].get_best_odds(fixture_id)
                                    if live_odds:
                                        st.success("📊 Odds en vivo:")
                                        col_odd1, col_odd2, col_odd3 = st.columns(3)
                                        with col_odd1:
                                            st.metric("Local", f"{live_odds['home']['value']}", 
                                                     live_odds['home']['bookmaker'][:15])
                                        with col_odd2:
                                            st.metric("Empate", f"{live_odds['draw']['value']}", 
                                                     live_odds['draw']['bookmaker'][:15])
                                        with col_odd3:
                                            st.metric("Visitante", f"{live_odds['away']['value']}", 
                                                     live_odds['away']['bookmaker'][:15])
                        
                        # Detector de valor
                        value_result = components['value_detector'].get_best_value_bet(analysis, match)
                        
                        if value_result:
                            with st.container(border=True):
                                if value_result.get('type') == 'value_bet':
                                    st.markdown(f"### 🔥 VALUE BET DETECTADO")
                                    st.markdown(f"**{value_result['market']}**")
                                    
                                    implied_prob = 1 / value_result['decimal_odd'] if value_result.get('decimal_odd') else 0
                                    
                                    col_val1, col_val2 = st.columns(2)
                                    with col_val1:
                                        st.metric("Tu probabilidad", f"{value_result.get('implied_probability', 0):.1%}")
                                        st.metric("Odds del mercado", f"{value_result['decimal_odd']:.2f}")
                                    with col_val2:
                                        st.metric("Prob. mercado", f"{implied_prob:.1%}")
                                        st.metric("📈 EDGE", f"+{value_result['edge']:.1%}", delta_color="normal")
                                    
                                    st.success(value_result['recommendation'])
                                else:
                                    best = analysis.get('best_bet', {})
                                    conf_color = {'ALTA': '🟢', 'MEDIA': '🟡', 'BAJA': '🔴'}.get(best.get('confidence', 'MEDIA'), '⚪')
                                    
                                    st.markdown(f"### {conf_color} RECOMENDACIÓN")
                                    st.markdown(f"**{best.get('market', 'Over 1.5 goles')}** - {best.get('probability', 0.7):.1%}")
                                    st.markdown(f"📌 *{best.get('reason', 'Análisis contextual')}*")
                                    
                                    if value_result.get('edge', 0) > 0:
                                        st.caption(f"💡 Nota: Hay una pequeña ventaja de {value_result['edge']:.1%} sobre el mercado")
                        else:
                            best = analysis.get('best_bet', {})
                            conf_color = {'ALTA': '🟢', 'MEDIA': '🟡', 'BAJA': '🔴'}.get(best.get('confidence', 'MEDIA'), '⚪')
                            
                            with st.container(border=True):
                                st.markdown(f"### {conf_color} RECOMENDACIÓN")
                                st.markdown(f"**{best.get('market', 'Over 1.5 goles')}** - {best.get('probability', 0.7):.1%}")
                                st.markdown(f"📌 *{best.get('reason', 'Análisis contextual')}*")
                        
                        if debug_mode and analysis.get('reglas_aplicadas'):
                            with st.expander("📋 Reglas aplicadas"):
                                for r in analysis['reglas_aplicadas']:
                                    st.caption(f"• {r}")
                        
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
                st.subheader("🎯 Parlay Recomendado")
                
                parlay = generar_parlay_pro(matches_analizados, max_parlay)
                
                if parlay:
                    with st.container(border=True):
                        col_p1, col_p2, col_p3 = st.columns(3)
                        with col_p1:
                            st.metric("Cuota", parlay['cuota_estimada'])
                        with col_p2:
                            st.metric("Probabilidad", f"{parlay['probabilidad_total']:.1%}")
                        with col_p3:
                            conf_emoji = {'ALTO': '🟢', 'MEDIO': '🟡', 'BAJO': '🔴'}.get(parlay['nivel_confianza'], '⚪')
                            st.metric("Confianza", f"{conf_emoji} {parlay['nivel_confianza']}")
                        
                        for s in parlay['selecciones']:
                            conf_emoji = '🟢' if s['confianza'] == 'ALTA' else '🟡' if s['confianza'] == 'MEDIA' else '🔴'
                            st.markdown(f"{conf_emoji} **{s['partido']}**: {s['apuesta']} ({s['prob']:.1%})")
                        
                        if st.button("📝 Registrar parlay"):
                            components['tracker'].add_bet({
                                'matches': [f"{s['partido']}: {s['apuesta']}" for s in parlay['selecciones']],
                                'total_odds': parlay['cuota_estimada'],
                                'total_prob': parlay['probabilidad_total']
                            }, stake=100)
                            st.success("✅ Parlay registrado!")
                            st.rerun()
        
        else:
            st.error("❌ No se detectaron partidos")
            if raw_text:
                st.code(raw_text)
    
    else:
        st.info("👆 Sube una imagen para comenzar")

if __name__ == "__main__":
    main()