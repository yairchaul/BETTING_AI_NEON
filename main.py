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
from modules.montecarlo_pro import MonteCarloPro

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
        'montecarlo': MonteCarloPro(simulations=50000)
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
    
    # ============================================================================
    # SIDEBAR CONFIGURACIÓN
    # ============================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        bankroll = st.number_input("Bankroll Total ($)", min_value=100, max_value=100000, value=1000, step=100)
        
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.55, 0.05)
        
        st.subheader("🎲 Mercados")
        categorias = st.multiselect(
            "Categorías",
            ["1X2", "Totales", "Primer Tiempo", "BTTS", "Combinado"],
            default=["1X2", "Totales", "BTTS"]
        )
        
        check_live_odds = st.checkbox("📡 Verificar odds en vivo", value=True)
        max_parlay = st.slider("Máximo selecciones por parlay", 2, 5, 3, 1)
        
        value_threshold = st.slider("Umbral de EV para VALUE", 0.0, 0.2, 0.05, 0.01)
        high_value_threshold = st.slider("Umbral de EV para HIGH VALUE", 0.0, 0.3, 0.10, 0.01)
        
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
    
    # ============================================================================
    # ÁREA PRINCIPAL
    # ============================================================================
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
            
            # ============================================================================
            # INICIO: Preparar listas para resumen
            # ============================================================================
            all_picks_for_optimizer = []
            matches_analizados = []
            mejores_opciones_global = []
            
            for i, match in enumerate(matches):
                home = match.get('home', 'Unknown')
                away = match.get('away', 'Unknown')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    st.caption(f"🎲 Cuotas: Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    odds_dict = {'all_odds': odds}
                    analysis = components['analyzer'].analyze_match(home, away, odds_dict)
                    
                    if analysis:
                        liga = analysis.get('liga', 'Desconocida')
                        liga_data = analysis.get('liga_data', {})
                        st.info(f"🏆 Liga detectada: **{liga}**")
                        
                        # Obtener probabilidades
                        final_probs_list = analysis.get('final_probs', [0.33, 0.33, 0.34])
                        mc_probs = analysis.get('mc_stats', {})
                        probs_by_model = analysis.get('probs_by_model', {})
                        
                        # Mostrar estadísticas de Monte Carlo
                        if mc_probs:
                            st.caption(f"📊 Simulación Monte Carlo (50,000 partidos)")
                            col_mc1, col_mc2, col_mc3 = st.columns(3)
                            with col_mc1:
                                st.metric("Goles promedio", f"{mc_probs.get('avg_goals', 0):.2f}")
                            with col_mc2:
                                st.metric("Desviación", f"{mc_probs.get('std_goals', 0):.2f}")
                            with col_mc3:
                                st.metric("Simulaciones", f"{mc_probs.get('simulations', 50000):,}")
                        
                        # Mostrar contribución de modelos
                        if probs_by_model:
                            with st.expander("📊 Contribución de modelos"):
                                col_m1, col_m2, col_m3 = st.columns(3)
                                
                                with col_m1:
                                    st.caption("🎲 Mercado")
                                    st.metric("Local", f"{probs_by_model.get('market', [0,0,0])[0]:.1%}")
                                    st.metric("Empate", f"{probs_by_model.get('market', [0,0,0])[1]:.1%}")
                                    st.metric("Visitante", f"{probs_by_model.get('market', [0,0,0])[2]:.1%}")
                                
                                with col_m2:
                                    st.caption("📈 Poisson")
                                    st.metric("Local", f"{probs_by_model.get('poisson', [0,0,0])[0]:.1%}")
                                    st.metric("Empate", f"{probs_by_model.get('poisson', [0,0,0])[1]:.1%}")
                                    st.metric("Visitante", f"{probs_by_model.get('poisson', [0,0,0])[2]:.1%}")
                                
                                with col_m3:
                                    st.caption("⚡ ELO")
                                    st.metric("Local", f"{probs_by_model.get('elo', [0,0,0])[0]:.1%}")
                                    st.metric("Empate", f"{probs_by_model.get('elo', [0,0,0])[1]:.1%}")
                                    st.metric("Visitante", f"{probs_by_model.get('elo', [0,0,0])[2]:.1%}")
                        
                        # ============================================================================
                        # DETECTOR DE VALOR
                        # ============================================================================
                        value_result = components['value_detector'].get_best_value_bet(analysis, match, bankroll=bankroll)
                        
                        if value_result:
                            with st.container(border=True):
                                if value_result.get('type') == 'high_value':
                                    st.markdown(f"### 🔥🔥 HIGH VALUE BET DETECTADO 🔥🔥")
                                    st.markdown(f"**{value_result['market']}**")
                                    
                                    col_val1, col_val2, col_val3 = st.columns(3)
                                    with col_val1:
                                        st.metric("Tu probabilidad", f"{value_result.get('market_prob', 0):.1%}")
                                        st.metric("Odds justas", f"{value_result['fair_odd']:.2f}")
                                    with col_val2:
                                        st.metric("Odds mercado", f"{value_result['decimal_odd']:.2f}")
                                        st.metric("📈 EV", f"+{value_result['ev']:.1%}")
                                    with col_val3:
                                        st.metric("💰 Stake Kelly", f"${value_result['stake']}")
                                        st.metric("Confianza", value_result['confidence'])
                                    
                                    st.success(value_result['recommendation'])
                                
                                elif value_result.get('type') == 'value_bet':
                                    st.markdown(f"### 🔥 VALUE BET DETECTADO")
                                    st.markdown(f"**{value_result['market']}**")
                                    
                                    col_val1, col_val2 = st.columns(2)
                                    with col_val1:
                                        st.metric("Tu probabilidad", f"{value_result.get('market_prob', 0):.1%}")
                                        st.metric("Odds justas", f"{value_result['fair_odd']:.2f}")
                                    with col_val2:
                                        st.metric("Odds mercado", f"{value_result['decimal_odd']:.2f}")
                                        st.metric("📈 EV", f"+{value_result['ev']:.1%}")
                                    
                                    st.info(f"💡 Stake sugerido: ${value_result['stake']} (Kelly {value_result['confidence']})")
                                    st.success(value_result['recommendation'])
                                
                                else:
                                    best = analysis.get('best_bet', {})
                                    st.markdown(f"### ✨ MEJOR OPCIÓN")
                                    st.markdown(f"**{best.get('market', 'Over 1.5')}** - {best.get('probability', 0.7):.1%}")
                                    st.markdown(f"📌 *{best.get('reason', 'Análisis contextual')}*")
                                    st.caption(f"ℹ️ Sin valor significativo (EV: {value_result.get('ev', 0):.1%})")
                        
                        # ============================================================================
                        # MOSTRAR TODOS LOS MERCADOS ANALIZADOS
                        # ============================================================================
                        with st.expander("📊 Ver TODOS los mercados analizados", expanded=True):
                            st.markdown("### 🎯 RESULTADO FINAL (TIEMPO REGULAR)")
                            
                            col_r1, col_r2, col_r3 = st.columns(3)
                            with col_r1:
                                st.metric("Gana Local", f"{final_probs_list[0]:.1%}")
                            with col_r2:
                                st.metric("Empate", f"{final_probs_list[1]:.1%}")
                            with col_r3:
                                st.metric("Gana Visitante", f"{final_probs_list[2]:.1%}")
                            
                            st.markdown("---")
                            st.markdown("### ⚽ AMBOS EQUIPOS ANOTAN (BTTS)")
                            
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                st.metric("SÍ anotan ambos", f"{mc_probs.get('btts', 0.5):.1%}")
                            with col_b2:
                                st.metric("NO anotan ambos", f"{1 - mc_probs.get('btts', 0.5):.1%}")
                            
                            st.markdown("---")
                            st.markdown("### 📊 TOTAL GOLES OVER/UNDER")
                            
                            over_1_5 = mc_probs.get('over_1_5', 0.8)
                            over_2_5 = mc_probs.get('over_2_5', 0.55)
                            
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                st.metric("Over 1.5", f"{over_1_5:.1%}")
                                st.metric("Under 1.5", f"{1 - over_1_5:.1%}")
                            with col_t2:
                                st.metric("Over 2.5", f"{over_2_5:.1%}")
                                st.metric("Under 2.5", f"{1 - over_2_5:.1%}")
                            with col_t3:
                                st.metric("Over 3.5", f"{mc_probs.get('over_3_5', 0.3):.1%}")
                                st.metric("Under 3.5", f"{1 - mc_probs.get('over_3_5', 0.3):.1%}")
                        
                        # ============================================================================
                        # MEJOR OPCIÓN PARA ESTE PARTIDO
                        # ============================================================================
                        st.markdown("---")
                        st.subheader(f"🎯 Mejor opción para {home} vs {away}")
                        
                        # Crear lista de opciones para este partido
                        opciones_partido = []
                        
                        # 1X2
                        opciones_partido.append(("Gana Local", final_probs_list[0], "1X2"))
                        opciones_partido.append(("Empate", final_probs_list[1], "1X2"))
                        opciones_partido.append(("Gana Visitante", final_probs_list[2], "1X2"))
                        
                        # BTTS
                        btts_prob = mc_probs.get('btts', 0.5)
                        opciones_partido.append(("Ambos anotan (BTTS)", btts_prob, "BTTS"))
                        opciones_partido.append(("No anotan ambos", 1 - btts_prob, "BTTS"))
                        
                        # Totales
                        opciones_partido.append(("Over 1.5 goles", over_1_5, "Totales"))
                        opciones_partido.append(("Under 1.5 goles", 1 - over_1_5, "Totales"))
                        opciones_partido.append(("Over 2.5 goles", over_2_5, "Totales"))
                        opciones_partido.append(("Under 2.5 goles", 1 - over_2_5, "Totales"))
                        
                        # Ordenar por probabilidad
                        opciones_partido.sort(key=lambda x: x[1], reverse=True)
                        
                        # Mejor opción para este partido
                        mejor_opcion_partido = opciones_partido[0]
                        
                        # Guardar para el resumen final
                        mejores_opciones_global.append({
                            'partido': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'opcion': mejor_opcion_partido[0],
                            'probabilidad': mejor_opcion_partido[1],
                            'categoria': mejor_opcion_partido[2],
                            'cuota_justa': 1 / mejor_opcion_partido[1]
                        })
                        
                        # Mostrar la mejor opción destacada
                        with st.container(border=True):
                            col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 1, 1])
                            with col_m1:
                                st.markdown(f"### 🏆 MEJOR OPCIÓN")
                            with col_m2:
                                st.markdown(f"**{mejor_opcion_partido[0]}**")
                            with col_m3:
                                st.metric("Prob", f"{mejor_opcion_partido[1]:.1%}")
                            with col_m4:
                                st.metric("Cuota", f"{1/mejor_opcion_partido[1]:.2f}")
                        
                        # ============================================================================
                        # Preparar picks para el optimizador
                        # ============================================================================
                        markets_filtered = [
                            m for m in analysis.get('markets', []) 
                            if m.get('prob', 0) >= prob_minima and m.get('category', '') in categorias
                        ]
                        
                        for m in markets_filtered[:3]:
                            pick_ev = 0
                            decimal_odd = None
                            
                            if odds[0] != 'N/A' and 'local' in m['name'].lower():
                                decimal_odd = components['value_detector'].american_to_decimal(odds[0])
                            elif odds[2] != 'N/A' and 'visitante' in m['name'].lower():
                                decimal_odd = components['value_detector'].american_to_decimal(odds[2])
                            
                            if decimal_odd:
                                pick_ev = (m['prob'] * decimal_odd) - 1
                            
                            all_picks_for_optimizer.append({
                                'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                                'selection': m['name'],
                                'prob': m['prob'],
                                'odd': decimal_odd if decimal_odd else 1 / m['prob'] * 0.95,
                                'ev': pick_ev,
                                'category': m['category']
                            })
                        
                        matches_analizados.append(analysis)
            
            # ============================================================================
            # RESUMEN FINAL: MEJORES OPCIONES DE TODOS LOS PARTIDOS
            # ============================================================================
            if mejores_opciones_global:
                st.divider()
                st.subheader("📋 RESUMEN DE MEJORES OPCIONES POR PARTIDO")
                
                # Crear DataFrame con todas las mejores opciones
                resumen_data = []
                for idx, mejor in enumerate(mejores_opciones_global):
                    resumen_data.append({
                        '#': idx + 1,
                        'Partido': mejor['partido'],
                        'Mejor opción': mejor['opcion'],
                        'Probabilidad': f"{mejor['probabilidad']:.1%}",
                        'Categoría': mejor['categoria'],
                        'Cuota justa': f"{mejor['cuota_justa']:.2f}"
                    })
                
                df_resumen = pd.DataFrame(resumen_data)
                st.dataframe(df_resumen, use_container_width=True, hide_index=True)
                
                # ============================================================================
                # PARLAY BASADO EN LAS MEJORES OPCIONES
                # ============================================================================
                st.divider()
                st.subheader("🎯 PARLAY RECOMENDADO (Mejores opciones de cada partido)")
                
                # Preparar picks para el parlay
                parlay_picks = []
                for mejor in mejores_opciones_global:
                    odd_estimada = 1 / mejor['probabilidad'] * 0.95
                    
                    parlay_picks.append({
                        'match': mejor['partido'],
                        'selection': mejor['opcion'],
                        'prob': mejor['probabilidad'],
                        'odd': odd_estimada,
                        'category': mejor['categoria']
                    })
                
                # Calcular parlay
                if len(parlay_picks) >= 2:
                    prob_parlay = np.prod([p['prob'] for p in parlay_picks])
                    odds_parlay = np.prod([p['odd'] for p in parlay_picks])
                    ev_parlay = (prob_parlay * odds_parlay) - 1
                    
                    with st.container(border=True):
                        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                        with col_r1:
                            st.metric("Partidos", len(parlay_picks))
                        with col_r2:
                            st.metric("Probabilidad total", f"{prob_parlay:.1%}")
                        with col_r3:
                            st.metric("Cuota total", f"{odds_parlay:.2f}")
                        with col_r4:
                            color_ev = "normal" if ev_parlay > 0 else "inverse"
                            st.metric("EV total", f"{ev_parlay:.2%}", delta_color=color_ev)
                        
                        st.markdown("**Selecciones del parlay:**")
                        for pick in parlay_picks:
                            st.markdown(f"• **{pick['match']}**: {pick['selection']} ({pick['prob']:.1%})")
                        
                        if st.button("📝 Registrar este parlay (mejores opciones)"):
                            components['tracker'].add_bet({
                                'matches': [f"{p['match']}: {p['selection']}" for p in parlay_picks],
                                'total_odds': odds_parlay,
                                'total_prob': prob_parlay
                            }, stake=100)
                            st.success("✅ Parlay registrado!")
                            st.rerun()
                else:
                    st.info("Se necesitan al menos 2 partidos para formar un parlay")
            
            # ============================================================================
            # PARLAY TRADICIONAL Y OPTIMIZADO
            # ============================================================================
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
                
                # PARLAY OPTIMIZADO
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
                                st.metric("EV Total", f"{ev_opt:.2%}")
                            
                            st.markdown("**Selecciones:**")
                            for p in optimal['picks']:
                                if p.get('ev', 0) > high_value_threshold:
                                    color = '🔴🔴'
                                elif p.get('ev', 0) > value_threshold:
                                    color = '🟢'
                                else:
                                    color = '🟡'
                                
                                stake_kelly = components['value_detector'].calculate_kelly_stake(
                                    p['prob'], p['odd'], bankroll
                                )
                                
                                st.markdown(
                                    f"{color} **{p['match']}**: {p['selection']} "
                                    f"({p['prob']:.1%}) [EV: {p.get('ev', 0):.2%}] "
                                    f"💰 Stake: ${stake_kelly:.2f}"
                                )
                            
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
        
        else:
            st.error("❌ No se detectaron partidos")
            if raw_text:
                st.code(raw_text)
    
    else:
        st.info("👆 Sube una imagen para comenzar el análisis profesional")

if __name__ == "__main__":
    main()