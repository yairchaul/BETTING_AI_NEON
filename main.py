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
from modules.betting_tracker import BettingTracker

st.set_page_config(page_title="Analizador Pro: IA + Value Betting", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa todos los componentes del ecosistema"""
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
    """Genera parlay con las mejores opciones (diversificadas)"""
    if len(matches_analizados) < 2:
        return None
    
    selecciones = []
    categorias_usadas = set()
    partidos_usados = set()
    
    for match in matches_analizados:
        markets = match.get('markets', [])
        match_name = f"{match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}"
        
        if match_name in partidos_usados:
            continue
            
        mejores_opciones = sorted(markets, key=lambda x: x['prob'], reverse=True)
        
        seleccionado = None
        for opcion in mejores_opciones[:5]:
            if opcion['name'] != 'Over 1.5 goles' and opcion['category'] not in categorias_usadas:
                seleccionado = opcion
                break
        
        if not seleccionado and mejores_opciones:
            seleccionado = mejores_opciones[0]
        
        if seleccionado and seleccionado.get('prob', 0) > 0.55:
            categorias_usadas.add(seleccionado.get('category', ''))
            partidos_usados.add(match_name)
            
            cuota_final = seleccionado.get('real_odd') or (1 / seleccionado['prob'] * 0.95)
            
            selecciones.append({
                'match': match_name,
                'selection': seleccionado['name'],
                'prob': seleccionado['prob'],
                'odd': cuota_final,
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
    st.title("🎯 Analizador Pro: IA + Value Betting")
    st.markdown("**Sistema Híbrido:** Visión por Computadora + Análisis de Probabilidad + Gestión de Riesgo (Kelly)")
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        bankroll = st.number_input("Bankroll Total ($)", value=1000, min_value=1)
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.55, 0.05)
        value_threshold = st.slider("Umbral de EV para Parlay", 0.0, 0.2, 0.05, 0.01)
        max_parlay = st.slider("Máximo selecciones parlay", 2, 5, 3, 1)
        
        st.divider()
        use_ollama = st.checkbox("🤖 Usar IA local (Ollama)", value=True)
        debug_mode = st.checkbox("🔧 Modo debug", value=False)
        
        components['tracker'].show_tracker_ui()

    uploaded_file = st.file_uploader("Sube tu captura de pantalla", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        img_bytes = uploaded_file.getvalue()
        
        with col1:
            st.image(uploaded_file, caption="Captura original", use_container_width=True)

        with st.spinner("🔍 Procesando imagen con Visión Híbrida..."):
            try:
                matches = components['parser'].parse_image(img_bytes)
            except Exception as e:
                st.error(f"Error en visión: {e}")
                matches = []
            
        if matches:
            with col2:
                st.subheader(f"Partidos detectados ({len(matches)})")
                df_view = [{'LOCAL': m['home'], 'VISITANTE': m['away'], 'CUOTAS': m['all_odds']} for m in matches]
                st.dataframe(pd.DataFrame(df_view), use_container_width=True, hide_index=True)

            st.divider()
            
            all_picks_for_optimizer = []
            matches_analizados = []
            
            for i, match in enumerate(matches):
                home, away = match['home'], match['away']
                odds_raw = match['all_odds']
                
                with st.expander(f"📊 {home} vs {away}", expanded=(i==0)):
                    analysis = components['analyzer'].analyze_match(home, away, odds_raw)
                    
                    if analysis:
                        # 🤖 Análisis Extra: Ollama
                        if use_ollama and components['ollama'].is_available:
                            ollama_analysis = components['ollama'].analyze_match(home, away)
                            if ollama_analysis:
                                st.info(f"🤖 IA Local: {ollama_analysis.get('explanation', '')[:150]}...")

                        # 💰 Análisis de Valor Optimizado
                        value_result = components['value_detector'].get_best_value_bet(analysis, match, bankroll=bankroll)
                        
                        if value_result:
                            with st.container(border=True):
                                if value_result.get('type') == 'high_value':
                                    st.markdown("### 🔥🔥 HIGH VALUE BET DETECTADO 🔥🔥")
                                elif value_result.get('type') == 'value_bet':
                                    st.markdown("### 🔥 VALUE BET DETECTADO")
                                else:
                                    st.markdown("### ✨ MEJOR OPCIÓN")

                                st.markdown(f"**Mercado:** {value_result.get('market', 'N/A')}")
                                
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Prob. IA", f"{value_result.get('market_prob', 0):.1%}")
                                c2.metric("Cuota Real", f"{value_result.get('decimal_odd', 0):.2f}")
                                c3.metric("📈 EV", f"{value_result.get('ev', 0):.1%}")
                                
                                if value_result.get('stake', 0) > 0:
                                    st.success(f"💰 **Stake sugerido (Kelly): ${value_result['stake']}**")
                                    st.caption(f"Confianza: {value_result.get('confidence')}")

                                # Registrar en Tracker
                                if st.button(f"Registrar apuesta: {home}", key=f"btn_{i}"):
                                    components['tracker'].add_bet(home, away, value_result['market'], value_result['decimal_odd'], value_result['stake'])
                                    st.toast("✅ Registrada")

                        # Recolectar para Parlay
                        matches_analizados.append(analysis)
                        for m in analysis.get('markets', []):
                            if m['prob'] >= prob_minima:
                                all_picks_for_optimizer.append({
                                    'match': f"{home} vs {away}",
                                    'selection': m['name'],
                                    'prob': m['prob'],
                                    'odd': value_result['decimal_odd'] if value_result and value_result['market'] == m['name'] else (1/m['prob']*0.95),
                                    'ev': value_result['ev'] if value_result and value_result['market'] == m['name'] else 0
                                })

            # --- SECCIÓN DE PARLAYS ---
            if matches_analizados:
                st.divider()
                col_par1, col_par2 = st.columns(2)
                
                with col_par1:
                    st.subheader("🎯 Parlay Tradicional")
                    parlay = generar_parlay_pro(matches_analizados, max_parlay)
                    if parlay:
                        with st.container(border=True):
                            st.metric("Cuota Total", parlay['cuota_estimada'])
                            for s in parlay['selecciones']:
                                st.write(f"✅ {s['match']}: {s['selection']}")

                with col_par2:
                    st.subheader("🎯 Parlay Optimizado (EV)")
                    if len(all_picks_for_optimizer) >= 2:
                        optimal = components['optimizer'].find_optimal_parlays(all_picks_for_optimizer, max_size=max_parlay, target_ev=value_threshold)
                        if optimal:
                            with st.container(border=True):
                                st.metric("EV Combinado", f"{optimal.get('combined_ev', 0):.2%}")
                                for p in optimal['picks']:
                                    st.write(f"🔥 {p['match']}: {p['selection']}")
        else:
            st.error("No se detectaron partidos. Intenta una imagen con mejor contraste.")
    else:
        st.info("👆 Sube una imagen de tu casa de apuestas para comenzar el análisis profesional.")

if __name__ == "__main__":
    main()
