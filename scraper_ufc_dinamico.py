# -*- coding: utf-8 -*-
"""
SCRAPER UFC DINÁMICO - Busca IDs de ESPN automáticamente
No usa IDs fijos, los obtiene dinámicamente desde la búsqueda de ESPN
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
import json
from datetime import datetime
from urllib.parse import quote

class ScraperUFCDinamico:
    def __init__(self, db_path="data/betting_stats.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
        self._init_db()
        self.cache_ids = self._cargar_cache_ids()
    
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
                url TEXT,
                espn_id TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Tabla peleadores_ufc lista")
    
    def _cargar_cache_ids(self):
        """Carga IDs de la BD existente para no buscar repetidos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, espn_id FROM peleadores_ufc WHERE espn_id IS NOT NULL AND espn_id != ''")
            rows = cursor.fetchall()
            conn.close()
            return {row[0].lower(): row[1] for row in rows}
        except:
            return {}
    
    def _buscar_id_espn(self, nombre):
        """Busca el ID de ESPN para un peleador por su nombre"""
        nombre_busqueda = quote(nombre.lower())
        url = f"https://www.espn.com/search/_/q/{nombre_busqueda}/type/mma"
        
        print(f"   🔎 Buscando ID para: {nombre}")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar enlaces a perfiles de peleadores
            # Patrón: /mma/fighter/_/id/[NUMERO]/[nombre]
            links = soup.find_all('a', href=re.compile(r'/mma/fighter/_/id/\d+'))
            
            for link in links:
                href = link.get('href', '')
                match = re.search(r'/id/(\d+)', href)
                if match:
                    espn_id = match.group(1)
                    # Verificar que el nombre coincida aproximadamente
                    link_text = link.text.strip().lower()
                    if nombre.lower() in link_text or link_text in nombre.lower():
                        print(f"   ✅ ID encontrado: {espn_id}")
                        return espn_id
            
            # Si no encontró en los enlaces, buscar en el texto
            page_text = soup.get_text()
            id_match = re.search(r'/mma/fighter/_/id/(\d+)/[^"]*', page_text)
            if id_match:
                espn_id = id_match.group(1)
                print(f"   ✅ ID encontrado (texto): {espn_id}")
                return espn_id
            
            print(f"   ⚠️ No se encontró ID para {nombre}")
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error buscando ID: {e}")
            return None
    
    def obtener_peleador_desde_espn(self, nombre):
        """Obtiene datos del peleador desde ESPN (busca ID dinámicamente)"""
        
        # Verificar cache primero
        nombre_lower = nombre.lower()
        if nombre_lower in self.cache_ids:
            espn_id = self.cache_ids[nombre_lower]
            print(f"   📦 Usando ID de cache: {espn_id}")
        else:
            espn_id = self._buscar_id_espn(nombre)
            if not espn_id:
                return None
            self.cache_ids[nombre_lower] = espn_id
        
        url = f"https://www.espn.com/mma/fighter/_/id/{espn_id}/{nombre.lower().replace(' ', '-')}"
        
        print(f"   🔍 Buscando en ESPN: {nombre} (ID: {espn_id})")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
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
                'url': url,
                'espn_id': espn_id
            }
            
            # Buscar record (está en el encabezado)
            record_elem = soup.find('div', class_='record')
            if record_elem:
                datos['record'] = record_elem.text.strip()
            
            # Buscar la sección de estadísticas
            page_text = soup.get_text()
            
            # Buscar altura (formato: "1.93 m")
            altura_match = re.search(r'(\d+\.?\d*)\s*m', page_text)
            if altura_match:
                altura_m = float(altura_match.group(1))
                datos['altura'] = f"{altura_m:.2f}m"
                datos['altura_cm'] = int(altura_m * 100)
            
            # Buscar peso (formato: "83 kg")
            peso_match = re.search(r'(\d+)\s*kg', page_text)
            if peso_match:
                datos['peso'] = f"{peso_match.group(1)}kg"
            
            # Buscar alcance (formato: "2.03 m")
            alcance_match = re.search(r'ALCANCE\s*(\d+\.?\d*)\s*m', page_text, re.IGNORECASE)
            if alcance_match:
                alcance_m = float(alcance_match.group(1))
                datos['alcance'] = f"{alcance_m:.2f}m"
                datos['alcance_cm'] = int(alcance_m * 100)
            
            # Calcular KO rate desde el texto
            ko_match = re.search(r'KO/TKO\s*(\d+)', page_text, re.IGNORECASE)
            if ko_match:
                ko_count = int(ko_match.group(1))
                record_parts = datos['record'].split('-')
                if len(record_parts) >= 1 and record_parts[0].isdigit():
                    wins = int(record_parts[0])
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
        if not datos:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO peleadores_ufc 
            (nombre, record, altura, peso, alcance, postura, ko_rate, ultima_actualizacion, url, espn_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['nombre'],
            datos['record'],
            datos.get('altura', 'N/A'),
            datos.get('peso', 'N/A'),
            datos.get('alcance', 'N/A'),
            datos['postura'],
            datos['ko_rate'],
            datetime.now().strftime("%Y%m%d"),
            datos.get('url', ''),
            datos.get('espn_id', '')
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
                    datos = self.obtener_peleador_desde_espn(p1)
                    if datos:
                        self.guardar_peleador(datos)
                    time.sleep(2)  # Respetar servidor
                
                if p2:
                    print(f"\n📡 Procesando: {p2}")
                    datos = self.obtener_peleador_desde_espn(p2)
                    if datos:
                        self.guardar_peleador(datos)
                    time.sleep(2)
        else:
            print("⚠️ No hay eventos UFC cargados. Ejecuta primero: python cargar_ufc_json.py")
        
        print("\n✅ Actualizacion completada")

def actualizar_ufc():
    scraper = ScraperUFCDinamico()
    scraper.actualizar_todos_peleadores()

if __name__ == "__main__":
    actualizar_ufc()
