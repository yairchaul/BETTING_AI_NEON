# modules/cerebro.py
import requests
import numpy as np
import streamlit as st
import unicodedata

SIMULATIONS = 20000

def buscar_equipos_v2(nombre_query):
    """Motor de búsqueda elástico que emula la flexibilidad de Google."""
    try:
        if len(nombre_query) < 3:
            return []
            
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Normalización para ignorar acentos y mayúsculas
        query = unicodedata.normalize('NFD', nombre_query)
        query = "".join([c for c in query if unicodedata.category(c) != 'Mn']).lower()
        
        # Intentar búsqueda general
        url = f"https://v3.football.api-sports.io/teams?search={query}"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        candidatos = []
        if data.get('results', 0) > 0:
            for item in data['response']:
                candidatos.append({
                    "display": f"{item['team']['name']} ({item['team']['country']})",
                    "id": item['team']['id'],
                    "logo": item['team']['logo'],
                    "name": item['team']['name']
                })
        return candidatos
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return []

def extraer_stats_avanzadas(team_id):
    """Extrae métricas de rendimiento (ataque/defensa) basadas en los últimos juegos."""
    try:
        api_key = st.secrets["football_api_key"]
        headers = {'x-apisports-key': api_key}
        
        # Obtenemos los últimos 10 partidos para mayor precisión estadística
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        goles_favor = []
        goles_contra = []
        
        for game in data.get('response', []):
            is_home = game['teams']['home']['id'] == team_id
            
            # Goles del equipo
            if is_home:
                goles_favor.append(game['goals']['home'] if game['goals']['home'] is not None else 0)
                goles_contra.append(game['goals']['away'] if game['goals']['away'] is not None else 0)
            else:
                goles_favor.append(game['goals']['away'] if game['goals']['away'] is not None else 0)
                goles_contra.append(game['goals']['home'] if game['goals']['home'] is not None else 0)
        
        # Cálculo de potencia relativa
        if goles_favor:
            avg_favor = sum(goles_favor) / len(goles_favor)
        else:
            avg_favor = 1.0
            
        if goles_contra:
            avg_contra = sum(goles_contra) / len(goles_contra)
        else:
            avg_contra = 1.2
        
        return {
            "attack_power": avg_favor,
            "defense_weakness": avg_contra,
            "partidos_analizados": len(goles_favor)
        }
    except Exception as e:
        st.warning(f"Error obteniendo stats para team {team_id}: {e}")
        return {
            "attack_power": 1.1,
            "defense_weakness": 1.1,
            "partidos_analizados": 0
        }

def simular_probabilidades(stats_h, stats_a):
    """Simulación de Monte Carlo con Distribución de Poisson."""
    try:
        # Factor de ventaja de localía (10% extra para el local)
        home_exp = stats_h["attack_power"] * stats_a["defense_weakness"] * 1.1
        away_exp = stats_a["attack_power"] * stats_h["defense_weakness"]
        
        # Asegurar valores mínimos
        home_exp = max(0.5, home_exp)
        away_exp = max(0.3, away_exp)
        
        # Generamos 20,000 resultados posibles del partido
        home_goals = np.random.poisson(home_exp, SIMULATIONS)
        away_goals = np.random.poisson(away_exp, SIMULATIONS)
        
        # Calculamos probabilidades
        prob_h = np.mean(home_goals > away_goals)
        prob_draw = np.mean(home_goals == away_goals)
        prob_a = np.mean(away_goals > home_goals)
        
        # Otras métricas útiles
        total_goals = home_goals + away_goals
        prob_over_1_5 = np.mean(total_goals > 1.5)
        prob_over_2_5 = np.mean(total_goals > 2.5)
        prob_btts = np.mean((home_goals > 0) & (away_goals > 0))
        
        # Probabilidad de Doble Oportunidad (1X)
        prob_1x = prob_h + prob_draw
        prob_x2 = prob_a + prob_draw
        
        return {
            "local": prob_h,
            "empate": prob_draw,
            "visitante": prob_a,
            "doble_oportunidad_1x": prob_1x,
            "doble_oportunidad_x2": prob_x2,
            "over_1.5": prob_over_1_5,
            "over_2.5": prob_over_2_5,
            "btts": prob_btts,
            "goles_promedio": np.mean(total_goals)
        }
    except Exception as e:
        st.error(f"Error en simulación: {e}")
        return {
            "local": 0.4,
            "empate": 0.2,
            "visitante": 0.4,
            "doble_oportunidad_1x": 0.6,
            "doble_oportunidad_x2": 0.6,
            "over_1.5": 0.7,
            "over_2.5": 0.5,
            "btts": 0.5,
            "goles_promedio": 2.2
        }

def obtener_mejor_apuesta(stats_h, stats_a):
    """Determina la mejor apuesta basada en las probabilidades simuladas."""
    probs = simular_probabilidades(stats_h, stats_a)
    
    # Encontrar la probabilidad más alta
    max_prob = 0
    best_selection = "Local"
    
    opciones = [
        ("Local", probs["local"]),
        ("Empate", probs["empate"]),
        ("Visitante", probs["visitante"]),
        ("Doble oportunidad (Local/Empate)", probs["doble_oportunidad_1x"]),
        ("Doble oportunidad (Visitante/Empate)", probs["doble_oportunidad_x2"]),
        ("Over 1.5 goles", probs["over_1.5"]),
        ("Over 2.5 goles", probs["over_2.5"]),
        ("Ambos equipos anotan (BTTS)", probs["btts"])
    ]
    
    for nombre, prob in opciones:
        if prob > max_prob:
            max_prob = prob
            best_selection = nombre
    
    return {
        "selection": best_selection,
        "probability": max_prob,
        "all_probabilities": probs
    }

def obtener_forma_reciente(team_id):
    """Obtiene la forma reciente de un equipo (wrapper para compatibilidad)."""
    return extraer_stats_avanzadas(team_id)

def obtener_forma_reciente(team_id):
    """Obtiene la forma reciente de un equipo (wrapper para compatibilidad)."""
    return extraer_stats_avanzadas(team_id)
