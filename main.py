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
from modules.ollama_analyzer import OllamaAnalyzer
from modules.parlay_optimizer import ParlayOptimizer
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
        'ollama': OllamaAnalyzer(),
        'optimizer': ParlayOptimizer(),
    }

components = init_components()

def generar_parlay_pro(matches_analizados, max_selecciones=3):
    """Genera parlay con las mejores opciones (diversificadas y sin duplicados)"""
    if len(matches_analizados) < 2:
        return None
    
    selecciones = []
    categorias_usadas = set()
    partidos_usados = set()
    
    for match in matches_analizados:
        # Buscar la mejor opción que no sea Over 1.5 si ya tenemos muchos
        best = match.get('best_bet', {})
        markets = match.get('markets', [])
        match_name = f"{match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}"
        
        if match_name in partidos_usados:
            continue
            
        # Priorizar mercados diferentes a Over 1.5
        mejores_opciones = sorted(markets, key=lambda x: x['prob'], reverse=True)
        
        seleccionado = None
        for opcion in mejores_opciones[:5]:  # Top 5
            if opcion['name'] != 'Over 1.5 goles' and opcion['category'] not in categorias_usadas:
                seleccionado = opcion
                break
        
        # Si no encontramos, usar la mejor opción
        if not seleccionado and mejores_opciones:
            seleccionado = mejores_opciones[0]
        
        if seleccionado and seleccionado.get('prob', 0) > 0.55:
            categorias_usadas.add(seleccionado.get('category', ''))
            partidos_usados.add(match_name)
            
            selecciones.append({
                'match': match_name,
                'selection': seleccionado['name'],
                'prob': seleccionado['prob'],
                'odd': 1 / seleccionado['prob'] * 0.95,
                'confianza': seleccionado.get('confidence', 'MEDIA'),
                'category': seleccionado.get('category', ''),
                'razon': seleccionado.get('reason', '')
            })
            
            if len(selecciones) >= max_selecciones:
                break
    
    if len(selecciones) >= 2:
        prob_total = np.prod([s['prob'] for s in selecciones])
        odds_total = np.prod([s['odd'] for s in selecciones])
        
        return {
            'selecciones': selecciones,
            'probabilidad_total': prob_total,
            'cuota_estimada': round(odds_total, 2),
            'nivel_confianza': 'MEDIO' if prob_total > 0.2 else 'BAJO',
            'ev': (prob_total * odds_total) - 1
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
        value_threshold = st.slider("Umbral de valor", 0.0, 0.2, 0.05, 0.01)
        use_ollama = st.checkbox("🤖 Usar IA local (Ollama)", value=True)
        
        st.divider()
        
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            if st.secrets.get("FOOTBALL_API_KEY"):
                st.success("⚽ API")
        with col_api2:
            if components['ollama'].is_available:
                st.success("🤖 Ollama: Conectado")
            else:
                st.warning("🤖 Ollama: No disponible")
        
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
            
            try:
                from google.cloud import vision
                image = vision.Image(content=img_bytes)
                response = components['vision'].client.text_detection(image=image)
                if response.text_annotations:
                    raw_text = response.text_annotations[0].description
                    matches = components['parser'].parse(raw_text)
                    st.info(f"📝 Partidos detectados: {len(matches)}")
            except Exception as e:
                st.error(f"Error en OCR: {e}")
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                df_view = []
                for m in matches:
                    odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    df_view.append({
                        'LOCAL': m.get('home', 'N/A')[:20],
                        'CUOTA L': odds[0],
                        'EMPATE': 'Empate',
                        'CUOTA E': odds[1],
                        'VISITANTE': m.get('away', 'N/A')[:20],
                        'CUOTA V': odds[2]
                    })
                
                st.dataframe(pd.DataFrame(df_view), use_container_width=True, hide_index=True)
            
            if debug_mode and raw_text:
                with st.expander("🔬 Ver texto raw detectado"):
                    st.code(raw_text[:2000])
            
            st.divider()
            st.subheader("3. Análisis Profesional")
            
            matches_analizados = []
            all_picks_for_optimizer = []
            
            for i, match in enumerate(matches):
                home = match.get('home', 'Unknown')
                away = match.get('away', 'Unknown')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    st.caption(f"🎲 Cuotas: Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    analysis = components['analyzer'].analyze_match(home, away, odds)
                    
                    if analysis:
                        liga = analysis.get('liga', 'Desconocida')
                        st.info(f"🏆 Liga detectada: **{liga}**")
                        
                        # Análisis con Ollama
                        if use_ollama and components['ollama'].is_available:
                            with st.spinner("🤖 Consultando IA local..."):
                                ollama_analysis = components['ollama'].analyze_match(home, away)
                                if ollama_analysis:
                                    st.info("🤖 Análisis de IA Local:")
                                    col_ollama1, col_ollama2, col_ollama3 = st.columns(3)
                                    with col_ollama1:
                                        st.metric("Local", f"{ollama_analysis.get('local_win_prob', 0):.1%}")
                                    with col_ollama2:
                                        st.metric("Empate", f"{ollama_analysis.get('draw_prob', 0):.1%}")
                                    with col_ollama3:
                                        st.metric("Visitante", f"{ollama_analysis.get('away_win_prob', 0):.1%}")
                                    st.caption(f"💡 {ollama_analysis.get('explanation', '')}")
                        
                        # Detector de valor
                        value_result = components['value_detector'].get_best_value_bet(analysis, match)
                        
                        if value_result:
                            with st.container(border=True):
                                if value_result.get('type') == 'value_bet' and value_result.get('edge', 0) > value_threshold:
                                    st.markdown(f"### 🔥 VALUE BET DETECTADO")
                                    st.markdown(f"**{value_result['market']}**")
                                    
                                    col_val1, col_val2 = st.columns(2)
                                    with col_val1:
                                        st.metric("Tu probabilidad", f"{value_result.get('implied_probability', 0):.1%}")
                                        st.metric("Odds justas", f"{1/value_result['implied_probability']:.2f}")
                                    with col_val2:
                                        st.metric("Odds mercado", f"{value_result['decimal_odd']:.2f}")
                                        st.metric("📈 EDGE", f"+{value_result['edge']:.1%}")
                                    
                                    st.success(value_result['recommendation'])
                                else:
                                    best = analysis.get('best_bet', {})
                                    st.markdown(f"### ✨ RECOMENDACIÓN")
                                    st.markdown(f"**{best.get('market', 'Over 1.5')}** - {best.get('probability', 0.7):.1%}")
                                    st.markdown(f"📌 *{best.get('reason', 'Análisis contextual')}*")
                        
                        # Preparar picks para optimizador
                        markets_filtered = [
                            m for m in analysis.get('markets', []) 
                            if m.get('prob', 0) >= prob_minima and m.get('category', '') in categorias
                        ]
                        
                        for m in markets_filtered[:3]:
                            all_picks_for_optimizer.append({
                                'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                                'selection': m['name'],
                                'prob': m['prob'],
                                'odd': 1 / m['prob'] * 0.95,
                                'category': m['category']
                            })
                        
                        matches_analizados.append(analysis)
            
            if matches_analizados:
                st.divider()
                
                # PARLAY TRADICIONAL
                st.subheader("🎯 Parlay Tradicional")
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
                            st.markdown(f"{conf_emoji} **{s['match']}**: {s['selection']} ({s['prob']:.1%})")
                        
                        if st.button("📝 Registrar parlay tradicional"):
                            components['tracker'].add_bet({
                                'matches': [f"{s['match']}: {s['selection']}" for s in parlay['selecciones']],
                                'total_odds': parlay['cuota_estimada'],
                                'total_prob': parlay['probabilidad_total']
                            }, stake=100)
                            st.success("✅ Parlay registrado!")
                            st.rerun()
                
            # PARLAY OPTIMIZADO (basado en EV)
if all_picks_for_optimizer and len(all_picks_for_optimizer) >= 2:
    st.divider()
    st.subheader("🎯 Parlay Optimizado (Basado en EV)")
    
    optimal = components['optimizer'].find_optimal_parlays(
        all_picks_for_optimizer, 
        max_size=max_parlay,
        target_ev=value_threshold
    )
    
    if optimal and isinstance(optimal, dict) and 'picks' in optimal:
        prob_opt = np.prod([p['prob'] for p in optimal['picks']])
        odds_opt = np.prod([p['odd'] for p in optimal['picks']])
        ev_opt = optimal.get('ev_combined', (prob_opt * odds_opt) - 1)
        
        with st.container(border=True):
            col_o1, col_o2, col_o3 = st.columns(3)
            with col_o1:
                st.metric("Cuota", f"{odds_opt:.2f}")
            with col_o2:
                st.metric("Probabilidad", f"{prob_opt:.1%}")
            with col_o3:
                st.metric("EV", f"{ev_opt:.2%}")
            
            st.markdown("**Selecciones:**")
            for p in optimal['picks']:
                ev_color = '🟢' if p.get('ev', 0) > value_threshold else '🟡'
                st.markdown(f"{ev_color} **{p['match']}**: {p['selection']} ({p['prob']:.1%}) [EV: {p.get('ev', 0):.2%}]")
            
            if st.button("📝 Registrar parlay optimizado"):
                components['tracker'].add_bet({
                    'matches': [f"{p['match']}: {p['selection']}" for p in optimal['picks']],
                    'total_odds': odds_opt,
                    'total_prob': prob_opt
                }, stake=100)
                st.success("✅ Parlay registrado!")
                st.rerun()
    else:
        st.info("No se encontró un parlay con EV positivo")
