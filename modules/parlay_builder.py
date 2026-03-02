# modules/parlay_builder.py
import streamlit as st
from itertools import combinations

def build_parlay(picks):
    """Construye un parlay a partir de picks"""
    if len(picks) < 2:
        return None
    
    total_prob = 1.0
    matches_list = []
    for p in picks:
        total_prob *= p['prob']
        matches_list.append(f"{p['match']}: {p['selection']}")
    
    # Cuota estimada (inversa de probabilidad con margen 5%)
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

def show_parlay_options(all_picks, tracker):
    """Muestra interfaz de parlays con opción de registrar"""
    st.divider()
    st.subheader("🎯 Parlays Recomendados")
    
    if len(all_picks) < 2:
        st.info("Se necesitan al menos 2 selecciones para generar parlays")
        return
    
    # Mostrar picks disponibles
    st.markdown("**Selecciones disponibles:**")
    cols = st.columns(3)
    for i, pick in enumerate(all_picks[:6]):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{pick['match']}**")
                st.markdown(f"📌 {pick['selection']}")
                st.metric("Prob", f"{pick['prob']:.1%}")
    
    # Botón para generar combinaciones
    if st.button("🔄 Generar combinaciones"):
        parlays = []
        
        # Generar parlays de 2 y 3 selecciones
        for size in [2, 3]:
            for combo in combinations(all_picks, size):
                parlay = build_parlay(list(combo))
                if parlay and parlay['ev'] > 0.05:  # EV mínimo 5%
                    parlays.append(parlay)
        
        # Ordenar por EV
        parlays.sort(key=lambda x: x['ev'], reverse=True)
        
        if parlays:
            st.markdown("**Top parlays encontrados:**")
            for i, p in enumerate(parlays[:5]):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.markdown(f"**Parlay #{i+1}**")
                        for m in p['matches']:
                            st.caption(f"• {m[:50]}...")
                    with col2:
                        st.metric("Cuota", p['total_odds'])
                    with col3:
                        st.metric("Prob", f"{p['total_prob']:.1%}")
                    with col4:
                        ev_color = "normal" if p['ev'] > 0 else "off"
                        st.metric("EV", f"{p['ev']:.2%}", delta_color=ev_color)
                        
                        if st.button(f"📝 Registrar #{i+1}", key=f"reg_{i}"):
                            bet = tracker.add_bet(p, stake=100)
                            st.success(f"✅ Apuesta #{bet['id']} registrada!")
                            st.rerun()
        else:
            st.info("No se encontraron parlays con EV positivo")
