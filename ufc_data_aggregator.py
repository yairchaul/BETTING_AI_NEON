"""
UFC DATA AGGREGATOR - Agregador de datos de peleadores UFC
"""
class UFCDataAggregator:
    def __init__(self):
        pass
    
    def get_fight_data(self, p1_nombre, p2_nombre, combates):
        """Obtiene datos de la pelea"""
        
        # Datos simulados (en producción vienen de SQLite)
        datos_p1 = {
            'nombre': p1_nombre,
            'record': '17-2-0',
            'ko_rate': 0.65,
            'grappling': 0.55,
            'reach': 178,
            'altura': 175
        }
        
        datos_p2 = {
            'nombre': p2_nombre,
            'record': '20-4-0',
            'ko_rate': 0.60,
            'grappling': 0.50,
            'reach': 175,
            'altura': 173
        }
        
        return {
            'peleador1': datos_p1,
            'peleador2': datos_p2
        }
