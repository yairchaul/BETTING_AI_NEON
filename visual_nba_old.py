import streamlit as st
import pandas as pd

class VisualNBA:
    def render(self, evento, idx, tracker):
        """Renderiza NBA con formato de tabla profesional"""
        with st.expander(f"**🏀 {evento.local} vs {evento.visitante}**", expanded=(idx == 0)):
            # Extraer datos del evento
            home_spread = evento.datos_crudos.get('home_spread', 'N/A')
            home_spread_odds = evento.datos_crudos.get('home_spread_odds', 'N/A')
            home_ou = evento.datos_crudos.get('home_ou', 'O')
            home_total = evento.datos_crudos.get('home_total', 'N/A')
            home_total_odds = evento.datos_crudos.get('home_total_odds', 'N/A')
            home_ml = evento.datos_crudos.get('home_ml', 'N/A')
            away_ml = evento.datos_crudos.get('away_ml', 'N/A')
            
            # Tabla principal
            data = {
                '': ['LOCAL', 'VISITANTE'],
                'EQUIPO': [evento.local, evento.visitante],
                'SPREAD': [f"{home_spread} ({home_spread_odds})", f"{home_spread} ({home_spread_odds})"],
                'TOTAL': [f"{home_ou} {home_total} ({home_total_odds})", f"{home_ou} {home_total} ({home_total_odds})"],
                'MONEYLINE': [home_ml, away_ml]
            }
            df = pd.DataFrame(data)
            st.table(df.set_index(''))
            
            # Probabilidades calculadas
            st.markdown("**📊 PROBABILIDADES CALCULADAS**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cubrir Spread", f"{evento.mercados.get('prob_spread', 0):.1%}")
            with col2:
                st.metric("Over", f"{evento.mercados.get('prob_over', 0):.1%}")
            with col3:
                st.metric("Under", f"{evento.mercados.get('prob_under', 0):.1%}")
            
            col4, col5 = st.columns(2)
            with col4:
                st.metric(f"Gana {evento.local}", f"{evento.mercados.get('prob_home_ml', 0):.1%}")
            with col5:
                st.metric(f"Gana {evento.visitante}", f"{evento.mercados.get('prob_away_ml', 0):.1%}")
            
            # Picks NBA
            from rule_engine import RuleEngine
            rule_engine = RuleEngine()
            picks = rule_engine.ejecutar(evento)
            
            if picks:
                st.markdown("**🎯 PICKS SEGÚN REGLAS NBA:**")
                for pick in picks:
                    st.info(f"Nivel {pick['nivel']}: **{pick['mercado']}** ({pick['prob']:.1%})")
                    if st.button(f"➕ Agregar", key=f"add_nba_{idx}_{pick['nivel']}"):
                        tracker.add_pick(
                            f"{evento.local} vs {evento.visitante}",
                            pick['mercado'],
                            pick['prob'],
                            pick['nivel'],
                            evento.deporte
                        )
                        st.rerun()
