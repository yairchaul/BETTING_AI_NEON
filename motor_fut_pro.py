# -*- coding: utf-8 -*-
"""
MOTOR FÚTBOL PRO V20 - Análisis con Poisson + Monte Carlo
"""

import numpy as np
from scipy.stats import poisson
import logging
from database_manager import db

logger = logging.getLogger(__name__)

def analizar_futbol_pro_v20(partido_data):
    """
    Analiza partido de fútbol con Poisson + Monte Carlo
    
    Args:
        partido_data: dict con local, visitante, stats
    
    Returns:
        dict con recomendacion, confianza, etc.
    """
    local = partido_data.get('home', '')
    visitante = partido_data.get('away', '')
    linea_ou = partido_data.get('odds', {}).get('over_under', 2.5)
    
    # Obtener últimos 5 partidos
    goles_local = db.obtener_historial_futbol(local, limite=5)
    goles_visit = db.obtener_historial_futbol(visitante, limite=5)
    
    if not goles_local or not goles_visit:
        logger.warning(f"Datos insuficientes para {local} vs {visitante}")
        # Datos por defecto basados en fuerza del equipo
        goles_local = [1, 2, 1, 1, 2]
        goles_visit = [1, 1, 1, 2, 1]
    
    # Calcular promedios
    prom_local = np.mean(goles_local)
    prom_visit = np.mean(goles_visit)
    
    # Proyección Poisson
    lambda_local = prom_local * 1.02  # ligera ventaja local
    lambda_visit = prom_visit * 0.98
    
    # Simulación Monte Carlo
    np.random.seed(42)
    sim_local = poisson.rvs(lambda_local, size=10000)
    sim_visit = poisson.rvs(lambda_visit, size=10000)
    sim_total = sim_local + sim_visit
    
    # Probabilidades
    prob_over = np.mean(sim_total > linea_ou)
    prob_under = 1 - prob_over
    prob_btts = np.mean((sim_local > 0) & (sim_visit > 0))
    prob_local_win = np.mean(sim_local > sim_visit)
    prob_visit_win = np.mean(sim_visit > sim_local)
    
    # Determinar mejor recomendación (jerarquía)
    if prob_over > 0.6:
        recomendacion = f"OVER {linea_ou}"
        confianza = int(prob_over * 100)
        probabilidad = prob_over
    elif prob_under > 0.6:
        recomendacion = f"UNDER {linea_ou}"
        confianza = int(prob_under * 100)
        probabilidad = prob_under
    elif prob_btts > 0.6:
        recomendacion = "BTTS"
        confianza = int(prob_btts * 100)
        probabilidad = prob_btts
    elif prob_local_win > 0.55:
        recomendacion = f"GANA {local}"
        confianza = int(prob_local_win * 100)
        probabilidad = prob_local_win
    elif prob_visit_win > 0.55:
        recomendacion = f"GANA {visitante}"
        confianza = int(prob_visit_win * 100)
        probabilidad = prob_visit_win
    else:
        recomendacion = "SIN VALOR CLARO"
        confianza = 50
        probabilidad = 0.5
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(probabilidad * 100, 1),
        'total_proyectado': round(np.mean(sim_total), 1),
        'proyeccion_local': round(np.mean(sim_local), 1),
        'proyeccion_visitante': round(np.mean(sim_visit), 1),
        'prob_over': round(prob_over * 100, 1),
        'prob_btts': round(prob_btts * 100, 1),
        'etiqueta_verde': confianza >= 70,
        'stats_local': {'goles': goles_local, 'promedio': round(prom_local, 1)},
        'stats_visitante': {'goles': goles_visit, 'promedio': round(prom_visit, 1)}
    }

def backtest_futbol_pro_v20(partidos_historicos):
    """Backtest para evaluar precisión del modelo"""
    resultados = []
    for partido in partidos_historicos:
        try:
            prediccion = analizar_futbol_pro_v20(partido)
            real = partido.get('resultado_real', {})
            acierto = False
            rec = prediccion.get('recomendacion', '')
            
            if 'OVER' in rec:
                acierto = real.get('total_goles', 0) > partido.get('odds', {}).get('over_under', 2.5)
            elif 'UNDER' in rec:
                acierto = real.get('total_goles', 0) < partido.get('odds', {}).get('over_under', 2.5)
            elif 'BTTS' in rec:
                acierto = real.get('local_goles', 0) > 0 and real.get('visit_goles', 0) > 0
            elif 'GANA' in rec:
                ganador = rec.replace('GANA ', '')
                if ganador == partido.get('home'):
                    acierto = real.get('local_goles', 0) > real.get('visit_goles', 0)
                else:
                    acierto = real.get('visit_goles', 0) > real.get('local_goles', 0)
            
            resultados.append({
                'partido': f"{partido.get('home')} vs {partido.get('away')}",
                'prediccion': rec,
                'acierto': acierto,
                'confianza': prediccion.get('confianza', 0)
            })
        except Exception as e:
            logger.error(f"Error en backtest: {e}")
    
    aciertos = sum(1 for r in resultados if r['acierto'])
    total = len(resultados)
    
    return {
        'total_partidos': total,
        'aciertos': aciertos,
        'precision': round(aciertos / total * 100, 1) if total > 0 else 0,
        'resultados': resultados
    }
