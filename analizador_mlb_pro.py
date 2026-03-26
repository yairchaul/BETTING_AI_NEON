"""
ANALIZADOR MLB PRO - Versión corregida
"""
import sqlite3
import numpy as np
from datetime import datetime

class AnalizadorMLBPro:
    def __init__(self, api_key_gemini=None):
        self.db_path = 'data/betting_stats.db'
        self.gemini = None
        if api_key_gemini:
            try:
                from cerebro_gemini_pro import CerebroGemini
                self.gemini = CerebroGemini(api_key_gemini)
            except:
                pass

    def obtener_stats_reales(self, equipo):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            hoy = datetime.now().strftime("%Y%m%d")
            
            cursor.execute("""
                SELECT puntos_favor, puntos_contra, fecha 
                FROM historial_equipos 
                WHERE nombre_equipo = ? AND deporte = 'mlb' AND fecha < ?
                ORDER BY fecha DESC LIMIT 10
            """, (equipo, hoy))
            rows = cursor.fetchall()
            conn.close()
            
            if rows and len(rows) >= 3:
                carreras_favor = [r[0] for r in rows]
                carreras_contra = [r[1] for r in rows]
                varianza = np.std(carreras_favor) if len(carreras_favor) > 1 else 0
                consistencia = max(0, 100 - (varianza * 12))
                
                return {
                    'promedio_favor': np.mean(carreras_favor),
                    'promedio_contra': np.mean(carreras_contra),
                    'consistencia': consistencia,
                    'varianza': varianza,
                    'ultimos': carreras_favor[:5]
                }
            return None
        except Exception as e:
            print(f"Error obteniendo stats de {equipo}: {e}")
            return None

    def analizar_partido(self, partido, stats_local=None, stats_visit=None):
        local = partido.get('local', '')
        visitante = partido.get('visitante', '')
        
        # Intentar obtener datos de SQLite
        st_l = self.obtener_stats_reales(local)
        st_v = self.obtener_stats_reales(visitante)
        
        # Si no hay datos en SQLite, usar los proporcionados como fallback
        if not st_l and stats_local:
            st_l = {
                'promedio_favor': stats_local.get('promedio_favor', 4.5),
                'promedio_contra': stats_local.get('promedio_contra', 4.5),
                'consistencia': stats_local.get('consistencia', 50)
            }
        if not st_v and stats_visit:
            st_v = {
                'promedio_favor': stats_visit.get('promedio_favor', 4.5),
                'promedio_contra': stats_visit.get('promedio_contra', 4.5),
                'consistencia': stats_visit.get('consistencia', 50)
            }
        
        # Si aún no hay datos, usar valores por defecto
        if not st_l:
            st_l = {'promedio_favor': 4.5, 'promedio_contra': 4.5, 'consistencia': 50}
        if not st_v:
            st_v = {'promedio_favor': 4.5, 'promedio_contra': 4.5, 'consistencia': 50}
        
        # Proyección
        proy_local = (st_l['promedio_favor'] + st_v['promedio_contra']) / 2
        proy_visit = (st_v['promedio_favor'] + st_l['promedio_contra']) / 2
        total_proy = proy_local + proy_visit
        
        consistencia_media = (st_l.get('consistencia', 50) + st_v.get('consistencia', 50)) / 2
        
        if total_proy > 9.0 and consistencia_media > 65:
            rec = f"OVER {int(total_proy)} carreras"
            conf = min(90, 65 + int((total_proy - 8) * 8))
            etiqueta_verde = conf >= 75
        elif total_proy < 7.0 and consistencia_media > 70:
            rec = f"UNDER {int(total_proy)} carreras"
            conf = min(90, 70 + int((7 - total_proy) * 5))
            etiqueta_verde = conf >= 75
        elif abs(proy_local - proy_visit) >= 2.0 and consistencia_media > 60:
            ganador = local if proy_local > proy_visit else visitante
            rec = f"Run Line: {ganador} -1.5"
            conf = min(85, 60 + abs(proy_local - proy_visit) * 8)
            etiqueta_verde = conf >= 75
        else:
            ganador = local if proy_local > proy_visit else visitante
            rec = f"Moneyline: {ganador}"
            conf = min(80, 55 + abs(proy_local - proy_visit) * 5)
            etiqueta_verde = conf >= 75
        
        conf = int(conf)
        
        return {
            'recomendacion': rec,
            'confianza': conf,
            'etiqueta_verde': etiqueta_verde,
            'proyeccion_local': round(proy_local, 1),
            'proyeccion_visitante': round(proy_visit, 1),
            'total_proyectado': round(total_proy, 1),
            'consistencia': f"{consistencia_media:.0f}%"
        }
