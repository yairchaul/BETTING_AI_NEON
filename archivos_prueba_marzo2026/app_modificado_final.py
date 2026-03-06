# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(r'C:\Users\Yair\Desktop\BETTING_AI')

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from modules.elo_system import ELOSystem
from modules.odds_api_integrator_no_streamlit import OddsAPIIntegrator
from modules.parser_orden_exacto import ParserOrdenExacto
import pytesseract
from PIL import Image
import tempfile

class CustomPredictor:
    def __init__(self):
        self.elo = ELOSystem()
        self.odds_api = OddsAPIIntegrator()
        self.parser = ParserOrdenExacto()
        
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            image = image.convert('L')
            image = image.point(lambda x: 0 if x < 128 else 255)
            
            try:
                text = pytesseract.image_to_string(image, lang='spa')
            except:
                text = pytesseract.image_to_string(image, lang='eng')
            
            return text
        except Exception as e:
            return f"Error OCR: {e}"
    
    def predict_from_image(self, image_path):
        text = self.extract_text_from_image(image_path)
        matches = self.parser.parse_text(text)
        
        return {
            'matches': matches,
            'raw_text': text,
            'num_matches': len(matches)
        }

def american_to_decimal(american):
    if not american or american == 'N/A':
        return 2.0
    try:
        american = str(american).replace('+', '')
        american = int(american)
        if american > 0:
            return round(1 + (american / 100), 2)
        else:
            return round(1 + (100 / abs(american)), 2)
    except:
        return 2.0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.predictor = CustomPredictor()
        self.init_ui()
        self.current_image = None
    
    def init_ui(self):
        self.setWindowTitle("Analizador de Apuestas - Orden Exacto")
        self.setGeometry(100, 100, 1200, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        title = QLabel(" Analizador Profesional de Apuestas")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton(" Seleccionar imagen")
        self.btn_select.clicked.connect(self.select_image)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_analyze = QPushButton(" Analizar")
        self.btn_analyze.clicked.connect(self.analyze_image)
        self.btn_analyze.setEnabled(False)
        btn_layout.addWidget(self.btn_analyze)
        
        main_layout.addLayout(btn_layout)
        
        self.image_label = QLabel("No hay imagen seleccionada")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(250)
        self.image_label.setStyleSheet("border: 2px solid gray;")
        main_layout.addWidget(self.image_label)
        
        self.tabs = QTabWidget()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.results_text, " Resultados")
        
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)
        self.ocr_text.setFont(QFont("Consolas", 9))
        self.tabs.addTab(self.ocr_text, " Texto OCR")
        
        main_layout.addWidget(self.tabs)
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar captura", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.current_image = file_path
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
            result = self.predictor.predict_from_image(self.current_image)
            
            self.ocr_text.setText(f" TEXTO OCR:\n{'='*50}\n{result['raw_text']}")
            
            if result['num_matches'] == 0:
                self.results_text.setText(" No se detectaron partidos")
                return
            
            text = f" PARTIDOS DETECTADOS: {result['num_matches']}\n"
            text += "=" * 80 + "\n\n"
            
            # Tabla de resultados
            header = f"{'No.':4} {'Local':15} {'L':6} {'Empate':8} {'E':6} {'Visitante':20} {'V':6}\n"
            text += header
            text += "-" * 80 + "\n"
            
            for i, match in enumerate(result['matches'], 1):
                local = match.get('local', 'N/A')[:15]
                cuota_l = match.get('cuota_local', 'N/A')
                empate = match.get('empate', 'N/A')[:8]
                cuota_e = match.get('cuota_empate', 'N/A')
                visitante = match.get('visitante', 'N/A')[:20]
                cuota_v = match.get('cuota_visitante', 'N/A')
                
                text += f"{i:4} {local:15} {cuota_l:6} {empate:8} {cuota_e:6} {visitante:20} {cuota_v:6}\n"
            
            text += "\n" + "=" * 80 + "\n"
            text += "\n ODDS DECIMALES:\n"
            
            for i, match in enumerate(result['matches'], 1):
                dec_l = american_to_decimal(match.get('cuota_local', ''))
                dec_e = american_to_decimal(match.get('cuota_empate', ''))
                dec_v = american_to_decimal(match.get('cuota_visitante', ''))
                
                text += f"Partido {i}: Local {dec_l:.2f} | Empate {dec_e:.2f} | Visitante {dec_v:.2f}\n"
            
            self.results_text.setText(text)
            
        except Exception as e:
            self.results_text.setText(f" Error: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
