"""
SELECTOR DE MEJOR OPCIÓN PARA FÚTBOL
"""
class SelectorMejorOpcion:
    @staticmethod
    def seleccionar(probabilidades):
        """Selecciona la mejor opción basada en probabilidades"""
        
        opciones = [
            ('Over 2.5', probabilidades.get('over_25', 0)),
            ('BTTS', probabilidades.get('btts', 0)),
            ('Victoria Local', probabilidades.get('local_win', 0)),
            ('Victoria Visitante', probabilidades.get('visit_win', 0))
        ]
        
        mejor = max(opciones, key=lambda x: x[1])
        
        return {
            'mejor_opcion': mejor[0],
            'probabilidad': mejor[1],
            'todas': opciones
        }
