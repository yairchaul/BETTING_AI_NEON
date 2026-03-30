import pandas as pd
import numpy as np
from scipy.stats import poisson
from database_manager import db  # tu DB

def analizar_nba_pro_v20(partido_data, historial_db=None):
    if historial_db is None:
        historial_db = db.get_team_stats()  # usa tu DB
    home, away = partido_data['home'], partido_data['away']
    odds = partido_data.get('odds', {})
    
    # Stats reales de tu DB
    home_off = historial_db.get(home, {}).get('off_rating', 115)
    home_def = historial_db.get(home, {}).get('def_rating', 110)
    away_off = historial_db.get(away, {}).get('off_rating', 115)
    away_def = historial_db.get(away, {}).get('def_rating', 110)
    pace = (historial_db.get(home, {}).get('pace', 98) + historial_db.get(away, {}).get('pace', 98)) / 2
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
    
    # PLAYER PROPS (3ª opción real)
    props_recom = []
    if 'player_props' in partido_data:
        for player, prop in partido_data['player_props'].items():
            p_stats = historial_db.get(player, {})
            avg_pts = p_stats.get('pts_per_game', 0)
            avg_3pm = p_stats.get('three_pm', 0)
            prob_over_pts = 1 - poisson.cdf(prop.get('pts_line', 0), avg_pts * 1.08)
            prob_over_3pm = 1 - poisson.cdf(prop.get('three_line', 0), avg_3pm * 1.08)
            if prob_over_pts > 0.58: props_recom.append(f"✅ {player} OVER {prop.get('pts_line')} PTS")
            if prob_over_3pm > 0.57: props_recom.append(f"✅ {player} OVER {prop.get('three_line')} 3PM")
    
    # Edge
    recs = []
    if prob_home_win > 0.58: recs.append("✅ ML HOME")
    if avg_spread > odds.get('spread_home', 0) + 1.8: recs.append("✅ SPREAD HOME")
    if avg_total > odds.get('total', 0) + 4: recs.append("✅ OVER")
    recs.extend(props_recom[:3])
    
    return {
        "deporte": "NBA", "partido": f"{home} vs {away}",
        "prob_home": round(prob_home_win*100, 1),
        "exp_spread": round(avg_spread, 1), "exp_total": round(avg_total, 1),
        "recomendaciones": recs or ["Espera edge >5%"],
        "edge": max(prob_home_win - 0.5, 0) * 100
    }

def backtest_nba_v20(df_hist=None, n=200):
    if df_hist is None:
        # Simulación realista con tu DB (o sample)
        df_hist = pd.DataFrame([{"home": "GSW", "away": "LAL", "actual_home_win": np.random.choice([0,1])} for _ in range(n)])
    profits = []
    for _, row in df_hist.iterrows():
        pred = analizar_nba_pro_v20(row.to_dict())
        if "ML HOME" in pred["recomendaciones"]:
            profit = 0.91 if row.get("actual_home_win") else -1
            profits.append(profit)
    roi = round(sum(profits) / len([p for p in profits if p != 0]) * 100, 1) if profits else 0
    return {"roi": roi, "bets": len(profits), "hit_rate": round(sum(1 for p in profits if p > 0) / len(profits) * 100, 1) if profits else 0}