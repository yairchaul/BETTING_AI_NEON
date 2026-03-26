import logging

logger = logging.getLogger(__name__)

class AnalizadorGeminiNBA:
    def __init__(self, api_key):
        self.api_key = api_key
        self.gemini = None
        try:
            from cerebro_gemini_pro import CerebroGemini
            self.gemini = CerebroGemini(api_key)
            logger.info("✅ CerebroGemini cargado correctamente")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar Gemini: {e}")
            self.gemini = None

    def analizar(self, partido):
        """Versión antigua para compatibilidad"""
        return self.analizar_con_decision(partido, None)

    def analizar_con_decision(self, partido, analisis_heuristico):
        """
        Gemini como DECISOR FINAL usando el orquestrador
        """
        if not self.gemini:
            return "❌ Gemini no disponible - usa el pick matemático"
        
        if not analisis_heuristico:
            return "❌ No hay análisis matemático disponible"
        
        return self.gemini.orquestrar_decision_final(
            deporte="NBA",
            partido=partido,
            analisis_heuristico=analisis_heuristico
        )
