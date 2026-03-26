import numpy as np
from scipy.stats import norm, poisson
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalizadorNBAMejorado:
    def __init__(self, partido_data=None):
        self.partido = partido_data

    def convertir_cuota_a_decimal(self, cuota):
        """Convierte cuotas Americanas a decimal de forma segura"""
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
        except Exception as e:
            logger.error(f"Error calculando EV con cuota {cuota}: {e}")
            return 0.0

    def obtener_ultimos_5(self, equipo):
        try:
            conn = sqlite3.connect('data/betting_stats.db')
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
                "pts_favor": pts_favor,
                "pts_contra": pts_contra,
                "prom_favor": float(np.mean(pts_favor)),
                "prom_contra": float(np.mean(pts_contra)),
                "std_favor": float(np.std(pts_favor, ddof=1)) if len(pts_favor) > 1 else 12.0,
                "ultimos_favor": pts_favor.tolist()
            }
        except Exception as e:
            logger.error(f"Error últimos 5 de {equipo}: {e}")
            return None

    def analizar(self):
        if not self.partido:
            return {"status": "ERROR", "msg": "No hay datos del partido"}

        local = self.partido.get("local", "")
        visitante = self.partido.get("visitante", "")
        odds = self.partido.get("odds", {})
        
        linea_ou = float(odds.get("over_under", 225.0))
        ou_odds = odds.get("over_odds", "-110")
        under_odds = odds.get("under_odds", "-110")
        ml_local = odds.get("moneyline", {}).get("local", "-110")
        ml_visit = odds.get("moneyline", {}).get("visitante", "-110")

        stats_l = self.obtener_ultimos_5(local)
        stats_v = self.obtener_ultimos_5(visitante)

        if not stats_l or not stats_v:
            return {"status": "NO_VALUE", "msg": "Datos insuficientes"}

        # Proyección
        ataque_l = stats_l["prom_favor"]
        defensa_v = stats_v["prom_contra"]
        ataque_v = stats_v["prom_favor"]
        defensa_l = stats_l["prom_contra"]

        pace_factor = 1.03 if (ataque_l + ataque_v) > 230 else 0.97

        expected_local = (ataque_l * 0.6 + defensa_v * 0.4) * pace_factor
        expected_visit = (ataque_v * 0.6 + defensa_l * 0.4) * pace_factor
        total_proyectado = expected_local + expected_visit

        # Simulación
        np.random.seed(42)
        sim_local = poisson.rvs(expected_local, size=10000)
        sim_visit = poisson.rvs(expected_visit, size=10000)
        sim_total = sim_local + sim_visit
        sim_diff = sim_local - sim_visit

        prob_over = float(np.mean(sim_total > linea_ou))
        prob_under = 1 - prob_over
        prob_ml_local = float(np.mean(sim_local > sim_visit))
        prob_ml_visit = 1 - prob_ml_local

        # Opciones
        opciones = [
            ("OVER", f"OVER {linea_ou}", prob_over, ou_odds),
            ("UNDER", f"UNDER {linea_ou}", prob_under, under_odds),
            ("ML_LOCAL", f"ML {local}", prob_ml_local, ml_local),
            ("ML_VISIT", f"ML {visitante}", prob_ml_visit, ml_visit),
        ]

        opciones_validas = []
        for tipo, texto, prob, cuota in opciones:
            ev = self.calcular_valor_esperado(prob, cuota)
            if ev > 3:
                opciones_validas.append((tipo, texto, ev, prob, cuota))

        if not opciones_validas:
            recomendacion = "SIN VALOR CLARO"
            ev_mejor = 0
            prob_mejor = 0
        else:
            mejor = max(opciones_validas, key=lambda x: x[2])
            tipo_mejor, texto_mejor, ev_mejor, prob_mejor, _ = mejor
            recomendacion = texto_mejor

        return {
            "status": "OK",
            "over_under": {
                "pick": recomendacion,
                "ev_pct": round(ev_mejor, 1),
                "prob_pct": round(prob_mejor * 100, 1),
                "confianza": min(95, int(50 + ev_mejor * 2))
            },
            "proyecciones": {
                "total": round(total_proyectado, 1),
                "detalle": f"Pace: {pace_factor:.2f}"
            },
            "etiqueta_verde": ev_mejor >= 8
        }
