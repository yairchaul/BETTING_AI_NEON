# === ARCHIVO: pro_analyzer_ultimate.py (MODIFICADO) ===
# Agrega estas importaciones al inicio del archivo:

from modules.team_translator import TeamTranslator
from modules.odds_api_integrator import OddsAPIIntegrator

# Luego, dentro de la funci?n analyze_screenshot, despu?s de obtener
# los equipos del parser, agrega:

def analyze_screenshot(image_path):
    # ... c?digo existente ...
    
    # Obtener equipos del parser
    resultado = universal_parser.parse_image(image_path)
    home_team = resultado.get('home_team', '')
    away_team = resultado.get('away_team', '')
    odds_captura = resultado.get('odds', {})
    
    # INICIO DE NUEVA FUNCIONALIDAD
    # Traducir equipos para la API
    translator = TeamTranslator()
    odds_api = OddsAPIIntegrator()
    
    home_api = translator.translate(home_team)
    away_api = translator.translate(away_team)
    
    # Buscar odds reales
    odds_reales = odds_api.get_live_odds(home_api, away_api)
    
    if odds_reales:
        # Usar odds reales para c?lculos
        cuotas_reales = {
            'local': odds_reales['cuota_local'],
            'empate': odds_reales['cuota_empate'],
            'visitante': odds_reales['cuota_visitante']
        }
        
        # Calcular EV con odds reales
        probs = resultado.get('probabilidades', [0.33, 0.34, 0.33])
        ev_real = {
            'local': (probs[0] * cuotas_reales['local']) - 1,
            'empate': (probs[1] * cuotas_reales['empate']) - 1,
            'visitante': (probs[2] * cuotas_reales['visitante']) - 1
        }
        
        # A?adir a los resultados
        resultado['odds_reales'] = cuotas_reales
        resultado['ev_real'] = ev_real
        resultado['traduccion'] = {
            'home_original': home_team,
            'home_api': home_api,
            'away_original': away_team,
            'away_api': away_api
        }
    # FIN DE NUEVA FUNCIONALIDAD
    
    # ... continuar con el resto del an?lisis ...
    
    return resultado
