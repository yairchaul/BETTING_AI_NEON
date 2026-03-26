import logging
import numpy as np
from scipy.stats import poisson
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

class MotorNBA_Pro_V17:
    def __init__(self, db_path='data/betting_stats.db'):
        self.db_path = db_path
        logger.info("Motor NBA Pro V17 - MODO REAL (con BD)")

    def obtener_ultimos_5(self, equipo):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            hoy = datetime.now()
            inicio_temporada = datetime(hoy.year - 1 if hoy.month < 10 else hoy.year, 10, 1)
            
            cursor.execute("""
                SELECT puntos_favor, puntos_contra 
                FROM historial_equipos 
                WHERE nombre_equipo = ? AND deporte = 'nba' 
                  AND fecha >= ? 
                ORDER BY fecha DESC LIMIT 5
            """, (equipo, inicio_temporada.strftime('%Y%m%d')))
            rows = cursor.fetchall()
            conn.close()

            if len(rows) < 3:
                return None

            pts_favor = np.array([r[0] for r in rows])
            pts_contra = np.array([r[1] for r in rows])

            return {
                "prom_favor": float(np.mean(pts_favor)),
                "prom_contra": float(np.mean(pts_contra)),
                "std_favor": float(np.std(pts_favor, ddof=1)) if len(pts_favor) > 1 else 12.0
            }
        except Exception as e:
            logger.error(f"Error BD {equipo}: {e}")
            return None

    def convertir_cuota_a_decimal(self, cuota):
        if not cuota:
            return 1.91
        try:
            cuota_str = str(cuota).strip()
            if cuota_str.startswith('+'):
                return 1 + (float(cuota_str[1:]) / 100)
            elif cuota_str.startswith('-'):
                return 1 + (100 / float(cuota_str[1:]))
            else:
                return float(cuota_str)
        except:
            return 1.91

    def calcular_valor_esperado(self, prob, cuota):
        try:
            cuota_dec = self.convertir_cuota_a_decimal(cuota)
            ev = (prob * cuota_dec) - 1
            return round(ev * 100, 1)
        except:
            return 0.0

    def analizar(self, local, visitante, fecha, linea_ou=225.0):
        stats_l = self.obtener_ultimos_5(local)
        stats_v = self.obtener_ultimos_5(visitante)

        if not stats_l or not stats_v:
            logger.warning(f"Datos insuficientes para {local} vs {visitante}")
            return {"status": "NO_VALUE", "msg": "Datos insuficientes"}

        ataque_l = stats_l["prom_favor"]
        defensa_v = stats_v["prom_contra"]
        ataque_v = stats_v["prom_favor"]
        defensa_l = stats_l["prom_contra"]

        pace_factor = 1.03 if (ataque_l + ataque_v) > 230 else 0.97

        expected_local = (ataque_l * 0.6 + defensa_v * 0.4) * pace_factor
        expected_visit = (ataque_v * 0.6 + defensa_l * 0.4) * pace_factor
        total_proyectado = expected_local + expected_visit

        np.random.seed(42)
        sim_local = poisson.rvs(expected_local, size=10000)
        sim_visit = poisson.rvs(expected_visit, size=10000)
        sim_total = sim_local + sim_visit

        prob_over = float(np.mean(sim_total > linea_ou))
        prob_under = 1 - prob_over

        ev_over = self.calcular_valor_esperado(prob_over, "-110")
        ev_under = self.calcular_valor_esperado(prob_under, "-110")

        if ev_over > ev_under and ev_over > 3:
            recomendacion = f"OVER {linea_ou}"
            ev_mejor = ev_over
            prob_mejor = prob_over
        elif ev_under > 3:
            recomendacion = f"UNDER {linea_ou}"
            ev_mejor = ev_under
            prob_mejor = prob_under
        else:
            recomendacion = "SIN VALOR CLARO"
            ev_mejor = 0
            prob_mejor = 0.5

        return {
            "status": "OK",
            "over_under": {
                "pick": recomendacion,
                "ev_pct": ev_mejor,
                "prob_pct": round(prob_mejor * 100, 1),
                "confianza": min(85, int(50 + ev_mejor * 2))
            },
            "proyecciones": {
                "total": round(total_proyectado, 1),
                "detalle": f"Proy: {expected_local:.1f} - {expected_visit:.1f} | {stats_l['prom_favor']:.1f} vs {defensa_v:.1f}"
            },
            "etiqueta_verde": ev_mejor >= 8
        }

def get_motor_nba_v17():
    return MotorNBA_Pro_V17()
