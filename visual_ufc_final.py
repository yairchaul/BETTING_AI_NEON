# En la función _obtener_datos_peleador, agrega debug
def _obtener_datos_peleador(self, nombre):
    """Obtiene todos los datos del peleador desde BD"""
    if not nombre:
        return {'record': 'N/A', 'altura': 'N/A', 'alcance': 'N/A', 'ko_rate': 0, 'odds': 'N/A'}
    
    try:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Buscar coincidencias
        c.execute("""
            SELECT record, altura, alcance, ko_rate, odds 
            FROM peleadores_ufc 
            WHERE nombre = ? OR nombre LIKE ? OR ? LIKE '%' || nombre || '%'
            LIMIT 1
        """, (nombre, f"%{nombre}%", nombre))
        row = c.fetchone()
        
        if not row:
            # Intentar búsqueda más flexible
            c.execute("""
                SELECT record, altura, alcance, ko_rate, odds 
                FROM peleadores_ufc 
                WHERE lower(nombre) LIKE lower(?)
                LIMIT 1
            """, (f"%{nombre.split()[0]}%",))
            row = c.fetchone()
        
        conn.close()
        
        if row:
            return {
                'record': row[0] if row[0] else 'N/A',
                'altura': row[1] if row[1] else 'N/A',
                'alcance': row[2] if row[2] else 'N/A',
                'ko_rate': int(float(row[3]) * 100) if row[3] else 0,
                'odds': row[4] if row[4] else 'N/A'
            }
        
        # Si no encuentra, retornar N/A
        return {'record': 'N/A', 'altura': 'N/A', 'alcance': 'N/A', 'ko_rate': 0, 'odds': 'N/A'}
        
    except Exception as e:
        logger.debug(f"Error obteniendo datos de {nombre}: {e}")
        return {'record': 'N/A', 'altura': 'N/A', 'alcance': 'N/A', 'ko_rate': 0, 'odds': 'N/A'}
