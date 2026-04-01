# -*- coding: utf-8 -*-
"""
MOTOR NBA PRO V17 - Análisis con Poisson + Monte Carlo
"""

import numpy as np
from scipy.stats import poisson
import logging
from database_manager import db

logger = logging.getLogger(__name__)

def analizar_nba_pro_v17(partido_data):
    """
    Analiza partido NBA con Poisson + Monte Carlo
    
    Args:
        partido_data: dict con local, visitante, odds
    
    Returns:
        dict con recomendacion, confianza, etc.
    """
    local = partido_data.get('home', '')
    visitante = partido_data.get('away', '')
    odds = partido_data.get('odds', {})
    linea_ou = odds.get('over_under', 225.0)
    
    # Obtener últimos 5 partidos de cada equipo
    stats_l = db.get_team_stats(local, deporte='nba', limit=5)
    stats_v = db.get_team_stats(visitante, deporte='nba', limit=5)
    
    if not stats_l or not stats_v:
        logger.warning(f"Datos insuficientes para {local} vs {visitante}")
        return {
            'recomendacion': 'DATOS INSUFICIENTES',
            'confianza': 40,
            'total_proyectado': 225,
            'etiqueta_verde': False
        }
    
    # Proyección ataque vs defensa
    ataque_l = stats_l.get('promedio_favor', 112)
    defensa_v = stats_v.get('promedio_contra', 110)
    ataque_v = stats_v.get('promedio_favor', 110)
    defensa_l = stats_l.get('promedio_contra', 112)
    
    # Ajuste por ritmo (pace)
    pace_factor = 1.03 if (ataque_l + ataque_v) > 230 else 0.97
    
    expected_local = (ataque_l * 0.6 + defensa_v * 0.4) * pace_factor
    expected_visit = (ataque_v * 0.6 + defensa_l * 0.4) * pace_factor
    total_proyectado = expected_local + expected_visit
    
    # Simulación Monte Carlo (10,000 iteraciones)
    np.random.seed(42)
    sim_local = poisson.rvs(expected_local, size=10000)
    sim_visit = poisson.rvs(expected_visit, size=10000)
    sim_total = sim_local + sim_visit
    
    prob_over = np.mean(sim_total > linea_ou)
    prob_under = 1 - prob_over
    
    # Determinar recomendación
    if prob_over > 0.55:
        recomendacion = f"OVER {linea_ou}"
        confianza = int(prob_over * 100)
        probabilidad = prob_over
    elif prob_under > 0.55:
        recomendacion = f"UNDER {linea_ou}"
        confianza = int(prob_under * 100)
        probabilidad = prob_under
    else:
        recomendacion = "SIN VALOR CLARO"
        confianza = 50
        probabilidad = 0.5
    
    return {
        'recomendacion': recomendacion,
        'confianza': confianza,
        'probabilidad': round(probabilidad * 100, 1),
        'total_proyectado': round(total_proyectado, 1),
        'proyeccion_local': round(expected_local, 1),
        'proyeccion_visitante': round(expected_visit, 1),
        'etiqueta_verde': confianza >= 70,
        'stats_local': stats_l,
        'stats_visitante': stats_v
    }

def backtest_nba_pro_v17(partidos_historicos):
    """Backtest para evaluar precisión del modelo"""
    resultados = []
    for partido in partidos_historicos:
        try:
            prediccion = analizar_nba_pro_v17(partido)
            real = partido.get('resultado_real', {})
            acierto = False
            
            if 'OVER' in prediccion.get('recomendacion', ''):
                acierto = real.get('total', 0) > partido.get('odds', {}).get('over_under', 225)
            elif 'UNDER' in prediccion.get('recomendacion', ''):
                acierto = real.get('total', 0) < partido.get('odds', {}).get('over_under', 225)
            
            resultados.append({
                'partido': f"{partido.get('home')} vs {partido.get('away')}",
                'prediccion': prediccion.get('recomendacion'),
                'real': real.get('total', 0),
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
