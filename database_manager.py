"""
DATABASE MANAGER - Con Bitácora de Errores y Z-Score
"""
import sqlite3
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='data/betting_stats.db'):
        self.db_path = db_path
        self._crear_tablas_auditoria()
    
    def _crear_tablas_auditoria(self):
        """Crea tablas de auditoría para el aprendizaje automático"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS auditoria_ia (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        partido TEXT,
                        deporte TEXT,
                        proyectado REAL,
                        real REAL,
                        error REAL,
                        z_score REAL,
                        etiqueta_verde INTEGER DEFAULT 0
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS estadisticas_equipos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_equipo TEXT,
                        deporte TEXT,
                        promedio_pts REAL,
                        desviacion_std REAL,
                        ultima_actualizacion TEXT,
                        partidos_analizados INTEGER
                    )
                ''')
                conn.commit()
                logger.info("Tablas de auditoría creadas/verificadas")
        except Exception as e:
            logger.error(f"Error creando tablas auditoría: {e}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones seguras"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except Exception as e:
            logger.error(f"Error en conexión DB: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def calcular_estadisticas_equipo(self, equipo, deporte):
        """Calcula promedio y desviación estándar de un equipo"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT puntos_favor 
                    FROM historial_equipos 
                    WHERE nombre_equipo = ? AND deporte = ?
                    ORDER BY fecha DESC LIMIT 10
                """, (equipo, deporte))
                rows = cursor.fetchall()
                
                if rows and len(rows) >= 5:
                    import numpy as np
                    puntos = [r[0] for r in rows]
                    promedio = np.mean(puntos)
                    desviacion = np.std(puntos)
                    return {
                        'promedio': round(promedio, 1),
                        'desviacion': round(desviacion, 1),
                        'muestra': len(puntos),
                        'ultimos': puntos[:5]
                    }
                return None
        except Exception as e:
            logger.error(f"Error calculando estadísticas de {equipo}: {e}")
            return None
    
    def registrar_error_proyeccion(self, partido, deporte, proyectado, real, z_score, etiqueta_verde=False):
        """Registra error para que la IA aprenda de sus fallos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                error = abs(proyectado - real)
                from datetime import datetime
                fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                    INSERT INTO auditoria_ia 
                    (fecha, partido, deporte, proyectado, real, error, z_score, etiqueta_verde)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (fecha, partido, deporte, proyectado, real, error, z_score, 1 if etiqueta_verde else 0))
                conn.commit()
                logger.info(f"Error registrado: {partido} - Error: {error} puntos")
        except Exception as e:
            logger.error(f"Error registrando error: {e}")
    
    def obtener_historial_nba(self, equipo, limite=5):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT puntos_favor, puntos_contra 
                    FROM historial_equipos 
                    WHERE nombre_equipo = ? AND deporte = 'nba'
                    ORDER BY fecha DESC LIMIT ?
                """, (equipo, limite))
                rows = cursor.fetchall()
                
                if rows and len(rows) >= 3:
                    import numpy as np
                    pts_f = [r[0] for r in rows]
                    return {
                        'puntos_por_partido': np.mean(pts_f),
                        'ultimos_puntos': pts_f,
                        'desviacion': np.std(pts_f),
                        'registros': len(rows)
                    }
                return None
        except Exception as e:
            logger.error(f"Error obteniendo historial NBA de {equipo}: {e}")
            return None
    
    def obtener_historial_mlb(self, equipo, limite=5):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT puntos_favor, puntos_contra 
                    FROM historial_equipos 
                    WHERE nombre_equipo = ? AND deporte = 'mlb'
                    ORDER BY fecha DESC LIMIT ?
                """, (equipo, limite))
                rows = cursor.fetchall()
                
                if rows and len(rows) >= 3:
                    import numpy as np
                    pts_f = [r[0] for r in rows]
                    return {
                        'carreras_por_partido': np.mean(pts_f),
                        'ultimas_carreras': pts_f,
                        'desviacion': np.std(pts_f)
                    }
                return None
        except Exception as e:
            logger.error(f"Error obteniendo historial MLB de {equipo}: {e}")
            return None
    
    def obtener_historial_futbol(self, equipo, limite=5):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT puntos_favor 
                    FROM historial_equipos 
                    WHERE nombre_equipo = ? AND deporte = 'futbol'
                    ORDER BY fecha DESC LIMIT ?
                """, (equipo, limite))
                rows = cursor.fetchall()
                
                if rows and len(rows) >= 3:
                    return [r[0] for r in rows]
                return None
        except Exception as e:
            logger.error(f"Error obteniendo historial fútbol de {equipo}: {e}")
            return None
    
    def obtener_peleador_ufc(self, nombre):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT nombre, record, altura, peso, alcance, postura, ko_rate, grappling
                    FROM peleadores_ufc 
                    WHERE nombre LIKE ? OR nombre = ?
                    LIMIT 1
                """, (f"%{nombre}%", nombre))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'nombre': row[0],
                        'record': row[1] if row[1] else '0-0-0',
                        'altura': row[2] if row[2] else 'N/A',
                        'peso': row[3] if row[3] else 'N/A',
                        'alcance': row[4] if row[4] else 'N/A',
                        'postura': row[5] if row[5] else 'Desconocida',
                        'ko_rate': row[6] if row[6] else 0.5,
                        'grappling': row[7] if row[7] else 0.5
                    }
                return None
        except Exception as e:
            logger.error(f"Error obteniendo peleador UFC {nombre}: {e}")
            return None
    
    def obtener_estadisticas_aprendizaje(self, deporte):
        """Obtiene estadísticas de aprendizaje para mejorar predicciones"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(error) as error_medio, 
                           COUNT(*) as total_errores,
                           AVG(z_score) as z_medio
                    FROM auditoria_ia 
                    WHERE deporte = ? AND fecha > date('now', '-30 days')
                """, (deporte,))
                row = cursor.fetchone()
                return {
                    'error_medio': round(row[0], 1) if row[0] else 0,
                    'total_errores': row[1] if row[1] else 0,
                    'z_medio': round(row[2], 2) if row[2] else 0
                }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas aprendizaje: {e}")
            return {'error_medio': 0, 'total_errores': 0, 'z_medio': 0}

# Instancia global
db = DatabaseManager()
