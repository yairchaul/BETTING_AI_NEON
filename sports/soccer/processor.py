import re
from evento import Evento

class SoccerProcessor:
    def _limpiar_nombre(self, texto):
        """Limpia nombres de equipos de basura OCR"""
        if not texto:
            return ""
        # Eliminar cuotas y palabras sueltas
        texto = re.sub(r'[+-]\d+', '', texto)
        texto = re.sub(r'\b(FC|CF|CD|SD|UD|vs|VS|Empate|Draw)\b', '', texto, flags=re.IGNORECASE)
        return texto.strip()

    def process(self, raw_lines):
        """
        Procesa líneas de fútbol y devuelve lista de Eventos.
        Cada partido debe tener: Local, OddsL, Empate, OddsE, Visitante, OddsV
        """
        eventos = []
        
        # Aplanar líneas en una lista de palabras
        flat_words = []
        for line in raw_lines:
            if isinstance(line, list):
                flat_words.extend(line)
            elif isinstance(line, str):
                words = line.split()
                flat_words.extend([w.strip() for w in words if w.strip()])
        
        # Debug - mostrar palabras detectadas
        # print("Palabras detectadas:", flat_words)
        
        # Buscar patrones de partidos (buscar "Empate" como separador)
        i = 0
        while i < len(flat_words) - 5:
            # Buscar la palabra "Empate" en las siguientes posiciones
            for j in range(i, min(i+10, len(flat_words))):
                if flat_words[j] == "Empate":
                    empate_idx = j
                    
                    # Extraer datos
                    if empate_idx - 2 >= 0 and empate_idx + 3 < len(flat_words):
                        # Local (todo antes del odds local)
                        local_words = []
                        k = i
                        while k < empate_idx - 1 and not re.match(r'^[+-]', flat_words[k]):
                            local_words.append(flat_words[k])
                            k += 1
                        
                        if k < empate_idx - 1:
                            local_odd = flat_words[k]
                            
                            # Odds del empate (justo después de "Empate")
                            if empate_idx + 1 < len(flat_words):
                                empate_odd = flat_words[empate_idx + 1]
                                
                                # Visitante (después del odds de empate)
                                visitante_idx = empate_idx + 2
                                if visitante_idx < len(flat_words):
                                    visitante_words = []
                                    v = visitante_idx
                                    while v < len(flat_words) and not re.match(r'^[+-]', flat_words[v]):
                                        visitante_words.append(flat_words[v])
                                        v += 1
                                    
                                    if v < len(flat_words):
                                        visitante_odd = flat_words[v]
                                        
                                        local = self._limpiar_nombre(' '.join(local_words))
                                        visitante = self._limpiar_nombre(' '.join(visitante_words))
                                        
                                        # Solo agregar si ambos nombres son válidos
                                        if local and visitante and len(local) > 2 and len(visitante) > 2:
                                            # Crear evento
                                            evento = Evento(
                                                local=local,
                                                visitante=visitante,
                                                deporte='FUTBOL',
                                                datos_crudos={
                                                    'local_odd': local_odd,
                                                    'empate_odd': empate_odd,
                                                    'visitante_odd': visitante_odd
                                                }
                                            )
                                            evento.odds = {
                                                'local': local_odd,
                                                'draw': empate_odd,
                                                'visitante': visitante_odd
                                            }
                                            eventos.append(evento)
                                            i = v + 1
                                            break
            i += 1
        
        return eventos
