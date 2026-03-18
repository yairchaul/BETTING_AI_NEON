"""
UFC.COM SCRAPER - Extrae datos de peleadores de UFC.com
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import streamlit as st

class UFCComScraper:
    """
    Scraper para obtener datos de peleadores de UFC.com
    """
    
    def __init__(self):
        self.base_url = "https://www.ufc.com"
        self.cache = {}
        print("✅ UFC.com Scraper inicializado")
    
    def _normalize_name(self, name):
        """Normaliza nombre para URL de UFC.com"""
        # Convertir a minúsculas y reemplazar espacios con guiones
        name = name.lower().strip()
        # Eliminar caracteres especiales
        name = re.sub(r'[^\w\s-]', '', name)
        # Reemplazar espacios con guiones
        name = re.sub(r'[-\s]+', '-', name)
        return name
    
    def get_fighter_data(self, fighter_name):
        """
        Obtiene datos de un peleador desde UFC.com
        """
        if fighter_name in self.cache:
            return self.cache[fighter_name]
        
        # Esperar un poco para no saturar el servidor
        time.sleep(1)
        
        normalized = self._normalize_name(fighter_name)
        url = f"{self.base_url}/athlete/{normalized}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraer datos básicos
                data = {
                    'nombre': fighter_name,
                    'altura': self._extract_height(soup),
                    'peso': self._extract_weight(soup),
                    'alcance': self._extract_reach(soup),
                    'postura': self._extract_stance(soup),
                    'fuente': 'UFC.com'
                }
                
                self.cache[fighter_name] = data
                return data
            else:
                return None
        except Exception as e:
            print(f"Error scraping UFC.com para {fighter_name}: {e}")
            return None
    
    def _extract_height(self, soup):
        """Extrae altura"""
        try:
            # Buscar en la tabla de stats
            stats = soup.find_all('div', class_='c-stat-compare__number')
            if stats and len(stats) > 0:
                # La altura suele ser el primer stat
                return stats[0].text.strip()
        except:
            pass
        return 'N/A'
    
    def _extract_weight(self, soup):
        """Extrae peso"""
        try:
            stats = soup.find_all('div', class_='c-stat-compare__number')
            if stats and len(stats) > 1:
                # El peso suele ser el segundo stat
                return stats[1].text.strip()
        except:
            pass
        return 'N/A'
    
    def _extract_reach(self, soup):
        """Extrae alcance"""
        try:
            # Buscar en la sección de info
            info_items = soup.find_all('div', class_='c-bio__info')
            for item in info_items:
                label = item.find('div', class_='c-bio__label')
                if label and 'Reach' in label.text:
                    value = item.find('div', class_='c-bio__text')
                    if value:
                        return value.text.strip()
        except:
            pass
        return 'N/A'
    
    def _extract_stance(self, soup):
        """Extrae postura"""
        try:
            info_items = soup.find_all('div', class_='c-bio__info')
            for item in info_items:
                label = item.find('div', class_='c-bio__label')
                if label and 'Stance' in label.text:
                    value = item.find('div', class_='c-bio__text')
                    if value:
                        return value.text.strip()
        except:
            pass
        return 'Desconocida'
