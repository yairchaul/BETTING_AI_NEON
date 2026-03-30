# motor_mlb_pro_v2.py
import numpy as np
from scipy.stats import poisson

def analizar_mlb_pro(partido_data, historial_db):
    home, away = partido_data['home'], partido_data['away']
    odds = partido_data['odds']
    
    # Team level básico (runs)
    exp_home_runs = historial_db[home]['avg_runs'] * (historial_db[away]['pitcher_era'] / 4.2)
    exp_away_runs = historial_db[away]['avg_runs'] * (historial_db[home]['pitcher_era'] / 4.2)
    
    sims = 15000
    home_r = poisson.rvs(exp_home_runs, size=sims)
    away_r = poisson.rvs(exp_away_runs, size=sims)
    prob_home_win = (home_r > away_r).mean()
    avg_total_runs = (home_r + away_r).mean()
    
    # === NUEVA 3ª OPCIÓN: PLAYER PROPS MLB ===
    props_recom = []
    if 'player_props' in partido_data:
        for player, prop in partido_data['player_props'].items():
            avg_hr = historial_db.get(player, {}).get('hr_per_game', 0)
            avg_hits = historial_db.get(player, {}).get('hits_per_game', 0)
            pitcher_factor = 1 - (historial_db[away if 'home' in player else home]['pitcher_k9'] / 9 * 0.15)
            
            prob_hr = poisson.pmf(1, avg_hr * pitcher_factor) + poisson.pmf(2, avg_hr * pitcher_factor)  # al menos 1 HR
            prob_hits_over = 1 - poisson.cdf(prop['hits_line'], avg_hits * pitcher_factor)
            
            if prob_hr > 0.32 and prop.get('hr_odds'):
                props_recom.append(f"✅ {player} SÍ HR")
            if prob_hits_over > 0.55:
                props_recom.append(f"✅ {player} OVER {prop['hits_line']} HITS")
    
    recs = []
    if prob_home_win > 0.58: recs.append("✅ ML HOME")
    if avg_total_runs > odds.get('total_runs', 0) + 0.8: recs.append("✅ OVER RUNS")
    recs.extend(props_recom[:3])
    
    return {
        "deporte": "MLB",
        "partido": f"{home} vs {away}",
        "prob_home": round(prob_home_win*100, 1),
        "exp_total_runs": round(avg_total_runs, 1),
        "recomendaciones": recs or ["Espera edge"],
        "edge": abs(prob_home_win - 0.5) * 100
    }