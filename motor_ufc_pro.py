# motor_ufc_pro_v2.py
def analizar_ufc_pro(peleadores_data, historial_db):
    a, b = peleadores_data['a'], peleadores_data['b']
    a_stats = historial_db[a]
    b_stats = historial_db[b]
    
    strike_def_a = a_stats['strike_def']
    td_acc_b = b_stats['td_acc']
    reach_diff = a_stats.get('reach', 0) - b_stats.get('reach', 0)
    
    sims = 12000
    a_wins = sum(1 for _ in range(sims) if np.random.rand() < (0.55 + (strike_def_a - td_acc_b + reach_diff*0.008)))
    prob_a_win = a_wins / sims
    prob_ko = prob_a_win * 0.48  # ajustado por stats
    
    recs = []
    if prob_a_win > 0.62: recs.append(f"✅ {a} GANADOR")
    if prob_ko > 0.40: recs.append(f"✅ {a} por KO")
    
    return {
        "deporte": "UFC",
        "pelea": f"{a} vs {b}",
        "prob_a": round(prob_a_win*100, 1),
        "recomendaciones": recs or ["Espera"],
        "edge": abs(prob_a_win - 0.5)*100
    }