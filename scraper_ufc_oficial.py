# -*- coding: utf-8 -*-
"""
SCRAPER UFC OFICIAL - Con selectores exactos de ufcespanol.com
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from datetime import datetime

class ScraperUFCOficial:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self._init_db()
    
    def _init_db(self):
        """Inicializa tabla de peleadores UFC"""
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
        """Convierte pulgadas a centimetros"""
        try:
            return int(float(pulgadas) * 2.54)
        except:
            return 0
    
    def obtener_peleador_por_nombre(self, nombre):
        """Busca un peleador en ufcespanol.com por nombre"""
        nombre_clean = nombre.lower().replace(' ', '-').replace('.', '').replace("'", "")
        url = f"https://www.ufcespanol.com/athlete/{nombre_clean}"
        
        print(f"   🔍 Buscando: {nombre} -> {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                print(f"   ⚠️ No encontrado (HTTP {response.status_code})")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
            
            # Buscar la sección de información (c-bio__info)
            info_section = soup.find('div', class_='c-bio__info')
            if info_section:
                items = info_section.find_all('div', class_='c-bio__info-item')
                for item in items:
                    label = item.find('div', class_='c-bio__info-label')
                    value = item.find('div', class_='c-bio__info-value')
                    if label and value:
                        label_text = label.text.strip().lower()
                        value_text = value.text.strip()
                        
                        if 'alto' in label_text or 'height' in label_text:
                            datos['altura'] = value_text
                        elif 'peso' in label_text or 'weight' in label_text:
                            datos['peso'] = value_text
                        elif 'alcance' in label_text or 'reach' in label_text:
                            datos['alcance'] = value_text
                        elif 'postura' in label_text or 'stance' in label_text:
                            datos['postura'] = value_text
            
            # Si no encontró en c-bio__info, buscar en otra estructura
            if datos['altura'] == 'N/A':
                # Buscar por texto directo
                page_text = soup.get_text()
                altura_match = re.search(r'ALTO\s*(\d+\.?\d*)', page_text, re.IGNORECASE)
                if altura_match:
                    datos['altura'] = altura_match.group(1)
                
                peso_match = re.search(r'PESO\s*(\d+\.?\d*)', page_text, re.IGNORECASE)
                if peso_match:
                    datos['peso'] = peso_match.group(1)
                
                alcance_match = re.search(r'ALCANCE\s*(\d+\.?\d*)', page_text, re.IGNORECASE)
                if alcance_match:
                    datos['alcance'] = alcance_match.group(1)
            
            # Calcular KO rate
            ko_count = 0
            total_wins = 0
            
            # Buscar "Wins by Knockout"
            ko_match = re.search(r'Wins by Knockout\s*(\d+)', page_text, re.IGNORECASE)
            if ko_match:
                ko_count = int(ko_match.group(1))
            
            # Buscar "Wins by Submission"
            sub_match = re.search(r'Wins by Submission\s*(\d+)', page_text, re.IGNORECASE)
            if sub_match:
                total_wins = ko_count + int(sub_match.group(1))
            
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
        """Guarda o actualiza peleador en BD"""
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
        """Actualiza todos los peleadores que tienen eventos próximos"""
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
                    datos = self.obtener_peleador_por_nombre(p1)
                    if datos:
                        self.guardar_peleador(datos)
                    time.sleep(1)
                
                if p2:
                    print(f"\n📡 Procesando: {p2}")
                    datos = self.obtener_peleador_por_nombre(p2)
                    if datos:
                        self.guardar_peleador(datos)
                    time.sleep(1)
        else:
            print("⚠️ No hay eventos UFC cargados. Ejecuta primero: python cargar_ufc_json.py")
        
        print("\n✅ Actualizacion completada")

def actualizar_ufc():
    scraper = ScraperUFCOficial()
    scraper.actualizar_todos_peleadores()

if __name__ == "__main__":
    actualizar_ufc()
