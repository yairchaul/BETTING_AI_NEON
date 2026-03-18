"""
ANALIZADOR PREMIUM - Edge Rating, Public Money, Sharps Action
"""
import streamlit as st

class AnalizadorPremium:
    def __init__(self):
        print("✅ Analizador Premium inicializado")
    
    def analizar(self, partido, resultado_heurístico):
        """
        Genera análisis premium basado en datos del partido
        """
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        odds = partido.get('odds', {})
        records = partido.get('records', {})
        
        # Extraer récords
        try:
            record_local = records.get('local', '0-0').split('-')
            record_visit = records.get('visitante', '0-0').split('-')
            wins_local = int(record_local[0]) if len(record_local) > 0 else 0
            wins_visit = int(record_visit[0]) if len(record_visit) > 0 else 0
            total_local = wins_local + (int(record_local[1]) if len(record_local) > 1 else 0)
            total_visit = wins_visit + (int(record_visit[1]) if len(record_visit) > 1 else 0)
            
            pct_local = (wins_local / total_local * 100) if total_local > 0 else 50
            pct_visit = (wins_visit / total_visit * 100) if total_visit > 0 else 50
        except:
            pct_local = 50
            pct_visit = 50
            wins_local = 0
            wins_visit = 0
        
        # Calcular Edge Rating (0-10)
        diff = pct_local - pct_visit
        
        if diff > 15:
            edge = 9.0
        elif diff > 10:
            edge = 8.0
        elif diff > 5:
            edge = 7.0
        elif diff > 2:
            edge = 6.0
        elif diff > -2:
            edge = 5.0
        elif diff > -5:
            edge = 4.0
        elif diff > -10:
            edge = 3.0
        else:
            edge = 2.0
        
        # Ajustar por spread
        spread = odds.get('spread', {}).get('valor', 0)
        if spread < 0 and pct_local > 50:
            edge += 1.0
        elif spread > 0 and pct_visit > 50:
            edge += 1.0
        
        edge = min(10, max(1, round(edge, 1)))
        
        # Public Money (basado en odds)
        ml_local = odds.get('moneyline', {}).get('local', '-110')
        try:
            ml_value = int(ml_local)
            if ml_value < 0:
                public_money = 64  # Favorito
                public_team = local
            else:
                public_money = 36  # Underdog
                public_team = visitante
        except:
            public_money = 50
            public_team = local if pct_local > pct_visit else visitante
        
        # Sharps Action (dinero inteligente)
        if edge >= 8:
            sharps = f"Strong on {local}"
        elif edge <= 3:
            sharps = f"Strong on {visitante}"
        else:
            sharps = "Split action"
        
        return {
            'edge_rating': edge,
            'public_money': public_money,
            'public_team': public_team,
            'sharps_action': sharps,
            'recomendacion': resultado_heurístico.get('apuesta', 'N/A'),
            'confianza': resultado_heurístico.get('confianza', 0)
        }
