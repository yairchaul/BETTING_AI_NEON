import numpy as np
from scipy.stats import poisson

def analizar_mlb_pro_v2(partido_data, historial_db):
    exp_home_runs = historial_db.get(partido_data['home'], {}).get('avg_runs', 4.5) * (historial_db.get(partido_data['away'], {}).get('pitcher_era', 4.0) / 4.2)
    exp_away_runs = historial_db.get(partido_data['away'], {}).get('avg_runs', 4.5) * (historial_db.get(partido_data['home'], {}).get('pitcher_era', 4.0) / 4.2)
    
    sims = 15000
    home_r = poisson.rvs(exp_home_runs, size=sims)
    away_r = poisson.rvs(exp_away_runs, size=sims)
    prob_home_win = (home_r > away_r).mean()
    avg_total = (home_r + away_r).mean()
    
    # PLAYER PROPS MLB
    props_recom = []
    if 'player_props' in partido_data:
        for player, prop in partido_data['player_props'].items():
            avg_hr = historial_db.get(player, {}).get('hr_per_game', 0.4)
            prob_hr = 1 - poisson.cdf(0, avg_hr * 0.95)
            if prob_hr > 0.32:
                props_recom.append(f"✅ {player} SÍ HR")
    
    recs = []
    if prob_home_win > 0.58: recs.append("✅ ML HOME")
    if avg_total > partido_data.get('total_line', 0) + 0.8: recs.append("✅ OVER RUNS")
    recs.extend(props_recom[:3])
    
    return {
        "deporte": "MLB",
        "prob_home": round(prob_home_win*100, 1),
        "exp_total_runs": round(avg_total, 1),
        "recomendaciones": recs or ["Espera edge"],
        "edge": max(prob_home_win - 0.5, 0) * 100
    }