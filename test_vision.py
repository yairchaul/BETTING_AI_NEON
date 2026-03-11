"""
Prueba de vision_reader con procesador de fútbol
"""
import sys
from pathlib import Path
from processors.vision_reader import VisionReader

print("="*60)
print("🧪 PRUEBA VISION READER + FÚTBOL")
print("="*60)

# Crear vision reader
vision = VisionReader()

# Buscar capturas en el directorio
capturas = list(Path(".").glob("*.png")) + list(Path(".").glob("*.jpg"))
print(f"\n📁 Capturas encontradas: {len(capturas)}")

for captura in capturas[:3]:  # Probar primeras 3
    print(f"\n🔍 Procesando: {captura.name}")
    eventos = vision.procesar_captura(str(captura))
    
    print(f"   Eventos totales: {len(eventos)}")
    for evento in eventos:
        print(f"   - {evento}")

print("\n✅ PRUEBA COMPLETADA")
