import streamlit as st
import re
from .models import UFCModelMATUA
from .rules import UFCRules

class UFCProcessor:
    # Procesador específico para UFC con análisis de Moneyline, Método y Rounds
    
    def __init__(self):
        self.model = UFCModelMATUA()
        self.rules = UFCRules()
    
    def parse_ufc_captura(self, lines):
        # Parsea las líneas de captura de UFC
        # Formato: lista alternada de peleador y odds
        peleas = []
        
        i = 0
        while i < len(lines) - 3:
            # Buscar patrón: nombre, odds, nombre, odds
            fighter1 = lines[i]
            odds1 = lines[i + 1]
            fighter2 = lines[i + 2]
            odds2 = lines[i + 3]
            
            # Verificar que los odds tengan formato (+/-) y los nombres no sean números
            if (re.match(r'^[+-]?\d+$', odds1) and 
                re.match(r'^[+-]?\d+$', odds2) and
                not re.match(r'^[+-]?\d+$', fighter1) and
                not re.match(r'^[+-]?\d+$', fighter2)):
                
                peleas.append({
                    'fighter1': fighter1.strip('- '),
                    'fighter2': fighter2.strip('- '),
                    'odds1': int(odds1),
                    'odds2': int(odds2)
                })
                i += 4
            else:
                i += 1
        
        return peleas
    
    def render_fight(self, idx, pelea):
        # Renderiza una pelea UFC en la UI
        with st.expander(f"**🥊 {pelea['fighter1']} vs {pelea['fighter2']}**", expanded=(idx == 0)):
            # Mostrar peleadores y odds
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### 🏠 **{pelea['fighter1']}**")
                st.metric(
                    label="Cuota",
                    value=f"{pelea['odds1']:+d}",
                    delta=self._american_to_decimal(pelea['odds1'])
                )
            with col2:
                st.markdown(f"### 🚀 **{pelea['fighter2']}**")
                st.metric(
                    label="Cuota",
                    value=f"{pelea['odds2']:+d}",
                    delta=self._american_to_decimal(pelea['odds2'])
                )
            
            # Calcular probabilidades con modelo MATUA
            probs = self.model.calculate_fight_probabilities(
                pelea['fighter1'], pelea['fighter2'],
                None, None,
                pelea['odds1'], pelea['odds2']
            )
            
            # Mostrar probabilidades moneyline
            st.subheader("📊 Probabilidades de Victoria")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                prob1 = probs['moneyline']['fighter1_win'] / 10000
                st.metric(
                    f"Gana {pelea['fighter1']}",
                    f"{prob1:.1%}",
                    f"Fair: {probs.get('expected_value', {}).get('fighter1_ev', 0):.1%}"
                )
            with col_p2:
                prob2 = probs['moneyline']['fighter2_win'] / 10000
                st.metric(
                    f"Gana {pelea['fighter2']}",
                    f"{prob2:.1%}",
                    f"Fair: {probs.get('expected_value', {}).get('fighter2_ev', 0):.1%}"
                )
            with col_p3:
                # Mostrar favorito
                favorito = pelea['fighter1'] if pelea['odds1'] < pelea['odds2'] else pelea['fighter2']
                st.metric("Favorito", favorito)
            
            # Métodos de victoria
            st.subheader("🥊 Método de Victoria")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("KO/TKO", f"{probs['method_probs']['ko_tko']:.1%}")
            with col_m2:
                st.metric("Sumisión", f"{probs['method_probs']['submission']:.1%}")
            with col_m3:
                st.metric("Decisión", f"{probs['method_probs']['decision']:.1%}")
            
            # Rounds
            if probs['round_probs']:
                st.subheader("⏱️ Rounds más probables")
                col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                rounds = ['round_1', 'round_2', 'round_3', 'round_4', 'round_5']
                cols = [col_r1, col_r2, col_r3, col_r4, col_r5]
                for i, round_name in enumerate(rounds):
                    with cols[i]:
                        st.metric(
                            f"Round {i+1}",
                            f"{probs['round_probs'][round_name]:.1%}"
                        )
            
            # Aplicar reglas UFC
            picks = self.rules.aplicar_reglas(
                probs,
                pelea['fighter1'],
                pelea['fighter2'],
                pelea['odds1'],
                pelea['odds2']
            )
            
            st.markdown('**🎯 Picks según reglas UFC:**')
            return picks
    
    def _american_to_decimal(self, odds):
        # Convierte odds americanos a decimales
        try:
            odds = int(odds)
            if odds > 0:
                return round(1 + (odds / 100), 2)
            else:
                return round(1 + (100 / abs(odds)), 2)
        except:
            return 2.0
