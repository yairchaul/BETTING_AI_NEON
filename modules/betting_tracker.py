# modules/betting_tracker.py
import streamlit as st
import pandas as pd
from datetime import datetime

class BettingTracker:
    def __init__(self):
        """Inicializa el tracker asegurando que exista la variable en session_state"""
        if 'bets' not in st.session_state:
            st.session_state.bets = []
    
    def add_bet(self, parlay_data, stake=100):
        """Registra una nueva apuesta"""
        bet = {
            'id': len(st.session_state.bets) + 1,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'selections': parlay_data['matches'],
            'total_odds': parlay_data['total_odds'],
            'probability': parlay_data['total_prob'],
            'stake': stake,
            'potential_win': round(stake * parlay_data['total_odds'], 2),
            'status': 'Pendiente',
            'result': None,
            'profit': 0
        }
        st.session_state.bets.append(bet)
        return bet
    
    def update_bet_result(self, bet_id, result):
        """Actualiza el resultado de una apuesta"""
        for bet in st.session_state.bets:
            if bet['id'] == bet_id:
                bet['status'] = 'Resuelta'
                bet['result'] = result
                if result == 'Ganada':
                    bet['profit'] = bet['potential_win'] - bet['stake']
                else:
                    bet['profit'] = -bet['stake']
                break
    
    def get_stats(self):
        """Obtiene estadísticas de rendimiento"""
        # Verificar que existe la variable en session_state
        if 'bets' not in st.session_state:
            st.session_state.bets = []
            return {'total_bets': 0, 'won': 0, 'lost': 0, 'pending': 0, 'win_rate': 0, 'total_profit': 0}
        
        bets = st.session_state.bets
        if not bets:
            return {'total_bets': 0, 'won': 0, 'lost': 0, 'pending': 0, 'win_rate': 0, 'total_profit': 0}
        
        total_bets = len(bets)
        won = sum(1 for b in bets if b.get('result') == 'Ganada')
        lost = sum(1 for b in bets if b.get('result') == 'Perdida')
        pending = total_bets - won - lost
        
        total_profit = sum(b.get('profit', 0) for b in bets)
        win_rate = round(won / (won + lost) * 100, 1) if (won + lost) > 0 else 0
        
        return {
            'total_bets': total_bets,
            'won': won,
            'lost': lost,
            'pending': pending,
            'win_rate': win_rate,
            'total_profit': total_profit
        }
    
    def show_tracker_ui(self):
        """Muestra la interfaz del tracker en sidebar"""
        # Verificar inicialización
        if 'bets' not in st.session_state:
            st.session_state.bets = []
            return
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Registro de Apuestas")
        
        stats = self.get_stats()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total", stats['total_bets'])
            st.metric("Ganadas", stats['won'])
        with col2:
            # Color verde si profit positivo, rojo si negativo
            profit_color = "normal" if stats['total_profit'] >= 0 else "inverse"
            st.metric("Profit", f"${stats['total_profit']:,.0f}", delta_color=profit_color)
            st.metric("Win Rate", f"{stats['win_rate']}%")
        
        if stats['pending'] > 0:
            st.sidebar.info(f"⏳ {stats['pending']} pendientes")
        
        # Botón para ver historial completo
        if st.sidebar.button("📜 Ver historial"):
            self.show_history()
    
    def show_history(self):
        """Muestra el historial completo de apuestas"""
        if 'bets' not in st.session_state or not st.session_state.bets:
            st.sidebar.info("No hay apuestas registradas")
            return
        
        # Crear DataFrame para mostrar
        history_data = []
        for bet in reversed(st.session_state.bets[-20:]):  # Últimas 20
            status_emoji = "✅" if bet.get('result') == 'Ganada' else "❌" if bet.get('result') == 'Perdida' else "⏳"
            
            # Acortar selecciones para mostrar
            selections_preview = ", ".join([s[:30] + "..." for s in bet['selections'][:2]])
            if len(bet['selections']) > 2:
                selections_preview += f" +{len(bet['selections'])-2} más"
            
            history_data.append({
                'ID': bet['id'],
                'Fecha': bet['date'][5:16],
                'Estado': status_emoji,
                'Cuota': bet['total_odds'],
                'Profit': f"${bet['profit']:+,.0f}",
                'Selecciones': selections_preview
            })
        
        st.sidebar.dataframe(
            pd.DataFrame(history_data), 
            use_container_width=True,
            hide_index=True
        )
        
        # Botones para actualizar resultados (solo pendientes)
        pending_bets = [b for b in st.session_state.bets if b['status'] == 'Pendiente']
        if pending_bets:
            st.sidebar.markdown("---")
            st.sidebar.caption("📝 Actualizar resultados:")
            
            # Mostrar solo las primeras 3 pendientes para no saturar
            for bet in pending_bets[:3]:
                cols = st.sidebar.columns([2, 1, 1])
                with cols[0]:
                    st.caption(f"#{bet['id']}: {bet['selections'][0][:20]}...")
                with cols[1]:
                    if st.button("✅ Ganada", key=f"win_{bet['id']}"):
                        self.update_bet_result(bet['id'], 'Ganada')
                        st.rerun()
                with cols[2]:
                    if st.button("❌ Perdida", key=f"loss_{bet['id']}"):
                        self.update_bet_result(bet['id'], 'Perdida')
                        st.rerun()
