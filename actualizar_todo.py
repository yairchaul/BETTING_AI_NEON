# -*- coding: utf-8 -*-
"""
SCRIPT MAESTRO - Actualiza todos los datos automáticamente
Ejecuta: python actualizar_todo.py
"""

import subprocess
import sys
import os
from datetime import datetime

def ejecutar_script(script_name, descripcion):
    print(f"\n{'='*50}")
    print(f"📡 {descripcion}")
    print(f"{'='*50}")
    try:
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Errores:\n{result.stderr}")
        return True
    except Exception as e:
        print(f"❌ Error en {script_name}: {e}")
        return False

def main():
    print(f"\n🚀 INICIANDO ACTUALIZACIÓN AUTOMÁTICA - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    scripts = [
        ("scraper_ufc_final.py", "Actualizando datos de peleadores UFC..."),
        ("scraper_odds_ufc_definitivo.py", "Actualizando odds de Action Network..."),
        ("scraper_mlb_dinamico.py", "Actualizando datos MLB..."),
        ("scraper_futbol_dinamico.py", "Actualizando datos fútbol..."),
    ]
    
    for script, desc in scripts:
        if os.path.exists(script):
            ejecutar_script(script, desc)
        else:
            print(f"⚠️ {script} no encontrado")
    
    print(f"\n✅ ACTUALIZACIÓN COMPLETADA - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
