"""
PLAYER PROPS - Función para calcular probabilidad de props de jugadores
Se integrará con scraper de líderes en próxima iteración
"""

from scipy.stats import norm

def calcular_player_prop_prob(promedio, desviacion, linea_prop, tipo="puntos"):
    """
    Calcula probabilidad de OVER en props de jugadores usando distribución normal
    
    Args:
        promedio: promedio histórico del jugador (pts, 3pm, hr, etc.)
        desviacion: desviación estándar
        linea_prop: línea de la casa (ej: 25.5)
        tipo: "puntos", "triples", "hr", "asistencias"
    
    Returns:
        float: probabilidad de OVER
    """
    if promedio <= 0:
        return 0.5
    
    z = (linea_prop - promedio) / (desviacion + 0.01)
    prob_over = 1 - norm.cdf(z)
    
    # Limitar entre 5% y 95%
    return max(0.05, min(0.95, prob_over))

def calcular_player_prop_recomendacion(promedio, desviacion, linea_prop, umbral=0.55):
    """
    Devuelve recomendación para player prop
    
    Returns:
        dict con recomendación, probabilidad y confianza
    """
    prob = calcular_player_prop_prob(promedio, desviacion, linea_prop)
    
    if prob >= umbral:
        return {
            'recomendacion': f"OVER {linea_prop}",
            'probabilidad': round(prob * 100, 1),
            'confianza': int(prob * 100),
            'etiqueta_verde': prob >= 0.60
        }
    elif 1 - prob >= umbral:
        return {
            'recomendacion': f"UNDER {linea_prop}",
            'probabilidad': round((1 - prob) * 100, 1),
            'confianza': int((1 - prob) * 100),
            'etiqueta_verde': (1 - prob) >= 0.60
        }
    else:
        return {
            'recomendacion': "SIN VALOR CLARO",
            'probabilidad': 0,
            'confianza': 0,
            'etiqueta_verde': False
        }
