"""
ANALIZADOR UFC HEURÍSTICO - Usa datos históricos REALES del dataset
"""
import streamlit as st
import numpy as np

class AnalizadorUFCHuristico:
    def __init__(self, fighter1_data, fighter2_data):
        self.f1 = fighter1_data
        self.f2 = fighter2_data
    
    def _get_win_rate(self, record_dict):
        """Calcula win rate del récord"""
        total = record_dict['wins'] + record_dict['losses']
        if total == 0:
            return 50
        return (record_dict['wins'] / total) * 100
    
    def _get_experience_factor(self, record_dict):
        """Factor de experiencia basado en número de peleas"""
        total_peleas = record_dict['wins'] + record_dict['losses']
        factor = 0.8 + (total_peleas / 50)  # Ajustado para UFC (max ~30 peleas)
        return min(1.2, factor)
    
    def _get_ko_percentage(self, historial):
        """Calcula % de victorias por KO basado en HISTORIAL REAL"""
        if not historial:
            return 33
        
        total_victorias = 0
        ko_victorias = 0
        
        for pelea in historial:
            if pelea.get('resultado') == 'Victoria':
                total_victorias += 1
                metodo = str(pelea.get('metodo', '')).upper()
                if 'KO' in metodo or 'TKO' in metodo:
                    ko_victorias += 1
        
        if total_victorias == 0:
            return 0
        
        return (ko_victorias / total_victorias) * 100
    
    def _get_submission_percentage(self, historial):
        """Calcula % de victorias por sumisión basado en HISTORIAL REAL"""
        if not historial:
            return 33
        
        total_victorias = 0
        sub_victorias = 0
        
        for pelea in historial:
            if pelea.get('resultado') == 'Victoria':
                total_victorias += 1
                metodo = str(pelea.get('metodo', '')).upper()
                if 'SUBMISSION' in metodo:
                    sub_victorias += 1
        
        if total_victorias == 0:
            return 0
        
        return (sub_victorias / total_victorias) * 100
    
    def _get_recent_form(self, historial, n=3):
        """Calcula forma reciente basado en últimas N peleas REALES"""
        if not historial:
            return 50
        
        recientes = historial[:n]
        victorias = sum(1 for p in recientes if p.get('resultado') == 'Victoria')
        
        return (victorias / len(recientes)) * 100
    
    def _get_striking_stats(self, advanced_stats):
        """Obtiene estadísticas de golpeo"""
        if not advanced_stats:
            return {'sig_str_per_fight': 0, 'sig_str_acc': 0}
        
        return {
            'sig_str_per_fight': advanced_stats.get('sig_str_landed_per_fight', 0),
            'sig_str_acc': advanced_stats.get('sig_str_acc', 0)
        }
    
    def _get_wrestling_stats(self, advanced_stats):
        """Obtiene estadísticas de lucha"""
        if not advanced_stats:
            return {'td_per_fight': 0, 'td_acc': 0}
        
        return {
            'td_per_fight': advanced_stats.get('td_landed_per_fight', 0),
            'td_acc': advanced_stats.get('td_acc', 0)
        }
    
    def _get_ko_tendency(self, historial, advanced_stats):
        """Combina historial y estadísticas para tendencia KO"""
        ko_pct_historial = self._get_ko_percentage(historial)
        kd_per_fight = advanced_stats.get('kd_per_fight', 0) if advanced_stats else 0
        
        # Ponderado: 70% historial, 30% KD por pelea
        return (ko_pct_historial * 0.7) + (kd_per_fight * 20 * 0.3)
    
    def _get_decision_tendency(self, historial):
        """Calcula tendencia a ir a decisión"""
        if not historial:
            return 50
        
        total_peleas = len(historial)
        decisiones = 0
        
        for pelea in historial:
            metodo = str(pelea.get('metodo', '')).upper()
            if 'DECISION' in metodo:
                decisiones += 1
        
        return (decisiones / total_peleas) * 100
    
    def analizar(self):
        """
        Análisis usando datos HISTÓRICOS REALES
        """
        # Obtener datos
        record1 = self.f1.get('record_dict', {'wins': 0, 'losses': 0, 'draws': 0})
        record2 = self.f2.get('record_dict', {'wins': 0, 'losses': 0, 'draws': 0})
        
        historial1 = self.f1.get('historial', [])
        historial2 = self.f2.get('historial', [])
        
        adv1 = self.f1.get('advanced_stats', {})
        adv2 = self.f2.get('advanced_stats', {})
        
        win_stats1 = self.f1.get('win_stats', {})
        win_stats2 = self.f2.get('win_stats', {})
        
        # Factores calculados con datos REALES
        wr1 = self._get_win_rate(record1)
        wr2 = self._get_win_rate(record2)
        
        exp1 = self._get_experience_factor(record1)
        exp2 = self._get_experience_factor(record2)
        
        form1 = self._get_recent_form(historial1)
        form2 = self._get_recent_form(historial2)
        
        ko_tend1 = self._get_ko_tendency(historial1, adv1)
        ko_tend2 = self._get_ko_tendency(historial2, adv2)
        
        dec_tend1 = self._get_decision_tendency(historial1)
        dec_tend2 = self._get_decision_tendency(historial2)
        
        # Estadísticas de pelea
        strike1 = self._get_striking_stats(adv1)
        strike2 = self._get_striking_stats(adv2)
        
        wrestle1 = self._get_wrestling_stats(adv1)
        wrestle2 = self._get_wrestling_stats(adv2)
        
        # SCORE COMPUESTO (basado en importancia de cada factor)
        score1 = (
            wr1 * 0.20 +              # Win rate histórico
            form1 * 0.25 +             # Forma reciente (más importante)
            exp1 * 15 +                 # Experiencia
            strike1['sig_str_per_fight'] * 0.5 +  # Producción de golpes
            strike1['sig_str_acc'] * 0.3 +        # Precisión
            wrestle1['td_per_fight'] * 2 +         # Derribos por pelea
            wrestle1['td_acc'] * 0.2               # Precisión derribos
        )
        
        score2 = (
            wr2 * 0.20 +
            form2 * 0.25 +
            exp2 * 15 +
            strike2['sig_str_per_fight'] * 0.5 +
            strike2['sig_str_acc'] * 0.3 +
            wrestle2['td_per_fight'] * 2 +
            wrestle2['td_acc'] * 0.2
        )
        
        total = score1 + score2
        prob1 = (score1 / total) * 100 if total > 0 else 50
        prob2 = (score2 / total) * 100 if total > 0 else 50
        
        # Determinar ganador
        if prob1 > prob2 + 12:
            ganador = self.f1.get('nombre', 'Peleador 1')
            confianza = 70
            color = 'green'
        elif prob2 > prob1 + 12:
            ganador = self.f2.get('nombre', 'Peleador 2')
            confianza = 70
            color = 'green'
        elif prob1 > prob2 + 5:
            ganador = self.f1.get('nombre')
            confianza = 60
            color = 'orange'
        elif prob2 > prob1 + 5:
            ganador = self.f2.get('nombre')
            confianza = 60
            color = 'orange'
        else:
            ganador = self.f1.get('nombre') if prob1 > prob2 else self.f2.get('nombre')
            confianza = 55
            color = 'yellow'
        
        # Determinar método más probable
        if ko_tend1 > 50 or ko_tend2 > 50:
            if ko_tend1 > ko_tend2 + 20:
                metodo = f"KO/TKO por {self.f1.get('nombre')}"
                prob_metodo = ko_tend1
            elif ko_tend2 > ko_tend1 + 20:
                metodo = f"KO/TKO por {self.f2.get('nombre')}"
                prob_metodo = ko_tend2
            else:
                metodo = "KO/TKO"
                prob_metodo = max(ko_tend1, ko_tend2)
        elif dec_tend1 > 70 or dec_tend2 > 70:
            metodo = "Decisión"
            prob_metodo = max(dec_tend1, dec_tend2)
        else:
            metodo = "Decisión"
            prob_metodo = 55
        
        return {
            'apuesta': f"🥊 GANA {ganador}",
            'confianza': confianza,
            'metodo': metodo,
            'prob_metodo': round(prob_metodo, 1),
            'detalle': (
                f"WR: {wr1:.0f}% vs {wr2:.0f}% | "
                f"Forma: {form1:.0f}% vs {form2:.0f}% | "
                f"KO%: {ko_tend1:.0f}% vs {ko_tend2:.0f}%"
            ),
            'prob1': round(prob1, 1),
            'prob2': round(prob2, 1),
            'color': color,
            'stats_detalle': {
                'win_rates': {'f1': round(wr1, 1), 'f2': round(wr2, 1)},
                'forma_reciente': {'f1': round(form1, 1), 'f2': round(form2, 1)},
                'ko_tendency': {'f1': round(ko_tend1, 1), 'f2': round(ko_tend2, 1)},
                'striking': {'f1': round(strike1['sig_str_per_fight'], 1), 
                            'f2': round(strike2['sig_str_per_fight'], 1)},
                'wrestling': {'f1': round(wrestle1['td_per_fight'], 2), 
                             'f2': round(wrestle2['td_per_fight'], 2)}
            }
        }
    
    def obtener_resumen(self):
        """Resumen para Gemini"""
        record1 = self.f1.get('record_dict', {'wins': 0, 'losses': 0})
        record2 = self.f2.get('record_dict', {'wins': 0, 'losses': 0})
        
        historial1 = self.f1.get('historial', [])
        historial2 = self.f2.get('historial', [])
        
        wr1 = self._get_win_rate(record1)
        wr2 = self._get_win_rate(record2)
        
        form1 = self._get_recent_form(historial1)
        form2 = self._get_recent_form(historial2)
        
        ko1 = self._get_ko_percentage(historial1)
        ko2 = self._get_ko_percentage(historial2)
        
        return {
            'f1_nombre': self.f1.get('nombre', ''),
            'f1_record': self.f1.get('record', '0-0-0'),
            'f1_winrate': round(wr1, 1),
            'f1_forma_reciente': round(form1, 1),
            'f1_ko_pct': round(ko1, 1),
            'f1_altura': self.f1.get('altura', 'N/A'),
            'f1_peso': self.f1.get('peso', 'N/A'),
            'f1_alcance': self.f1.get('alcance', 'N/A'),
            'f1_postura': self.f1.get('postura', 'Desconocida'),
            'f2_nombre': self.f2.get('nombre', ''),
            'f2_record': self.f2.get('record', '0-0-0'),
            'f2_winrate': round(wr2, 1),
            'f2_forma_reciente': round(form2, 1),
            'f2_ko_pct': round(ko2, 1),
            'f2_altura': self.f2.get('altura', 'N/A'),
            'f2_peso': self.f2.get('peso', 'N/A'),
            'f2_alcance': self.f2.get('alcance', 'N/A'),
            'f2_postura': self.f2.get('postura', 'Desconocida')
        }
