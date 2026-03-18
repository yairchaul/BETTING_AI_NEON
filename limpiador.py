"""
LIMPIADOR - Identifica qué módulos tenemos y cuáles podemos eliminar
"""
import os
import glob

print("🔍 ANALIZANDO MÓDULOS EXISTENTES")
print("=" * 60)

# Módulos esenciales (los que usamos)
esenciales = [
    "espn_data_pipeline.py",
    "bet_tracker.py",
    "visual_nba_mejorado.py",
    "visual_ufc.py",
    "visual_futbol.py",
    "analizador_nba.py",
    "analizador_gemini_nba.py",
    "analizador_premium.py",
    "main_vision_completo.py"
]

print("\n✅ MÓDULOS ESENCIALES:")
for e in esenciales:
    if os.path.exists(e):
        print(f"  ✓ {e}")

print("\n📁 OTROS MÓDULOS .py ENCONTRADOS:")
otros = []
for py in glob.glob("*.py"):
    if py not in esenciales and py != "limpiador.py":
        otros.append(py)

for o in sorted(otros):
    print(f"  • {o}")

print("\n" + "=" * 60)
print("💡 RECOMENDACIÓN:")
print("Puedes eliminar los archivos marcados con • si ya no los necesitas")
print("o moverlos a una carpeta 'backup' para seguridad.")
