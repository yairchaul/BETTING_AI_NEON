# -*- coding: utf-8 -*-
"""
SCRAPER UFC DESDE ESPN - Extrae datos de peleadores desde ESPN
URL base: https://www.espn.com/mma/fighter/_/id/{id}/{nombre}
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from datetime import datetime

class ScraperUFCEspn:
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
                url TEXT,
                espn_id TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Tabla peleadores_ufc lista")
    
    def _extraer_numero(self, texto):
        """Extrae numero de un string como '1.93 m'"""
        if not texto:
            return 0
        nums = re.findall(r'(\d+\.?\d*)', str(texto))
        return float(nums[0]) if nums else 0
    
    def _metros_a_cm(self, metros):
        """Convierte metros a centimetros"""
        try:
            return int(float(metros) * 100)
        except:
            return 0
    
    def _buscar_peleador_por_nombre(self, nombre):
        """Busca el ID del peleador en ESPN"""
        nombre_clean = nombre.lower().replace(' ', '-').replace('.', '')
        # Primero buscar en la lista de peleadores
        url = f"https://www.espn.com/mma/fighter/_/name/{nombre_clean}"
        return url
    
    def obtener_peleador_por_nombre(self, nombre):
        """Busca un peleador en ESPN.com por nombre"""
        nombre_clean = nombre.lower().replace(' ', '-').replace('.', '').replace("'", "")
        url = f"https://www.espn.com/mma/fighter/_/name/{nombre_clean}"
        
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
            
            # Buscar el record
            record_elem = soup.find('div', class_='record')
            if record_elem:
                datos['record'] = record_elem.text.strip()
            else:
                # Buscar en el encabezado
                header = soup.find('div', class_='fighter-header')
                if header:
                    record_text = header.find('span', class_='record')
                    if record_text:
                        datos['record'] = record_text.text.strip()
            
            # Buscar la sección de estadísticas
            stats_section = soup.find('div', class_='fighter-stats')
            if stats_section:
                # Altura
                height_elem = stats_section.find('div', class_='height')
                if height_elem:
                    altura_m = self._extraer_numero(height_elem.text)
                    if altura_m > 0:
                        datos['altura'] = f"{altura_m:.2f}m"
                        datos['altura_cm'] = self._metros_a_cm(altura_m)
                
                # Peso
                weight_elem = stats_section.find('div', class_='weight')
                if weight_elem:
                    peso_kg = self._extraer_numero(weight_elem.text)
                    if peso_kg > 0:
                        datos['peso'] = f"{peso_kg:.0f}kg"
                
                # Alcance
                reach_elem = stats_section.find('div', class_='reach')
                if reach_elem:
                    alcance_m = self._extraer_numero(reach_elem.text)
                    if alcance_m > 0:
                        datos['alcance'] = f"{alcance_m:.2f}m"
                        datos['alcance_cm'] = self._metros_a_cm(alcance_m)
                
                # Postura
                stance_elem = stats_section.find('div', class_='stance')
                if stance_elem:
                    datos['postura'] = stance_elem.text.strip()
            
            # Si no encontró stats, buscar en otra estructura
            if datos['altura'] == 'N/A':
                # Buscar por texto directo
                page_text = soup.get_text()
                altura_match = re.search(r'ALTURA\s*(\d+\.?\d*)\s*m', page_text, re.IGNORECASE)
                if altura_match:
                    altura_m = float(altura_match.group(1))
                    datos['altura'] = f"{altura_m:.2f}m"
                    datos['altura_cm'] = self._metros_a_cm(altura_m)
                
                peso_match = re.search(r'PESO\s*(\d+\.?\d*)\s*kg', page_text, re.IGNORECASE)
                if peso_match:
                    datos['peso'] = f"{peso_match.group(1)}kg"
                
                alcance_match = re.search(r'ALCANCE\s*(\d+\.?\d*)\s*m', page_text, re.IGNORECASE)
                if alcance_match:
                    alcance_m = float(alcance_match.group(1))
                    datos['alcance'] = f"{alcance_m:.2f}m"
                    datos['alcance_cm'] = self._metros_a_cm(alcance_m)
            
            # Calcular KO rate
            page_text = soup.get_text()
            ko_match = re.search(r'(\d+)\s*KO/TKO', page_text, re.IGNORECASE)
            if ko_match:
                ko_count = int(ko_match.group(1))
                # Buscar total de victorias
                record_parts = datos['record'].split('-')
                if len(record_parts) >= 1:
                    wins = int(record_parts[0]) if record_parts[0].isdigit() else 0
                    if wins > 0:
                        datos['ko_rate'] = min(0.9, ko_count / wins)
            
            altura_cm = datos.get('altura_cm', 0)
            alcance_cm = datos.get('alcance_cm', 0)
            
            print(f"   ✅ {nombre}: Altura={datos['altura']} ({altura_cm}cm), Alcance={datos['alcance']} ({alcance_cm}cm), Record={datos['record']}")
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
    scraper = ScraperUFCEspn()
    scraper.actualizar_todos_peleadores()

if __name__ == "__main__":
    actualizar_ufc()
