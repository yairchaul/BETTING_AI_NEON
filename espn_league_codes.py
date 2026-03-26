"""
ESPN LEAGUE CODES - Lista completa de códigos de ligas de fútbol
"""
class ESPNLeagueCodes:
    # Códigos correctos de ESPN para diferentes ligas
    LIGAS = {
        # Europa
        "Premier League": "eng.1",
        "LaLiga": "esp.1",
        "Bundesliga": "ger.1",
        "Serie A": "ita.1",
        "Ligue 1": "fra.1",
        "Eredivisie": "ned.1",
        "Primeira Liga": "por.1",
        "Belgian Pro League": "bel.1",
        "Scottish Premiership": "sco.1",
        "Russian Premier League": "rus.1",
        "Turkish Super Lig": "tur.1",
        "Greek Super League": "gre.1",
        "Ukrainian Premier League": "ukr.1",
        "Swiss Super League": "sui.1",
        "Austrian Bundesliga": "aut.1",
        "Czech First League": "cze.1",
        "Croatian League": "cro.1",
        "Danish Superliga": "den.1",
        "Swedish Allsvenskan": "swe.1",
        "Norwegian Eliteserien": "nor.1",
        "Finnish Veikkausliiga": "fin.1",
        
        # América
        "Liga MX": "mex.1",
        "MLS": "usa.1",
        "Argentine Liga Profesional": "arg.1",
        "Brazilian Serie A": "bra.1",
        "Chilean Primera Division": "chi.1",
        "Colombian Primera A": "col.1",
        "Uruguayan Primera Division": "uru.1",
        "Paraguayan Primera Division": "par.1",
        "Peruvian Liga 1": "per.1",
        "Ecuadorian Serie A": "ecu.1",
        "Venezuelan Primera Division": "ven.1",
        "Bolivian Primera Division": "bol.1",
        
        # Asia
        "J1 League": "jpn.1",
        "K League 1": "kor.1",
        "Saudi Pro League": "ksa.1",
        "UAE Pro League": "uae.1",
        "Qatar Stars League": "qat.1",
        "Chinese Super League": "chn.1",
        "A-League": "aus.1",
        
        # Torneos
        "UEFA Champions League": "uefa.champions",
        "UEFA Europa League": "uefa.europa",
        "Copa Libertadores": "conmebol.libertadores",
        "Copa Sudamericana": "conmebol.sudamericana",
        "CONCACAF Champions League": "concacaf.champions",
        "FA Cup": "eng.fa",
        "Copa del Rey": "esp.copa",
        "Coppa Italia": "ita.copa",
        "DFB Pokal": "ger.copa",
        "Copa Argentina": "arg.copa",
    }
    
    @classmethod
    def obtener_todas(cls):
        """Retorna todas las ligas disponibles"""
        return list(cls.LIGAS.keys())
    
    @classmethod
    def obtener_codigo(cls, nombre_liga):
        """Obtiene el código ESPN para una liga"""
        return cls.LIGAS.get(nombre_liga, None)
