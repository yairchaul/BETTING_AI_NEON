"""
ESPN FÚTBOL - Módulo exclusivo para fútbol
"""
from gestor_ligas_universal import GestorLigasUniversal

class ESPN_FUTBOL:
    def __init__(self):
        self.gestor = GestorLigasUniversal()
    
    def get_games(self, liga):
        """Obtiene partidos de una liga específica"""
        return self.gestor.obtener_partidos(liga)
