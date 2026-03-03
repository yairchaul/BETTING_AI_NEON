def _parse_simple_pattern(self, lines):
    """
    Parser específico para el formato que detectaste:
    +90
    Melbourne City
    Buriram United
    03 Mar 01:45
    1
    X
    2
    +125
    +220
    +200
    """
    matches = []
    i = 0
    
    while i < len(lines):
        # Buscar patrón: número con signo + 3 líneas + 3 cuotas
        if i + 8 < len(lines):
            # Verificar si la línea actual es un número con signo
            if re.match(r'^[+-]\d+$', lines[i]):
                potencial_local = lines[i+1]
                potencial_visitante = lines[i+2]
                potencial_fecha = lines[i+3]
                
                # Verificar las siguientes 3 líneas (1, X, 2)
                if (lines[i+4] == '1' and 
                    lines[i+5] == 'X' and 
                    lines[i+6] == '2'):
                    
                    # Las siguientes 3 líneas deberían ser las cuotas
                    cuota_local = lines[i+7] if i+7 < len(lines) else 'N/A'
                    cuota_empate = lines[i+8] if i+8 < len(lines) else 'N/A'
                    cuota_visitante = lines[i+9] if i+9 < len(lines) else 'N/A'
                    
                    # Validar que las cuotas tengan formato correcto
                    if (re.match(r'^[+-]\d+$', cuota_local) and
                        re.match(r'^[+-]\d+$', cuota_empate) and
                        re.match(r'^[+-]\d+$', cuota_visitante)):
                        
                        matches.append({
                            'home': potencial_local,
                            'away': potencial_visitante,
                            'all_odds': [cuota_local, cuota_empate, cuota_visitante],
                            'fecha': potencial_fecha
                        })
                        
                        # Saltamos todo el bloque (10 líneas)
                        i += 10
                        continue
        
        i += 1
    
    return matches