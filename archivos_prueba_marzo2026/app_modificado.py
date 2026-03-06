# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(r'C:\Users\Yair\Desktop\BETTING_AI')

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QMessageBox,
                             QFileDialog, QTabWidget, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

# Importar tus modulos
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
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            pass
    
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            image = image.convert('L')
            text = pytesseract.image_to_string(image, lang='spa')
            return text
        except Exception as e:
            return f"Error OCR: {e}"
    
    def predict_from_image(self, image_path):
        text = self.extract_text_from_image(image_path)
        matches = self.parser.parse_text(text)
        
        predictions = []
        for match in matches:
            home = match.get('local', '')
            away = match.get('visitante', '')
            
            if home and away:
                elo_probs = self.elo.get_win_probability(home, away)
                odds = self.odds_api.get_live_odds(home, away)
                
                predictions.append({
                    'match': f"{home} vs {away}",
                    'elo_probs': elo_probs,
                    'odds': odds,
                    'raw_text': text[:200]
                })
        
        return predictions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.predictor = CustomPredictor()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Analizador de Apuestas")
        self.setGeometry(100, 100, 1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Titulo
        title = QLabel("Analizador Profesional de Apuestas")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("Seleccionar imagen")
        self.btn_select.clicked.connect(self.select_image)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_analyze = QPushButton("Analizar")
        self.btn_analyze.clicked.connect(self.analyze_image)
        self.btn_analyze.setEnabled(False)
        btn_layout.addWidget(self.btn_analyze)
        
        layout.addLayout(btn_layout)
        
        # Preview de imagen
        self.image_label = QLabel("No hay imagen seleccionada")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(self.image_label)
        
        # Resultados
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results)
        
        self.current_image = None
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imagenes (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.current_image = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio)
                self.image_label.setPixmap(scaled)
            self.btn_analyze.setEnabled(True)
    
    def analyze_image(self):
        if not self.current_image:
            return
        
        self.results.setText("Analizando...")
        try:
            predictions = self.predictor.predict_from_image(self.current_image)
            
            text = "RESULTADOS DEL ANALISIS\n"
            text += "=" * 60 + "\n\n"
            
            for pred in predictions:
                text += f"Partido: {pred['match']}\n"
                text += f"   Probabilidades ELO: Local {pred['elo_probs']['home']:.1%}, "
                text += f"Empate {pred['elo_probs']['draw']:.1%}, "
                text += f"Visitante {pred['elo_probs']['away']:.1%}\n\n"
            
            self.results.setText(text)
            
        except Exception as e:
            self.results.setText(f"Error: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
