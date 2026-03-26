"""
ANALIZADOR NBA PROPS - Análisis de triples y puntos
"""
class AnalizadorNBAProps:
    def __init__(self):
        pass
    
    def analizar_partido(self, partido):
        """Analiza props de triples para el partido"""
        
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        
        # Simular análisis de jugadores destacados
        jugadores_destacados = []
        
        # Ejemplo de jugadores destacados (en producción vendrían de DB)
        if "Lakers" in local:
            jugadores_destacados.append({
                'nombre': 'LeBron James',
                'triples': 2.5,
                'probabilidad': 68,
                'recomendacion': 'OVER 2.5 TRIPLES'
            })
            jugadores_destacados.append({
                'nombre': 'Austin Reaves',
                'triples': 1.5,
                'probabilidad': 55,
                'recomendacion': 'UNDER 2.5 TRIPLES'
            })
        
        return {
            'partido': f"{local} vs {visitante}",
            'jugadores': jugadores_destacados,
            'recomendaciones': jugadores_destacados
        }
