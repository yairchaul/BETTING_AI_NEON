"""
Motor de reglas - 7 REGLAS JERÁRQUICAS para selección de picks
"""
import math

class RuleEngine:
    """Aplica las 7 reglas y determina qué apostar"""
    
    def aplicar_reglas(self, probs, partido):
        """
        Aplica las 7 reglas y retorna el pick recomendado
        """
        picks = []
        
        # Extraer probabilidades
        prob_local = probs.get('prob_local', 0)
        prob_empate = probs.get('prob_empate', 0)
        prob_visit = probs.get('prob_visit', 0)
        over_15 = probs.get('over_1_5', 0)
        over_25 = probs.get('over_2_5', 0)
        over_35 = probs.get('over_3_5', 0)
        over_15_1t = probs.get('over_1_5_1t', 0)
        btts_si = probs.get('btts_si', 0)
        
        # ============================================
        # REGLA 1: Over 1.5 Primer Tiempo > 60%
        # ============================================
        if over_15_1t > 0.60:
            cuota = self._prob_to_odds(over_15_1t)
            value = (over_15_1t * cuota) - 1
            return {
                'regla': 1,
                'descripcion': f"⚽ OVER 1.5 PRIMER TIEMPO ({partido['local']} vs {partido['visitante']})",
                'probabilidad': over_15_1t,
                'cuota_decimal': cuota,
                'cuota_americana': self._decimal_to_american(cuota),
                'value': value,
                'confianza': 'ALTA' if value > 0.1 else 'MEDIA'
            }
        
        # ============================================
        # REGLA 2: Over 3.5 + Favorito claro
        # ============================================
        if over_35 > 0.60:
            if prob_local > 0.55:
                # Combinado: local gana + over 3.5
                prob_combo = prob_local * over_35
                cuota_combo = partido['odds_local'] * self._prob_to_odds(over_35)
                value = (prob_combo * cuota_combo) - 1
                return {
                    'regla': 2,
                    'descripcion': f"🎯 {partido['local']} GANA + OVER 3.5",
                    'probabilidad': prob_combo,
                    'cuota_decimal': cuota_combo,
                    'cuota_americana': self._decimal_to_american(cuota_combo),
                    'value': value,
                    'confianza': 'ALTA' if value > 0.1 else 'MEDIA'
                }
            elif prob_visit > 0.55:
                prob_combo = prob_visit * over_35
                cuota_combo = partido['odds_visitante'] * self._prob_to_odds(over_35)
                value = (prob_combo * cuota_combo) - 1
                return {
                    'regla': 2,
                    'descripcion': f"🎯 {partido['visitante']} GANA + OVER 3.5",
                    'probabilidad': prob_combo,
                    'cuota_decimal': cuota_combo,
                    'cuota_americana': self._decimal_to_american(cuota_combo),
                    'value': value,
                    'confianza': 'ALTA' if value > 0.1 else 'MEDIA'
                }
        
        # ============================================
        # REGLA 3: BTTS > 60%
        # ============================================
        if btts_si > 0.60:
            cuota = self._prob_to_odds(btts_si)
            value = (btts_si * cuota) - 1
            return {
                'regla': 3,
                'descripcion': f"🤝 AMBOS ANOTAN ({partido['local']} vs {partido['visitante']})",
                'probabilidad': btts_si,
                'cuota_decimal': cuota,
                'cuota_americana': self._decimal_to_american(cuota),
                'value': value,
                'confianza': 'ALTA' if value > 0.1 else 'MEDIA'
            }
        
        # ============================================
        # REGLA 4: Partido equilibrado → mejor over cercano a 55%
        # ============================================
        if prob_local < 0.55 and prob_visit < 0.55:
            overs = [
                ('OVER 1.5', over_15),
                ('OVER 2.5', over_25),
                ('OVER 3.5', over_35)
            ]
            # Filtrar overs con prob > 0.50
            overs_validos = [(n, p) for n, p in overs if p > 0.50]
            
            if overs_validos:
                # Elegir el MÁS CERCANO a 55%
                mejor = min(overs_validos, key=lambda x: abs(x[1] - 0.55))
                cuota = self._prob_to_odds(mejor[1])
                value = (mejor[1] * cuota) - 1
                return {
                    'regla': 4,
                    'descripcion': f"⚽ {mejor[0]} (VALOR ÓPTIMO)",
                    'probabilidad': mejor[1],
                    'cuota_decimal': cuota,
                    'cuota_americana': self._decimal_to_american(cuota),
                    'value': value,
                    'confianza': 'MEDIA'
                }
        
        # ============================================
        # REGLA 5: Favorito local + mejor over
        # ============================================
        if prob_local > 0.50 and prob_visit < 0.40:
            # Mejor over (el de mayor probabilidad)
            overs = [
                ('OVER 1.5', over_15),
                ('OVER 2.5', over_25),
                ('OVER 3.5', over_35)
            ]
            mejor = max(overs, key=lambda x: x[1])
            prob_combo = prob_local * mejor[1]
            cuota_combo = partido['odds_local'] * self._prob_to_odds(mejor[1])
            value = (prob_combo * cuota_combo) - 1
            return {
                'regla': 5,
                'descripcion': f"🏠 {partido['local']} GANA + {mejor[0]}",
                'probabilidad': prob_combo,
                'cuota_decimal': cuota_combo,
                'cuota_americana': self._decimal_to_american(cuota_combo),
                'value': value,
                'confianza': 'MEDIA'
            }
        
        # ============================================
        # REGLA 6: Favorito visitante + mejor over
        # ============================================
        if prob_visit > 0.50 and prob_local < 0.40:
            overs = [
                ('OVER 1.5', over_15),
                ('OVER 2.5', over_25),
                ('OVER 3.5', over_35)
            ]
            mejor = max(overs, key=lambda x: x[1])
            prob_combo = prob_visit * mejor[1]
            cuota_combo = partido['odds_visitante'] * self._prob_to_odds(mejor[1])
            value = (prob_combo * cuota_combo) - 1
            return {
                'regla': 6,
                'descripcion': f"🚀 {partido['visitante']} GANA + {mejor[0]}",
                'probabilidad': prob_combo,
                'cuota_decimal': cuota_combo,
                'cuota_americana': self._decimal_to_american(cuota_combo),
                'value': value,
                'confianza': 'MEDIA'
            }
        
        # ============================================
        # REGLA 7: Default → mejor over
        # ============================================
        overs = [
            ('OVER 1.5', over_15),
            ('OVER 2.5', over_25),
            ('OVER 3.5', over_35)
        ]
        mejor = max(overs, key=lambda x: x[1])
        cuota = self._prob_to_odds(mejor[1])
        value = (mejor[1] * cuota) - 1
        return {
            'regla': 7,
            'descripcion': f"⚽ {mejor[0]} (DEFAULT)",
            'probabilidad': mejor[1],
            'cuota_decimal': cuota,
            'cuota_americana': self._decimal_to_american(cuota),
            'value': value,
            'confianza': 'BAJA' if value < 0 else 'MEDIA'
        }
    
    def _prob_to_odds(self, prob):
        """Convierte probabilidad a cuota decimal (con overround)"""
        if prob <= 0:
            return 2.0
        return round(1 / prob * 0.95, 2)
    
    def _decimal_to_american(self, decimal):
        """Convierte cuota decimal a americana"""
        if decimal <= 1:
            return "N/A"
        if decimal >= 2:
            return f"+{int((decimal - 1) * 100)}"
        else:
            return f"-{int(100 / (decimal - 1))}"
