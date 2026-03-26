"""
ANALIZADOR UFC GEMINI - Análisis contextual de peleas
"""
class AnalizadorUFCGemini:
    def __init__(self, api_key):
        self.api_key = api_key
        self.gemini = None
        try:
            from cerebro_gemini_pro import CerebroGemini
            self.gemini = CerebroGemini(api_key)
        except:
            pass
    
    def analizar(self, p1_data, p2_data, resumen):
        """Analiza pelea UFC con Gemini"""
        p1_nombre = p1_data.get('nombre', 'Peleador 1')
        p2_nombre = p2_data.get('nombre', 'Peleador 2')
        
        if self.gemini:
            try:
                datos = f"Resumen: {resumen}"
                return self.gemini.analizar_ufc(p1_nombre, p2_nombre, datos)
            except:
                return "Análisis Gemini no disponible"
        return "Gemini no disponible"
