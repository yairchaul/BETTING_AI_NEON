# -*- coding: utf-8 -*-
"""
SCRAPER ODDS UFC - Desde Action Network
Extrae odds en formato americano (+240, -142, etc.)
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import sqlite3

class ScraperOddsActionNetwork:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def _obtener_peleadores_desde_bd(self):
        """Obtiene la lista de peleadores desde la BD (último evento)"""
        try:
            conn = sqlite3.connect("data/betting_stats.db")
            cursor = conn.cursor()
            cursor.execute("SELECT cartelera FROM eventos_ufc ORDER BY fecha DESC LIMIT 1")
            evento = cursor.fetchone()
            conn.close()
            
            peleadores = []
            if evento and evento[0]:
                cartelera = json.loads(evento[0])
                for pelea in cartelera:
                    p1 = pelea.get('peleador1', '')
                    p2 = pelea.get('peleador2', '')
                    if p1:
                        peleadores.append(p1)
                    if p2:
                        peleadores.append(p2)
            return peleadores
        except Exception as e:
            print(f"Error leyendo BD: {e}")
            return []
    
    def obtener_odds(self):
        """Obtiene odds de UFC desde Action Network"""
        url = "https://www.actionnetwork.com/ufc/odds"
        
        print(f"📡 Extrayendo odds desde Action Network...")
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            odds = {}
            
            # Método 1: Buscar en la estructura de la página
            # Los odds están en elementos con clase que contiene "odds"
            odds_elements = soup.find_all('span', class_=re.compile(r'odds|price|value'))
            
            # También buscar nombres de peleadores
            nombres_elements = soup.find_all('span', class_=re.compile(r'name|fighter|participant'))
            
            # Buscar pares nombre-odd cercanos
            for i, nombre_elem in enumerate(nombres_elements):
                nombre = nombre_elem.text.strip()
                if len(nombre) > 3 and not any(c.isdigit() for c in nombre):
                    # Buscar el odd más cercano
                    for j in range(max(0, i-2), min(len(odds_elements), i+3)):
                        odd_text = odds_elements[j].text.strip()
                        if odd_text.startswith('+') or odd_text.startswith('-'):
                            odds[nombre.lower()] = odd_text
                            break
            
            # Método 2: Buscar por regex en el texto completo
            page_text = soup.get_text()
            
            # Patrón: "Nombre + odd" (ej: "Terrace Mckinney -142")
            patron_nombre_odd = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([+-]\d{3,4})'
            matches = re.findall(patron_nombre_odd, page_text)
            for nombre, odd in matches:
                odds[nombre.lower()] = odd
            
            # Patrón: "Nombre US: -142" (como en la imagen)
            patron_us = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+US:\s+([+-]\d+)'
            matches_us = re.findall(patron_us, page_text, re.IGNORECASE)
            for nombre, odd in matches_us:
                odds[nombre.lower()] = odd
            
            print(f"✅ Encontrados {len(odds)} odds totales")
            return odds
            
        except Exception as e:
            print(f"❌ Error extrayendo odds: {e}")
            return {}
    
    def obtener_odds_para_cartelera(self):
        """Obtiene odds específicas para los peleadores de la cartelera actual"""
        peleadores = self._obtener_peleadores_desde_bd()
        
        if not peleadores:
            print("⚠️ No hay peleadores en la BD. Ejecuta primero: python cargar_ufc_json.py")
            return {}
        
        print(f"📡 Buscando odds para {len(peleadores)} peleadores...")
        
        odds_totales = self.obtener_odds()
        
        resultados = {}
        for peleador in peleadores:
            nombre_lower = peleador.lower()
            encontrado = False
            
            # Buscar coincidencia exacta o parcial
            for key, odd in odds_totales.items():
                if nombre_lower in key or key in nombre_lower:
                    resultados[peleador] = odd
                    encontrado = True
                    break
            
            if not encontrado:
                # Buscar por apellido
                partes = peleador.split()
                if len(partes) > 1:
                    apellido = partes[-1].lower()
                    for key, odd in odds_totales.items():
                        if apellido in key:
                            resultados[peleador] = odd
                            encontrado = True
                            break
            
            if not encontrado:
                resultados[peleador] = "N/A"
        
        # Mostrar resultados
        encontrados = sum(1 for v in resultados.values() if v != "N/A")
        print(f"✅ Encontrados {encontrados}/{len(peleadores)} odds")
        
        for nombre, odd in resultados.items():
            print(f"   {nombre}: {odd}")
        
        return resultados
    
    def guardar_odds_en_bd(self, odds):
        """Guarda los odds en la BD"""
        conn = sqlite3.connect("data/betting_stats.db")
        cursor = conn.cursor()
        
        # Agregar columna odds si no existe
        try:
            cursor.execute("ALTER TABLE peleadores_ufc ADD COLUMN odds TEXT")
        except:
            pass
        
        for nombre, odd in odds.items():
            if odd != "N/A":
                cursor.execute('''
                    UPDATE peleadores_ufc SET odds = ? WHERE nombre = ?
                ''', (odd, nombre))
        
        conn.commit()
        conn.close()
        print(f"✅ {len([v for v in odds.values() if v != 'N/A'])} odds guardados en BD")

def actualizar_odds_ufc():
    scraper = ScraperOddsActionNetwork()
    odds = scraper.obtener_odds_para_cartelera()
    
    if odds:
        scraper.guardar_odds_en_bd(odds)
    
    return odds

if __name__ == "__main__":
    odds = actualizar_odds_ufc()
    
    print("\n📊 RESULTADO FINAL:")
    for nombre, odd in odds.items():
        print(f"   {nombre}: {odd}")
