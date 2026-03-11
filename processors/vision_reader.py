"""
Vision Reader - Lector REAL de capturas de pantalla
Procesa imágenes y extrae texto usando OCR
"""
import os
import cv2
import numpy as np
import pytesseract
from typing import List
import sys
from pathlib import Path

# Asegurar ruta de tesseract (ajusta según tu instalación)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evento import Evento
from stats_engine import StatsEngine
from rule_engine import RuleEngine

# Importar procesadores
try:
    from processors.procesador_futbol import ProcesadorFutbol
    from processors.procesador_nba import ProcesadorNBA
    from processors.procesador_ufc import ProcesadorUFC
except ImportError as e:
    print(f"⚠️ Error importando procesadores: {e}")
    ProcesadorFutbol = None
    ProcesadorNBA = None
    ProcesadorUFC = None

class VisionReader:
    """Lee capturas de pantalla usando OCR y extrae eventos"""
    
    def __init__(self):
        self.stats_engine = StatsEngine()
        self.rule_engine = RuleEngine()
        
        # Inicializar procesadores por deporte
        self.procesadores = {
            'FUTBOL': ProcesadorFutbol() if ProcesadorFutbol else None,
            'NBA': ProcesadorNBA() if ProcesadorNBA else None,
            'UFC': ProcesadorUFC() if ProcesadorUFC else None
        }
        
        # Verificar que tesseract está disponible
        self._verificar_tesseract()
        
        print("✅ VisionReader inicializado con OCR")
    
    def _verificar_tesseract(self):
        """Verifica que Tesseract OCR está instalado"""
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR disponible")
        except Exception as e:
            print(f"❌ Tesseract NO disponible: {e}")
            print("   Instala desde: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def procesar_captura(self, ruta_imagen: str, deporte: str = "FUTBOL") -> List[Evento]:
        """
        Procesa una imagen y extrae eventos del deporte especificado
        
        Args:
            ruta_imagen: Ruta al archivo de imagen
            deporte: Deporte a procesar (FUTBOL, NBA, UFC)
            
        Returns:
            List[Evento]: Lista de eventos detectados
        """
        print(f"\n📸 Procesando imagen: {ruta_imagen}")
        
        if not os.path.exists(ruta_imagen):
            print(f"❌ Archivo no encontrado: {ruta_imagen}")
            return []
        
        # PASO 1: Leer imagen con OpenCV
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            print(f"❌ No se pudo leer la imagen: {ruta_imagen}")
            return []
        
        # PASO 2: Preprocesar imagen para mejorar OCR
        imagen_procesada = self._preprocesar_imagen(imagen)
        
        # PASO 3: Extraer texto con OCR
        texto_extraido = self._extraer_texto(imagen_procesada)
        
        print(f"📝 Texto extraído ({len(texto_extraido)} caracteres)")
        print("-" * 50)
        print(texto_extraido[:500])  # Mostrar primeros 500 chars
        print("-" * 50)
        
        # PASO 4: Procesar según deporte
        eventos = []
        procesador = self.procesadores.get(deporte)
        
        if procesador:
            # El procesador específico extrae los eventos del texto
            eventos_raw = procesador.procesar(texto_extraido, ruta_imagen)
            
            # PASO 5: Enriquecer con estadísticas y reglas
            for evento in eventos_raw:
                # Calcular probabilidades
                probabilidades = self.stats_engine.calcular(evento)
                evento.mercados = probabilidades
                
                # Aplicar reglas para obtener picks
                picks = self.rule_engine.aplicar_reglas(evento, probabilidades)
                evento.value_bets = picks
                
                eventos.append(evento)
                
            print(f"✅ {len(eventos)} eventos detectados")
        else:
            print(f"❌ No hay procesador para {deporte}")
        
        return eventos
    
    def _preprocesar_imagen(self, imagen):
        """Preprocesa imagen para mejorar OCR"""
        # Convertir a escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro para reducir ruido
        suavizada = cv2.GaussianBlur(gris, (5, 5), 0)
        
        # Binarizar (blanco y negro)
        _, binaria = cv2.threshold(suavizada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Aumentar contraste
        kernel = np.ones((1, 1), np.uint8)
        dilatada = cv2.dilate(binaria, kernel, iterations=1)
        erosionada = cv2.erode(dilatada, kernel, iterations=1)
        
        return erosionada
    
    def _extraer_texto(self, imagen):
        """Extrae texto usando Tesseract OCR"""
        # Configuración para español y números
        config = '--oem 3 --psm 6 -l spa+eng'
        
        try:
            texto = pytesseract.image_to_string(imagen, config=config)
            return texto
        except Exception as e:
            print(f"❌ Error en OCR: {e}")
            return ""

# Función de compatibilidad
def procesar_imagen(ruta_imagen: str, deporte: str = "FUTBOL") -> List[Evento]:
    """Función de compatibilidad"""
    vision = VisionReader()
    return vision.procesar_captura(ruta_imagen, deporte)

if __name__ == "__main__":
    # Prueba rápida
    import sys
    if len(sys.argv) > 1:
        vision = VisionReader()
        eventos = vision.procesar_captura(sys.argv[1])
        for e in eventos:
            print(f"  - {e.equipo_local} vs {e.equipo_visitante}")
    else:
        print("Uso: python vision_reader.py <ruta_imagen>")
