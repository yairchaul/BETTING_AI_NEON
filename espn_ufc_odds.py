"""
ESPN UFC ODDS - Scraper para odds de UFC (estilo Caliente.mx)
Extrae moneyline y método de victoria aproximado
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class UFCOddsScraper:
    def __init__(self):
        self._setup_driver()
    
    def _setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def obtener_odds(self, event_id=None):
        """
        Obtiene odds de combates UFC desde ESPN Fightcenter
        """
        url = f"https://www.espn.com.mx/mma/fightcenter/_/id/{event_id or '600057366'}/league/ufc"
        print(f"📡 Extrayendo odds UFC desde: {url}")
        
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "FightCard")))
            time.sleep(3)
            
            combates = []
            
            # Buscar tarjetas de combates
            fight_cards = self.driver.find_elements(By.CLASS_NAME, "FightCard")
            
            for card in fight_cards:
                try:
                    # Nombres de peleadores
                    fighters = card.find_elements(By.CSS_SELECTOR, ".fighter-name")
                    if len(fighters) >= 2:
                        peleador1 = fighters[0].text.strip()
                        peleador2 = fighters[1].text.strip()
                    else:
                        continue
                    
                    # Odds (si están disponibles)
                    odds_elements = card.find_elements(By.CSS_SELECTOR, ".odds")
                    odds1 = "-150"
                    odds2 = "+130"
                    
                    if len(odds_elements) >= 2:
                        odds1 = odds_elements[0].text.strip() or "-150"
                        odds2 = odds_elements[1].text.strip() or "+130"
                    
                    # Categoría de peso
                    peso = ""
                    try:
                        peso_elem = card.find_element(By.CSS_SELECTOR, ".weight-class")
                        peso = peso_elem.text.strip()
                    except:
                        peso = "Peso Pactado"
                    
                    combates.append({
                        'peleador1': peleador1,
                        'peleador2': peleador2,
                        'categoria': peso,
                        'odds': {
                            'moneyline_local': odds1,
                            'moneyline_visitante': odds2,
                            'metodo': 'KO/Sub/Decisión'
                        }
                    })
                    
                except Exception as e:
                    print(f"   ⚠️ Error en combate: {e}")
                    continue
            
            return combates
            
        except Exception as e:
            print(f"❌ Error extrayendo odds UFC: {e}")
            return []
    
    def cerrar(self):
        if self.driver:
            self.driver.quit()

def obtener_odds_ufc_evento(event_id=None):
    scraper = UFCOddsScraper()
    try:
        odds = scraper.obtener_odds(event_id)
        return odds
    finally:
        scraper.cerrar()

if __name__ == "__main__":
    odds = obtener_odds_ufc_evento()
    for o in odds:
        print(f"{o['peleador1']} vs {o['peleador2']} | {o['odds']['moneyline_local']} / {o['odds']['moneyline_visitante']}")
