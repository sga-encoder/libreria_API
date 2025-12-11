def estanteria_optima(libros, capacidad_max):
    """
    libros: lista de diccionarios con {"peso": float, "valor": int}
    capacidad_max: capacidad máxima en kg
    """

    opciones = [0, 1]           # 0 = NO incluir, 1 = INCLUIR
    profundidad = len(libros)   # una decisión por libro

    mejor_valor = 0
    mejor_solucion = []

    def backtrack(solucion, peso_actual, valor_actual, index):
        nonlocal mejor_valor, mejor_solucion

        # 1. Condición de parada: tomamos decisión para todos los libros
        if index == profundidad:
            if valor_actual > mejor_valor:
                mejor_valor = valor_actual
                mejor_solucion.append(solucion[:])
            return

        # 2. Recorrer opciones: incluir o no incluir libro
        for opcion in opciones:
            libro = libros[index]

            if opcion == 1:
                # Intentar incluir el libro
                nuevo_peso = peso_actual + libro.get_weight()

                # Poda por capacidad
                if nuevo_peso > capacidad_max:
                    continue

                solucion.append(1)
                backtrack(solucion, nuevo_peso, valor_actual + libro.get_price(), index + 1)
                solucion.pop()

            else:
                # Opción 0: no incluir
                solucion.append(0)
                backtrack(solucion, peso_actual, valor_actual, index + 1)
                solucion.pop()

    # Llamada inicial
    backtrack([], 0.0, 0, 0)

    return mejor_solucion
