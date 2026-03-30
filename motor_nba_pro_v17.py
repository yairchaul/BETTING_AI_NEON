# motor_nba_pro_v19.py
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm

def analizar_nba_pro(partido_data, historial_db):
    home, away = partido_data['home'], partido_data['away']
    odds = partido_data['odds']
    
    # Team level (como antes pero más preciso)
    home_off = historial_db[home]['off_rating'].mean()
    home_def = historial_db[home]['def_rating'].mean()
    away_off = historial_db[away]['off_rating'].mean()
    away_def = historial_db[away]['def_rating'].mean()
    pace = (historial_db[home]['pace'].mean() + historial_db[away]['pace'].mean()) / 2
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
    
    # === NUEVA 3ª OPCIÓN: PLAYER PROPS ===
    props_recom = []
    if 'player_props' in partido_data:  # viene de tu player_props.py + scraper
        for player, prop_line in partido_data['player_props'].items():
            # Stats históricas del jugador (tú ya las tienes en DB)
            p_stats = historial_db.get(player, {})
            avg_pts = p_stats.get('pts_per_game', 0)
            avg_3pm = p_stats.get('three_pm', 0)
            matchup_factor = 1.0  # puedes ajustar por defensa rival
            
            # Poisson simple pero efectivo para props
            prob_over_pts = 1 - poisson.cdf(prop_line['pts_line'], avg_pts * matchup_factor)
            prob_over_3pm = 1 - poisson.cdf(prop_line['three_line'], avg_3pm * matchup_factor)
            
            if prob_over_pts > 0.58 and prop_line.get('pts_odds'):
                props_recom.append(f"✅ {player} OVER {prop_line['pts_line']} PTS")
            if prob_over_3pm > 0.57 and prop_line.get('three_odds'):
                props_recom.append(f"✅ {player} OVER {prop_line['three_line']} 3PM")
    
    # Value calculation (edge >5%)
    value_ml = (prob_home_win - (1 / (odds.get('ml_home', -110)/100 + 1))) * 100
    value_spread = avg_spread - odds.get('spread_home', 0)
    value_total = avg_total - odds.get('total', 0)
    
    recs = []
    if value_ml > 5: recs.append("✅ ML HOME")
    if value_spread > 1.8: recs.append("✅ SPREAD HOME")
    if value_spread < -1.8: recs.append("✅ SPREAD AWAY")
    if value_total > 4: recs.append("✅ OVER")
    if value_total < -4: recs.append("✅ UNDER")
    recs.extend(props_recom[:3])  # las 3 mejores props
    
    return {
        "deporte": "NBA",
        "partido": f"{home} vs {away}",
        "prob_home": round(prob_home_win*100, 1),
        "exp_spread": round(avg_spread, 1),
        "exp_total": round(avg_total, 1),
        "recomendaciones": recs or ["Espera mejor edge"],
        "edge": max(value_ml, abs(value_spread), abs(value_total))
    }