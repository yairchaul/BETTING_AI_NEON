# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(r'C:\Users\Yair\Desktop\BETTING_AI')

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QMessageBox,
                             QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from modules.elo_system import ELOSystem
from modules.odds_api_integrator_no_streamlit import OddsAPIIntegrator
from modules.parser_caliente_doble_bloque import CalienteDobleBloqueParser
import pytesseract
from PIL import Image
import tempfile

class CustomPredictor:
    def __init__(self):
        self.elo = ELOSystem()
        self.odds_api = OddsAPIIntegrator()
        self.parser = CalienteDobleBloqueParser()
        
        # Configurar Tesseract
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print(f" Tesseract no encontrado en {tesseract_path}")
    
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            # Mejorar imagen para OCR
            image = image.convert('L')  # Escala de grises
            image = image.point(lambda x: 0 if x < 128 else 255)  # Binarizar
            
            # Intentar con español, fallback a inglés
            try:
                text = pytesseract.image_to_string(image, lang='spa')
            except:
                text = pytesseract.image_to_string(image, lang='eng')
            
            return text
        except Exception as e:
            return f"Error OCR: {e}"
    
    def predict_from_image(self, image_path):
        # Extraer texto
        text = self.extract_text_from_image(image_path)
        
        # Parsear
        matches = self.parser.parse_text(text)
        
        # Devolver tanto los matches como el texto crudo
        return {
            'matches': matches,
            'raw_text': text,
            'num_matches': len(matches)
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.predictor = CustomPredictor()
        self.init_ui()
        self.current_image = None
    
    def init_ui(self):
        self.setWindowTitle("Analizador de Apuestas - Caliente.mx")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Título
        title = QLabel(" Analizador Profesional de Apuestas")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton(" Seleccionar imagen")
        self.btn_select.clicked.connect(self.select_image)
        self.btn_select.setMinimumHeight(40)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_analyze = QPushButton(" Analizar")
        self.btn_analyze.clicked.connect(self.analyze_image)
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setMinimumHeight(40)
        btn_layout.addWidget(self.btn_analyze)
        
        main_layout.addLayout(btn_layout)
        
        # Preview de imagen
        self.image_label = QLabel("No hay imagen seleccionada")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(250)
        self.image_label.setStyleSheet("border: 2px solid gray; background-color: #f0f0f0;")
        main_layout.addWidget(self.image_label)
        
        # Tabs para resultados
        self.tabs = QTabWidget()
        
        # Tab de resultados
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.results_text, " Resultados")
        
        # Tab de texto OCR
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)
        self.ocr_text.setFont(QFont("Consolas", 9))
        self.tabs.addTab(self.ocr_text, " Texto OCR")
        
        main_layout.addWidget(self.tabs)
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar captura de Caliente.mx", 
            "",
            "Imágenes (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.current_image = file_path
            # Mostrar preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(600, 250, Qt.AspectRatioMode.KeepAspectRatio)
                self.image_label.setPixmap(scaled)
            self.btn_analyze.setEnabled(True)
            self.results_text.clear()
            self.ocr_text.clear()
    
    def analyze_image(self):
        if not self.current_image:
            return
        
        self.results_text.setText(" Analizando...")
        QApplication.processEvents()
        
        try:
            # Predecir
            result = self.predictor.predict_from_image(self.current_image)
            
            # Mostrar texto OCR
            ocr_display = " TEXTO EXTRAÍDO POR TESSERACT:\n"
            ocr_display += "=" * 60 + "\n"
            ocr_display += result['raw_text']
            self.ocr_text.setText(ocr_display)
            
            # Mostrar resultados
            if result['num_matches'] == 0:
                self.results_text.setText(" No se detectaron partidos en la imagen")
                return
            
            text = f" PARTIDOS DETECTADOS: {result['num_matches']}\n"
            text += "=" * 60 + "\n\n"
            
            for i, match in enumerate(result['matches'], 1):
                text += f" Partido {i}:\n"
                text += f"   Local: {match.get('local', 'N/A')}\n"
                text += f"   Cuota Local: {match.get('cuota_local', 'N/A')}\n"
                text += f"   Empate: {match.get('empate', 'N/A')}\n"
                text += f"   Cuota Empate: {match.get('cuota_empate', 'N/A')}\n"
                text += f"   Visitante: {match.get('visitante', 'N/A')}\n"
                text += f"   Cuota Visitante: {match.get('cuota_visitante', 'N/A')}\n"
                
                # Intentar obtener ELO
                try:
                    home = match.get('local', '')
                    away = match.get('visitante', '')
                    if home and away:
                        elo_probs = self.predictor.elo.get_win_probability(home, away)
                        text += f"    ELO: Local {elo_probs['home']:.1%}, "
                        text += f"Empate {elo_probs['draw']:.1%}, "
                        text += f"Visitante {elo_probs['away']:.1%}\n"
                except:
                    pass
                
                text += "\n" + "-" * 50 + "\n\n"
            
            self.results_text.setText(text)
            
        except Exception as e:
            self.results_text.setText(f" Error: {str(e)}")
            import traceback
            self.ocr_text.setText(traceback.format_exc())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
