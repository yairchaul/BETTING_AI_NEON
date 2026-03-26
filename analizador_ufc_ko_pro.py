"""
ANALIZADOR UFC KO PRO - Análisis de probabilidad de KO
"""
class AnalizadorUFCKOPro:
    def __init__(self):
        pass
    
    def analizar_ko_probability(self, p1_data, p2_data):
        """Analiza probabilidad de KO con filtro de grappling"""
        
        ko_rate1 = p1_data.get('ko_rate', 0.5)
        ko_rate2 = p2_data.get('ko_rate', 0.5)
        grappling1 = p1_data.get('grappling', 0.5)
        grappling2 = p2_data.get('grappling', 0.5)
        
        # Ajuste por grappling
        ko_ajustado1 = ko_rate1 * (1 - (grappling2 * 0.3))
        ko_ajustado2 = ko_rate2 * (1 - (grappling1 * 0.3))
        
        prob_ko = max(ko_ajustado1, ko_ajustado2) * 100
        
        if ko_ajustado1 > ko_ajustado2 + 0.2:
            recomendacion = f"⚠️ ALERTA KO: {p1_data.get('nombre', 'P1')}"
            confianza = min(85, int(prob_ko + 15))
            etiqueta_verde = confianza >= 75
        elif ko_ajustado2 > ko_ajustado1 + 0.2:
            recomendacion = f"⚠️ ALERTA KO: {p2_data.get('nombre', 'P2')}"
            confianza = min(85, int(prob_ko + 15))
            etiqueta_verde = confianza >= 75
        else:
            recomendacion = "Probabilidad de KO moderada"
            confianza = int(prob_ko)
            etiqueta_verde = False
        
        return {
            'recomendacion': recomendacion,
            'confianza': confianza,
            'probabilidad_ko': prob_ko,
            'etiqueta_verde': etiqueta_verde
        }
    
    def analizar_metodo_victoria(self, p1_data, p2_data):
        """Analiza método de victoria probable"""
        ko_rate1 = p1_data.get('ko_rate', 0.5)
        ko_rate2 = p2_data.get('ko_rate', 0.5)
        
        if max(ko_rate1, ko_rate2) > 0.6:
            return {'metodo': 'KO/TKO', 'confianza': 70}
        return {'metodo': 'Decisión', 'confianza': 60}
