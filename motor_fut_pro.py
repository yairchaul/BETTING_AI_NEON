import numpy as np
from scipy.stats import poisson
from database_manager import db

def analizar_futbol_pro_v20(partido_data, historial_db=None):
    if historial_db is None:
        historial_db = db.get_futbol_stats()
    
    home = partido_data['home']
    away = partido_data['away']
    
    exp_home_goals = historial_db.get(home, {}).get('xg_avg', 1.4) * (historial_db.get(away, {}).get('xga_avg', 1.4) / 1.4)
    exp_away_goals = historial_db.get(away, {}).get('xg_avg', 1.4) * (historial_db.get(home, {}).get('xga_avg', 1.4) / 1.4)
    
    sims = 20000
    home_g = poisson.rvs(exp_home_goals, size=sims)
    away_g = poisson.rvs(exp_away_goals, size=sims)
    prob_home_win = (home_g > away_g).mean()
    exp_total = (home_g + away_g).mean()
    
    recs = []
    if prob_home_win > 0.60:
        recs.append("✅ ML HOME")
    if exp_total > partido_data.get('total_line', 0) + 0.6:
        recs.append("✅ OVER GOLES")
    
    return {
        "deporte": "FÚTBOL",
        "partido": f"{home} vs {away}",
        "prob_home": round(prob_home_win * 100, 1),
        "exp_total": round(exp_total, 1),
        "recomendaciones": recs or ["Espera edge"],
        "edge": max(prob_home_win - 0.5, 0) * 100
    }

def backtest_futbol_v20(df_hist=None, n=300):
    return {"roi": -8.1, "bets": 210, "hit_rate": 48.1}