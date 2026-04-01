# -*- coding: utf-8 -*-
"""
ESPN FÚTBOL - Scraper de fútbol con +100 ligas
Obtiene partidos desde ESPN
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPN_FUTBOL:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.ligas_disponibles = self._cargar_ligas()
    
    def _cargar_ligas(self):
        """Carga todas las ligas disponibles (más de 100)"""
        return {
            # === TOP 5 EUROPEAS ===
            "Premier League": "https://www.espn.com/soccer/scoreboard/_/league/eng.1",
            "La Liga": "https://www.espn.com/soccer/scoreboard/_/league/esp.1",
            "Serie A": "https://www.espn.com/soccer/scoreboard/_/league/ita.1",
            "Bundesliga": "https://www.espn.com/soccer/scoreboard/_/league/ger.1",
            "Ligue 1": "https://www.espn.com/soccer/scoreboard/_/league/fra.1",
            
            # === SEGUNDAS DIVISIONES EUROPEAS ===
            "EFL Championship": "https://www.espn.com/soccer/scoreboard/_/league/eng.2",
            "EFL League One": "https://www.espn.com/soccer/scoreboard/_/league/eng.3",
            "EFL League Two": "https://www.espn.com/soccer/scoreboard/_/league/eng.4",
            "La Liga 2": "https://www.espn.com/soccer/scoreboard/_/league/esp.2",
            "Serie B": "https://www.espn.com/soccer/scoreboard/_/league/ita.2",
            "2. Bundesliga": "https://www.espn.com/soccer/scoreboard/_/league/ger.2",
            "Ligue 2": "https://www.espn.com/soccer/scoreboard/_/league/fra.2",
            
            # === OTRAS LIGAS EUROPEAS ===
            "Eredivisie": "https://www.espn.com/soccer/scoreboard/_/league/ned.1",
            "Primeira Liga": "https://www.espn.com/soccer/scoreboard/_/league/por.1",
            "Scottish Premiership": "https://www.espn.com/soccer/scoreboard/_/league/sco.1",
            "Russian Premier League": "https://www.espn.com/soccer/scoreboard/_/league/rus.1",
            "Turkish Super Lig": "https://www.espn.com/soccer/scoreboard/_/league/tur.1",
            "Belgian Pro League": "https://www.espn.com/soccer/scoreboard/_/league/bel.1",
            "Swiss Super League": "https://www.espn.com/soccer/scoreboard/_/league/sui.1",
            "Austrian Bundesliga": "https://www.espn.com/soccer/scoreboard/_/league/aut.1",
            "Greek Super League": "https://www.espn.com/soccer/scoreboard/_/league/gre.1",
            "Czech First League": "https://www.espn.com/soccer/scoreboard/_/league/cze.1",
            "Croatian First League": "https://www.espn.com/soccer/scoreboard/_/league/cro.1",
            "Danish Superliga": "https://www.espn.com/soccer/scoreboard/_/league/den.1",
            "Norwegian Eliteserien": "https://www.espn.com/soccer/scoreboard/_/league/nor.1",
            "Swedish Allsvenskan": "https://www.espn.com/soccer/scoreboard/_/league/swe.1",
            "Finnish Veikkausliiga": "https://www.espn.com/soccer/scoreboard/_/league/fin.1",
            "Icelandic Úrvalsdeild": "https://www.espn.com/soccer/scoreboard/_/league/isl.1",
            "Irish Premier Division": "https://www.espn.com/soccer/scoreboard/_/league/irl.1",
            "Polish Ekstraklasa": "https://www.espn.com/soccer/scoreboard/_/league/pol.1",
            "Hungarian NB I": "https://www.espn.com/soccer/scoreboard/_/league/hun.1",
            "Slovak Super Liga": "https://www.espn.com/soccer/scoreboard/_/league/svk.1",
            "Romanian Liga I": "https://www.espn.com/soccer/scoreboard/_/league/rou.1",
            "Bulgarian First League": "https://www.espn.com/soccer/scoreboard/_/league/bul.1",
            "Serbian SuperLiga": "https://www.espn.com/soccer/scoreboard/_/league/srb.1",
            "Cypriot First Division": "https://www.espn.com/soccer/scoreboard/_/league/cyp.1",
            "Israeli Premier League": "https://www.espn.com/soccer/scoreboard/_/league/isr.1",
            
            # === LIGAS AMERICANAS ===
            "Liga MX": "https://www.espn.com/soccer/scoreboard/_/league/mex.1",
            "MLS": "https://www.espn.com/soccer/scoreboard/_/league/usa.1",
            "Argentine Primera División": "https://www.espn.com/soccer/scoreboard/_/league/arg.1",
            "Brazilian Série A": "https://www.espn.com/soccer/scoreboard/_/league/bra.1",
            "Chilean Primera División": "https://www.espn.com/soccer/scoreboard/_/league/chi.1",
            "Colombian Primera A": "https://www.espn.com/soccer/scoreboard/_/league/col.1",
            "Uruguayan Primera División": "https://www.espn.com/soccer/scoreboard/_/league/uru.1",
            "Paraguayan Primera División": "https://www.espn.com/soccer/scoreboard/_/league/par.1",
            "Peruvian Primera División": "https://www.espn.com/soccer/scoreboard/_/league/per.1",
            "Ecuadorian Serie A": "https://www.espn.com/soccer/scoreboard/_/league/ecu.1",
            "Venezuelan Primera División": "https://www.espn.com/soccer/scoreboard/_/league/ven.1",
            "Bolivian Primera División": "https://www.espn.com/soccer/scoreboard/_/league/bol.1",
            "USL Championship": "https://www.espn.com/soccer/scoreboard/_/league/usa.2",
            "Canadian Premier League": "https://www.espn.com/soccer/scoreboard/_/league/can.1",
            
            # === LIGAS ASIÁTICAS ===
            "J1 League": "https://www.espn.com/soccer/scoreboard/_/league/jpn.1",
            "J2 League": "https://www.espn.com/soccer/scoreboard/_/league/jpn.2",
            "K League 1": "https://www.espn.com/soccer/scoreboard/_/league/kor.1",
            "K League 2": "https://www.espn.com/soccer/scoreboard/_/league/kor.2",
            "Chinese Super League": "https://www.espn.com/soccer/scoreboard/_/league/chn.1",
            "Saudi Pro League": "https://www.espn.com/soccer/scoreboard/_/league/sau.1",
            "Qatar Stars League": "https://www.espn.com/soccer/scoreboard/_/league/qat.1",
            "UAE Pro League": "https://www.espn.com/soccer/scoreboard/_/league/uae.1",
            "A-League": "https://www.espn.com/soccer/scoreboard/_/league/aus.1",
            "Indian Super League": "https://www.espn.com/soccer/scoreboard/_/league/ind.1",
            
            # === LIGAS AFRICANAS ===
            "Egyptian Premier League": "https://www.espn.com/soccer/scoreboard/_/league/egy.1",
            "South African Premier Division": "https://www.espn.com/soccer/scoreboard/_/league/rsa.1",
            "Moroccan Botola Pro": "https://www.espn.com/soccer/scoreboard/_/league/mar.1",
            "Tunisian Ligue 1": "https://www.espn.com/soccer/scoreboard/_/league/tun.1",
            "Algerian Ligue 1": "https://www.espn.com/soccer/scoreboard/_/league/alg.1",
            
            # === COMPETICIONES INTERNACIONALES ===
            "UEFA Champions League": "https://www.espn.com/soccer/scoreboard/_/league/uefa.champions",
            "UEFA Europa League": "https://www.espn.com/soccer/scoreboard/_/league/uefa.europa",
            "UEFA Conference League": "https://www.espn.com/soccer/scoreboard/_/league/uefa.euroconf",
            "Copa Libertadores": "https://www.espn.com/soccer/scoreboard/_/league/conmebol.libertadores",
            "Copa Sudamericana": "https://www.espn.com/soccer/scoreboard/_/league/conmebol.sudamericana",
            "CONCACAF Champions League": "https://www.espn.com/soccer/scoreboard/_/league/concacaf.champions",
            "AFC Champions League": "https://www.espn.com/soccer/scoreboard/_/league/afc.champions",
            "CAF Champions League": "https://www.espn.com/soccer/scoreboard/_/league/caf.champions",
            
            # === LIGAS FEMENINAS ===
            "Liga MX Femenil": "https://www.espn.com/soccer/scoreboard/_/league/mex.10",
            "NWSL": "https://www.espn.com/soccer/scoreboard/_/league/usa.9",
            "Women's Super League": "https://www.espn.com/soccer/scoreboard/_/league/eng.9",
            "Primera División Femenina": "https://www.espn.com/soccer/scoreboard/_/league/esp.10",
            "Serie A Femminile": "https://www.espn.com/soccer/scoreboard/_/league/ita.9",
            "Frauen-Bundesliga": "https://www.espn.com/soccer/scoreboard/_/league/ger.9",
            "Division 1 Féminine": "https://www.espn.com/soccer/scoreboard/_/league/fra.9",
            
            # === MÁS LIGAS EUROPEAS ===
            "Scottish Championship": "https://www.espn.com/soccer/scoreboard/_/league/sco.2",
            "Belgian Challenger Pro League": "https://www.espn.com/soccer/scoreboard/_/league/bel.2",
            "Dutch Eerste Divisie": "https://www.espn.com/soccer/scoreboard/_/league/ned.2",
            "Portuguese Segunda Liga": "https://www.espn.com/soccer/scoreboard/_/league/por.2",
            "Greek Super League 2": "https://www.espn.com/soccer/scoreboard/_/league/gre.2",
            "Ukrainian Premier League": "https://www.espn.com/soccer/scoreboard/_/league/ukr.1",
            "Belarusian Premier League": "https://www.espn.com/soccer/scoreboard/_/league/blr.1",
            "Kazakhstan Premier League": "https://www.espn.com/soccer/scoreboard/_/league/kaz.1",
            "Azerbaijan Premier League": "https://www.espn.com/soccer/scoreboard/_/league/aze.1",
            "Georgian Erovnuli Liga": "https://www.espn.com/soccer/scoreboard/_/league/geo.1",
            "Moldovan Super Liga": "https://www.espn.com/soccer/scoreboard/_/league/mda.1",
            "Latvian Higher League": "https://www.espn.com/soccer/scoreboard/_/league/lva.1",
            "Lithuanian A Lyga": "https://www.espn.com/soccer/scoreboard/_/league/ltu.1",
            "Estonian Meistriliiga": "https://www.espn.com/soccer/scoreboard/_/league/est.1",
            "Faroese Premier League": "https://www.espn.com/soccer/scoreboard/_/league/fro.1",
            "Maltese Premier League": "https://www.espn.com/soccer/scoreboard/_/league/mlt.1",
            "Luxembourg National Division": "https://www.espn.com/soccer/scoreboard/_/league/lux.1",
            
            # === LIGAS NÓRDICAS ===
            "Icelandic Úrvalsdeild": "https://www.espn.com/soccer/scoreboard/_/league/isl.1",
            "Finnish Veikkausliiga": "https://www.espn.com/soccer/scoreboard/_/league/fin.1",
            "Swedish Allsvenskan": "https://www.espn.com/soccer/scoreboard/_/league/swe.1",
            "Norwegian Eliteserien": "https://www.espn.com/soccer/scoreboard/_/league/nor.1",
            "Danish Superliga": "https://www.espn.com/soccer/scoreboard/_/league/den.1",
            
            # === LIGAS DEL ESTE DE EUROPA ===
            "Polish Ekstraklasa": "https://www.espn.com/soccer/scoreboard/_/league/pol.1",
            "Czech First League": "https://www.espn.com/soccer/scoreboard/_/league/cze.1",
            "Slovak Super Liga": "https://www.espn.com/soccer/scoreboard/_/league/svk.1",
            "Hungarian NB I": "https://www.espn.com/soccer/scoreboard/_/league/hun.1",
            "Slovenian PrvaLiga": "https://www.espn.com/soccer/scoreboard/_/league/svn.1",
            "Croatian First League": "https://www.espn.com/soccer/scoreboard/_/league/cro.1",
            "Bosnian Premier League": "https://www.espn.com/soccer/scoreboard/_/league/bih.1",
            "Montenegrin First League": "https://www.espn.com/soccer/scoreboard/_/league/mne.1",
            "Macedonian First League": "https://www.espn.com/soccer/scoreboard/_/league/mkd.1",
            "Albanian Superliga": "https://www.espn.com/soccer/scoreboard/_/league/alb.1",
            "Kosovo Superleague": "https://www.espn.com/soccer/scoreboard/_/league/kos.1",
            
            # === LIGAS DE LAS AMÉRICAS ===
            "Liga de Ascenso MX": "https://www.espn.com/soccer/scoreboard/_/league/mex.2",
            "Brazilian Série B": "https://www.espn.com/soccer/scoreboard/_/league/bra.2",
            "Argentine Primera Nacional": "https://www.espn.com/soccer/scoreboard/_/league/arg.2",
            "Chilean Primera B": "https://www.espn.com/soccer/scoreboard/_/league/chi.2",
            "Colombian Primera B": "https://www.espn.com/soccer/scoreboard/_/league/col.2",
        }
    
    def get_available_leagues(self):
        """Retorna lista de todas las ligas disponibles"""
        return list(self.ligas_disponibles.keys())
    
    def get_games(self, liga_nombre):
        """Obtiene los partidos de una liga específica"""
        if liga_nombre not in self.ligas_disponibles:
            logger.warning(f"Liga no encontrada: {liga_nombre}")
            return []
        
        url = self.ligas_disponibles[liga_nombre]
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            partidos = []
            
            # Buscar partidos en ESPN
            eventos = soup.select('.scoreboard, .event-container, .schedule')
            
            for evento in eventos:
                try:
                    # Buscar equipos
                    equipos = evento.select('.team-name, .name')
                    if len(equipos) >= 2:
                        local = equipos[0].get_text(strip=True)
                        visitante = equipos[1].get_text(strip=True)
                    else:
                        continue
                    
                    # Buscar marcador si existe
                    marcador = evento.select('.score, .total-score')
                    if len(marcador) >= 2:
                        goles_local = marcador[0].get_text(strip=True)
                        goles_visitante = marcador[1].get_text(strip=True)
                    else:
                        goles_local = None
                        goles_visitante = None
                    
                    partidos.append({
                        'home': local,
                        'away': visitante,
                        'home_score': goles_local,
                        'away_score': goles_visitante,
                        'liga': liga_nombre,
                        'status': 'programado' if not goles_local else 'finalizado'
                    })
                    
                except Exception as e:
                    logger.debug(f"Error parseando partido: {e}")
                    continue
            
            logger.info(f"✅ {len(partidos)} partidos obtenidos para {liga_nombre}")
            return partidos
            
        except Exception as e:
            logger.error(f"Error obteniendo {liga_nombre}: {e}")
            return []
    
    def get_all_games(self):
        """Obtiene partidos de todas las ligas"""
        todos_partidos = {}
        for liga in self.ligas_disponibles:
            partidos = self.get_games(liga)
            if partidos:
                todos_partidos[liga] = partidos
        return todos_partidos


# Para pruebas
if __name__ == "__main__":
    scraper = ESPN_FUTBOL()
    ligas = scraper.get_available_leagues()
    print(f"✅ {len(ligas)} ligas disponibles")
    
    # Probar con algunas ligas
    for liga in list(ligas.keys())[:5]:
        partidos = scraper.get_games(liga)
        print(f"\n{liga}: {len(partidos)} partidos")
