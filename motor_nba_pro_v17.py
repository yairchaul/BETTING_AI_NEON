import pandas as pd
import numpy as np
from scipy.stats import poisson

def analizar_nba_pro_v20(partido_data, historial_db):
    # Team level (eficiencia real)
    home_off = historial_db.get(partido_data['home'], {}).get('off_rating', 115)
    home_def = historial_db.get(partido_data['home'], {}).get('def_rating', 110)
    away_off = historial_db.get(partido_data['away'], {}).get('off_rating', 115)
    away_def = historial_db.get(partido_data['away'], {}).get('def_rating', 110)
    pace = partido_data.get('pace', 98)
    rest_h = partido_data.get('rest_home', 1)
    rest_a = partido_data.get('rest_away', 1)
    
    exp_home = (home_off * away_def / 100) * pace / 100 * (1 + 0.035 * rest_h)
    exp_away = (away_off * home_def / 100) * pace / 100 * (1 + 0.035 * rest_a)
    exp_total = exp_home + exp_away
    exp_spread = exp_home - exp_away + 3.2
    
    sims = 20000
    home_scores = poisson.rvs(exp_home, size=sims)
    away_scores = poisson.rvs(exp_away, size=sims)
    prob_home_win = (home_scores > away_scores).mean()
    avg_spread = (home_scores - away_scores).mean()
    avg_total = (home_scores + away_scores).mean()
    
    # PLAYER PROPS (Poisson real)
    props_recom = []
    if 'player_props' in partido_data:
        for player, prop in partido_data['player_props'].items():
            avg_pts = historial_db.get(player, {}).get('pts_per_game', 0)
            prob_over = 1 - poisson.cdf(prop['line'], avg_pts * 1.05)  # matchup factor
            if prob_over > 0.58:
                props_recom.append(f"✅ {player} OVER {prop['line']} PTS")
    
    # Value edge
    recs = []
    if prob_home_win > 0.58: recs.append("✅ ML HOME")
    if avg_spread > partido_data.get('spread_line', 0) + 1.8: recs.append("✅ SPREAD HOME")
    if avg_total > partido_data.get('total_line', 0) + 4: recs.append("✅ OVER")
    recs.extend(props_recom[:3])
    
    return {
        "deporte": "NBA",
        "prob_home": round(prob_home_win*100, 1),
        "exp_spread": round(avg_spread, 1),
        "exp_total": round(avg_total, 1),
        "recomendaciones": recs or ["Espera edge"],
        "edge": max(prob_home_win - 0.5, 0) * 100
    }

# Backtest integrado (llámalo desde integrador)
def backtest_nba_v20(df_historial):
    # df_historial debe tener columnas: exp_home, exp_away, actual_home_win, etc.
    profits = []
    for _, row in df_historial.iterrows():
        pred = analizar_nba_pro_v20(row.to_dict(), {})  # tu DB aquí
        if "ML HOME" in pred["recomendaciones"]:
            profit = 0.909 if row["actual_home_win"] else -1
        elif any("OVER" in r for r in pred["recomendaciones"]):
            profit = 0.909 if row.get("prop_over", 0) else -1
        else:
            profit = 0
        profits.append(profit)
    return {"roi": round(sum(profits)/len([p for p in profits if p != 0])*100, 1) if any(profits) else 0}