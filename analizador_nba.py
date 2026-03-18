"""
ANALIZADOR NBA - CORREGIDO CON MANEJO DE NONE
"""
import streamlit as st

class AnalizadorNBA:
    def __init__(self, partido):
        """
        Args:
            partido: Diccionario con datos del partido
        """
        self.partido = partido
        self.local = partido.get('local', '')
        self.visitante = partido.get('visitante', '')
        self.odds = partido.get('odds', {})
        self.records = partido.get('records', {})
        
        # Si no hay records, usar valores por defecto
        self.record_local = self._parse_record(self.records.get('local', '0-0'))
        self.record_visit = self._parse_record(self.records.get('visitante', '0-0'))
    
    def _parse_record(self, record_str):
        """Convierte string '45-23' a dict con wins y losses"""
        try:
            parts = record_str.split('-')
            if len(parts) >= 2:
                return {'wins': int(parts[0]), 'losses': int(parts[1])}
        except:
            pass
        return {'wins': 0, 'losses': 0}
    
    def _calcular_win_rate(self, record):
        """Calcula porcentaje de victorias"""
        total = record['wins'] + record['losses']
        if total == 0:
            return 50
        return (record['wins'] / total) * 100
    
    def _calcular_probabilidad_handicap(self):
        """
        REGLA 1: Handicap con contexto de favorito/underdog
        """
        spread = self.odds.get('spread', {}).get('valor', 0)
        
        # Determinar si local es favorito (spread negativo)
        local_favorito = spread < 0
        
        # Obtener win rates
        win_rate_local = self._calcular_win_rate(self.record_local)
        win_rate_visit = self._calcular_win_rate(self.record_visit)
        
        # Factor de favorito/underdog
        if local_favorito:
            probabilidad_base = win_rate_local
            if win_rate_local > 60:
                probabilidad_base += 10
        else:
            probabilidad_base = win_rate_visit
            if win_rate_visit > 60:
                probabilidad_base += 10
        
        return min(probabilidad_base, 95)
    
    def _calcular_probabilidad_totales(self):
        """
        REGLA 2: Over/Under simplificado
        """
        # Por ahora, basado solo en win rates
        win_rate_local = self._calcular_win_rate(self.record_local)
        win_rate_visit = self._calcular_win_rate(self.record_visit)
        
        # Promedio simple
        prob_over_base = (win_rate_local + win_rate_visit) / 2
        prob_under_base = 100 - prob_over_base
        
        return {
            'over': min(prob_over_base, 90),
            'under': min(prob_under_base, 90)
        }
    
    def _calcular_probabilidad_moneyline(self):
        """
        REGLA 3: Moneyline basado en win rates
        """
        win_rate_local = self._calcular_win_rate(self.record_local)
        win_rate_visit = self._calcular_win_rate(self.record_visit)
        
        # Ventaja local: +5 puntos
        prob_local = win_rate_local + 5
        prob_visit = win_rate_visit
        
        total = prob_local + prob_visit
        if total > 0:
            prob_local = (prob_local / total) * 100
            prob_visit = (prob_visit / total) * 100
        else:
            prob_local = 50
            prob_visit = 50
        
        return {
            'local': min(prob_local, 90),
            'visitante': min(prob_visit, 90)
        }
    
    def analizar(self):
        """
        Ejecuta la jerarquía de reglas y devuelve la mejor apuesta
        """
        resultados = []
        
        # REGLA 1: Handicap
        prob_handicap = self._calcular_probabilidad_handicap()
        if prob_handicap >= 60:
            spread = self.odds.get('spread', {}).get('valor', 0)
            if spread < 0:
                equipo = self.local
            else:
                equipo = self.visitante
            resultados.append({
                'tipo': 'HANDICAP',
                'apuesta': f"HANDICAP {equipo}",
                'confianza': round(prob_handicap, 1),
                'detalle': f"Basado en win rate ({self._calcular_win_rate(self.record_local):.0f}%)",
                'regla': 1,
                'color': 'green'
            })
        
        # REGLA 2: Totales
        prob_totales = self._calcular_probabilidad_totales()
        if prob_totales['over'] >= 60:
            linea = self.odds.get('totales', {}).get('linea', 0)
            resultados.append({
                'tipo': 'OVER',
                'apuesta': f"OVER {linea}",
                'confianza': round(prob_totales['over'], 1),
                'detalle': f"Basado en promedio de equipos",
                'regla': 2,
                'color': 'green'
            })
        elif prob_totales['under'] >= 60:
            linea = self.odds.get('totales', {}).get('linea', 0)
            resultados.append({
                'tipo': 'UNDER',
                'apuesta': f"UNDER {linea}",
                'confianza': round(prob_totales['under'], 1),
                'detalle': f"Basado en promedio de equipos",
                'regla': 2,
                'color': 'green'
            })
        
        # REGLA 3: Moneyline
        prob_ml = self._calcular_probabilidad_moneyline()
        if prob_ml['local'] >= 55:
            resultados.append({
                'tipo': 'MONEYLINE',
                'apuesta': f"GANA {self.local}",
                'confianza': round(prob_ml['local'], 1),
                'detalle': f"Win rate superior ({self._calcular_win_rate(self.record_local):.0f}%)",
                'regla': 3,
                'color': 'blue'
            })
        elif prob_ml['visitante'] >= 55:
            resultados.append({
                'tipo': 'MONEYLINE',
                'apuesta': f"GANA {self.visitante}",
                'confianza': round(prob_ml['visitante'], 1),
                'detalle': f"Win rate superior ({self._calcular_win_rate(self.record_visit):.0f}%)",
                'regla': 3,
                'color': 'blue'
            })
        
        # Si no hay recomendaciones
        if not resultados:
            return {
                'apuesta': '❌ NO OPERABLE',
                'confianza': 0,
                'detalle': 'No se encontraron apuestas con suficiente confianza',
                'regla': 0,
                'color': 'red'
            }
        
        # Devolver la mejor opción
        return resultados[0]
    
    def obtener_resumen(self):
        """Resumen de estadísticas"""
        return {
            'win_rate_local': round(self._calcular_win_rate(self.record_local), 1),
            'win_rate_visit': round(self._calcular_win_rate(self.record_visit), 1)
        }
