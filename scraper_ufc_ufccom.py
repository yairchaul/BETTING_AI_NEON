# -*- coding: utf-8 -*-
"""
SCRAPER UFC DESDE UFC.COM - Versión que sí funcionó
Usa ufcespanol.com que tiene datos de los peleadores
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from datetime import datetime

class ScraperUFCUfcCom:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peleadores_ufc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                record TEXT,
                altura TEXT,
                peso TEXT,
                alcance TEXT,
                postura TEXT,
                ko_rate REAL,
                grappling REAL,
                ultima_actualizacion TEXT,
                url TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Tabla peleadores_ufc lista")
    
    def _pulgadas_a_cm(self, pulgadas):
        try:
            return int(float(pulgadas) * 2.54)
        except:
            return 0
    
    def _extraer_valor(self, texto, campo):
        """Extrae valor de un campo en el texto"""
        patron = rf'{campo}\s*(\d+\.?\d*)'
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def obtener_peleador(self, nombre):
        """Obtiene datos del peleador desde ufcespanol.com"""
        nombre_clean = nombre.lower().replace(' ', '-').replace('.', '').replace("'", "")
        url = f"https://www.ufcespanol.com/athlete/{nombre_clean}"
        
        print(f"   🔍 Buscando: {nombre} -> {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                print(f"   ⚠️ No encontrado (HTTP {response.status_code})")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            datos = {
                'nombre': nombre,
                'record': '0-0-0',
                'altura': 'N/A',
                'peso': 'N/A',
                'alcance': 'N/A',
                'postura': 'Desconocida',
                'ko_rate': 0.5,
                'url': url
            }
            
            # Buscar en la sección c-bio__info
            info_section = soup.find('div', class_='c-bio__info')
            if info_section:
                items = info_section.find_all('div', class_='c-bio__info-item')
                for item in items:
                    label = item.find('div', class_='c-bio__info-label')
                    value = item.find('div', class_='c-bio__info-value')
                    if label and value:
                        label_text = label.text.strip().lower()
                        value_text = value.text.strip()
                        
                        if 'alto' in label_text:
                            datos['altura'] = value_text
                        elif 'peso' in label_text:
                            datos['peso'] = value_text
                        elif 'alcance' in label_text:
                            datos['alcance'] = value_text
                        elif 'postura' in label_text:
                            datos['postura'] = value_text
            
            # Si no encontró en c-bio__info, buscar por regex en el texto
            if datos['altura'] == 'N/A':
                altura_val = self._extraer_valor(page_text, 'ALTO')
                if altura_val:
                    altura_num = float(altura_val)
                    if 50 <= altura_num <= 85:  # Validar rango de altura (pulgadas)
                        datos['altura'] = altura_val
                    else:
                        # Buscar altura en formato de texto
                        altura_match = re.search(r'ALTURA\s*(\d+\.?\d*)\s*in', page_text, re.IGNORECASE)
                        if altura_match:
                            datos['altura'] = altura_match.group(1)
            
            if datos['alcance'] == 'N/A':
                alcance_val = self._extraer_valor(page_text, 'ALCANCE')
                if alcance_val:
                    alcance_num = float(alcance_val)
                    if 50 <= alcance_num <= 85:  # Rango válido para alcance
                        datos['alcance'] = alcance_val
            
            # Calcular KO rate desde el historial
            ko_match = re.search(r'Wins by Knockout\s*(\d+)', page_text, re.IGNORECASE)
            sub_match = re.search(r'Wins by Submission\s*(\d+)', page_text, re.IGNORECASE)
            
            ko_count = int(ko_match.group(1)) if ko_match else 0
            sub_count = int(sub_match.group(1)) if sub_match else 0
            total_wins = ko_count + sub_count
            
            if total_wins > 0:
                datos['ko_rate'] = min(0.9, ko_count / total_wins)
            
            # Buscar record
            record_match = re.search(r'(\d+)-(\d+)-(\d+)', page_text)
            if record_match:
                datos['record'] = f"{record_match.group(1)}-{record_match.group(2)}-{record_match.group(3)}"
            
            altura_cm = 0
            alcance_cm = 0
            if datos['altura'] != 'N/A':
                try:
                    altura_cm = self._pulgadas_a_cm(float(datos['altura']))
                except:
                    pass
            if datos['alcance'] != 'N/A':
                try:
                    alcance_cm = self._pulgadas_a_cm(float(datos['alcance']))
                except:
                    pass
            
            print(f"   ✅ {nombre}: Altura={datos['altura']}in ({altura_cm}cm), Alcance={datos['alcance']}in ({alcance_cm}cm), KO={int(datos['ko_rate']*100)}%")
            return datos
            
        except Exception as e:
            print(f"   ⚠️ Error obteniendo {nombre}: {e}")
            return None
    
    def guardar_peleador(self, datos):
        if not datos:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO peleadores_ufc 
            (nombre, record, altura, peso, alcance, postura, ko_rate, ultima_actualizacion, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['nombre'],
            datos['record'],
            datos.get('altura', 'N/A'),
            datos.get('peso', 'N/A'),
            datos.get('alcance', 'N/A'),
            datos['postura'],
            datos['ko_rate'],
            datetime.now().strftime("%Y%m%d"),
            datos.get('url', '')
        ))
        
        conn.commit()
        conn.close()
    
    def actualizar_todos_peleadores(self):
        """Actualiza todos los peleadores desde eventos UFC"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cartelera FROM eventos_ufc ORDER BY fecha DESC LIMIT 1")
        evento = cursor.fetchone()
        conn.close()
        
        if evento and evento[0]:
            import json
            cartelera = json.loads(evento[0])
            
            for pelea in cartelera:
                p1 = pelea.get('peleador1')
                p2 = pelea.get('peleador2')
                
                if p1:
                    print(f"\n📡 Procesando: {p1}")
                    datos = self.obtener_peleador(p1)
                    if datos:
                        self.guardar_peleador(datos)
                    time.sleep(1)
                
                if p2:
                    print(f"\n📡 Procesando: {p2}")
                    datos = self.obtener_peleador(p2)
                    if datos:
                        self.guardar_peleador(datos)
                    time.sleep(1)
        else:
            print("⚠️ No hay eventos UFC cargados. Ejecuta primero: python cargar_ufc_json.py")
        
        print("\n✅ Actualizacion completada")

def actualizar_ufc():
    scraper = ScraperUFCUfcCom()
    scraper.actualizar_todos_peleadores()

if __name__ == "__main__":
    actualizar_ufc()
