import streamlit as st
from itertools import combinations
from .betting_tracker import BettingTracker

def build_parlay(picks):
    """Construye un parlay a partir de picks"""
    if len(picks) < 2:
        return None
    
    total_prob = 1.0
    matches_list = []
    for p in picks:
        total_prob *= p['prob']
        matches_list.append(f"{p['match']}: {p['selection']}")
    
    # Cuota estimada (inversa de probabilidad con margen)
    total_odds = 1.0
    for p in picks:
        total_odds *= (1 / p['prob']) * 0.95
    
    ev = (total_prob * total_odds) - 1
    
    return {
        'matches': matches_list,
        'picks': picks,
        'total_prob': total_prob,
        'total_odds': round(total_odds, 2),
        'ev': round(ev, 4)
    }

def show_parlay_options(all_picks):
    """Muestra interfaz de parlays con opción de registrar"""
    st.divider()
    st.subheader("🎯 Parlays Recomendados")
    
    # Inicializar tracker
    if 'tracker' not in st.session_state:
        st.session_state.tracker = BettingTracker()
    
    # Mostrar picks disponibles
    st.markdown("**Selecciones disponibles:**")
    cols = st.columns(3)
    for i, pick in enumerate(all_picks[:6]):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{pick['match']}**")
                st.markdown(f"📌 {pick['selection']}")
                st.metric("Probabilidad", f"{pick['prob']:.1%}")
    
    if st.button("🔄 Generar combinaciones"):
        parlays = []
        for combo in combinations(all_picks, 2):
            parlay = build_parlay(list(combo))
            if parlay and parlay['ev'] > 0:
                parlays.append(parlay)
        
        if parlays:
            st.markdown("**Top parlays encontrados:**")
            for i, p in enumerate(parlays[:5]):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**Parlay #{i+1}**")
                        for m in p['matches']:
                            st.markdown(f"• {m}")
                    with col2:
                        st.metric("Cuota", p['total_odds'])
                        st.metric("Prob", f"{p['total_prob']:.1%}")
                    with col3:
                        st.metric("EV", f"{p['ev']:.2%}")
                        if st.button(f"📝 Registrar", key=f"reg_{i}"):
                            bet = st.session_state.tracker.add_bet(p, stake=100)
                            st.success(f"✅ Apuesta #{bet['id']} registrada!")
                            st.rerun()
        else:
            st.info("No se encontraron parlays con EV positivo")
    
    # Mostrar tracker en sidebar
    st.session_state.tracker.show_tracker_ui()
