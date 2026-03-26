import sqlite3
import logging

logger = logging.getLogger(__name__)

from motor_nba_pro_v17 import get_motor_nba_v17
from selector_mejor_opcion_jerarquico import SelectorMejorOpcionJerarquico

class IntegradorV17:
    def __init__(self, db_path='data/betting_stats.db'):
        self.db_path = db_path
        self.motor = get_motor_nba_v17()
        self.selector = SelectorMejorOpcionJerarquico()
        logger.info("Motor V17 Pro cargado correctamente")

    def predecir_partido(self, local, visitante, fecha, linea_ou=225.0):
        try:
            resultado = self.motor.analizar(local, visitante, fecha, linea_ou)
            return resultado
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {"status": "NO_VALUE", "msg": str(e)}

    def obtener_estadisticas(self):
        return {"total": 0, "precision": 0}

_integrador = None

def get_integrador():
    global _integrador
    if _integrador is None:
        _integrador = IntegradorV17()
    return _integrador
