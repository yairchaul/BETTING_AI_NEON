"""
ANALIZADOR PREMIUM PROFESIONAL - Análisis avanzado con consistencia
"""
class AnalizadorPremiumProfesional:
    def __init__(self):
        pass
    
    def analizar(self, partido, resultado_heur, stats_adicionales=None):
        """Analiza partido con criterios premium"""
        
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        
        recomendacion = resultado_heur.get('recomendacion', '')
        confianza = resultado_heur.get('confianza', 50)
        etiqueta_verde = resultado_heur.get('etiqueta_verde', False)
        consistencia = resultado_heur.get('consistencia', 'N/A')
        
        # Ajuste por consistencia
        if consistencia != 'N/A' and isinstance(consistencia, str) and '%' in consistencia:
            try:
                cons_val = int(consistencia.replace('%', ''))
                if cons_val < 65:
                    confianza = max(40, confianza - 15)
                    etiqueta_verde = False
            except:
                pass
        
        # Ajuste por partidos jugados
        if stats_adicionales and stats_adicionales.get('partidos_jugados', 20) < 15:
            confianza = max(40, confianza - 10)
            etiqueta_verde = False
        
        return {
            'recomendacion': recomendacion,
            'confianza': confianza,
            'etiqueta_verde': etiqueta_verde,
            'tipo': resultado_heur.get('tipo', 'NBA'),
            'analisis': f"Confianza {confianza}% | Consistencia: {consistencia}",
            'proyeccion': resultado_heur.get('proyeccion', 'N/A'),
            'total_proyectado': resultado_heur.get('total_proyectado', 'N/A')
        }
