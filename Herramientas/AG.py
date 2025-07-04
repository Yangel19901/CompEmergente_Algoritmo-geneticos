import numpy as np


def ejecutar_algoritmo_genetico(funcion_objetivo_info, tamano_poblacion=10, umbral_diferencia=0.05, max_iteraciones=500, variabilidad_mutacion=1.0):
    
    funcion_callable = funcion_objetivo_info['funcion_callable']
    intervalo = funcion_objetivo_info['intervalo'] 
    num_variables = len(intervalo)
    objetivo = funcion_objetivo_info['objetivo'] 

    # 1. Inicialización de la población
    poblacion = []
    for _ in range(tamano_poblacion):
        individuo = [np.random.uniform(intervalo[i][0], intervalo[i][1]) for i in range(num_variables)]
        poblacion.append(individuo)

    mejor_individuo_global = None
    mejor_aptitud_global = -np.inf if objetivo == 'maximizar' else np.inf

    print(f"\n--- Ejecutando Algoritmo Genético para '{funcion_objetivo_info['nombre']}' ---")
    print(f"Tamaño de población: {tamano_poblacion}, Max. Iteraciones: {max_iteraciones}, Objetivo: {objetivo}")

    # Definir la función de mutación aquí, FUERA DEL BUCLE de generación y los condicionales
    def mutar_individuo(individuo, intervalo, variabilidad):
        individuo_mutado = list(individuo)
        for j in range(len(individuo)): # Usar len(individuo) en caso de que num_variables sea 0 o 1
            if np.random.rand() < 0.1: 
                mutacion = np.random.normal(0, variabilidad)
                individuo_mutado[j] = individuo_mutado[j] + mutacion
                # Asegurarse de que el gen mutado esté dentro de su intervalo
                individuo_mutado[j] = max(intervalo[j][0], min(individuo_mutado[j], intervalo[j][1]))
        return individuo_mutado

    for generacion in range(max_iteraciones):
        # 2. Evaluación de Aptitud
        aptitudes = []
        for individuo in poblacion:
            try:
                aptitud = funcion_callable(*individuo)
                # Convertir a float si el resultado es un array de numpy con un solo elemento
                if isinstance(aptitud, np.ndarray) and aptitud.size == 1:
                    aptitud = float(aptitud)
                aptitudes.append(aptitud)
            except Exception as e:
                # Asignar una aptitud muy baja/alta para penalizar estos individuos
                aptitudes.append(-np.inf if objetivo == 'maximizar' else np.inf)

        # Ajustar aptitudes para selección (Ruleta de la Fortuna requiere valores positivos, mayores = mejor)
        aptitudes_para_seleccion = np.array(aptitudes)
        
        if objetivo == 'minimizar':
            finite_aptitudes = aptitudes_para_seleccion[np.isfinite(aptitudes_para_seleccion)]
            if len(finite_aptitudes) > 0:
                max_finite_aptitud = np.max(finite_aptitudes)
                aptitudes_para_seleccion = max_finite_aptitud - aptitudes_para_seleccion 
            else:
                aptitudes_para_seleccion = np.ones_like(aptitudes_para_seleccion) * 1.0

            min_val_for_selection = np.min(aptitudes_para_seleccion)
            if min_val_for_selection < 0:
                aptitudes_para_seleccion = aptitudes_para_seleccion - min_val_for_selection + 1e-6
            elif np.sum(aptitudes_para_seleccion) == 0:
                aptitudes_para_seleccion = np.ones_like(aptitudes_para_seleccion) * 1.0
        else: # Maximizar
            min_val_for_selection = np.min(aptitudes_para_seleccion)
            if min_val_for_selection < 0:
                aptitudes_para_seleccion = aptitudes_para_seleccion - min_val_for_selection + 1e-6
            elif np.sum(aptitudes_para_seleccion) == 0:
                 aptitudes_para_seleccion = np.ones_like(aptitudes_para_seleccion) * 1.0


        # Obtener estadísticas de aptitud para mostrar (usando las aptitudes reales)
        aptitudes_reales = np.array(aptitudes)
        finite_aptitudes_reales = aptitudes_reales[np.isfinite(aptitudes_reales)]
        
        max_aptitud = np.max(finite_aptitudes_reales) if len(finite_aptitudes_reales) > 0 else float('nan')
        min_aptitud = np.min(finite_aptitudes_reales) if len(finite_aptitudes_reales) > 0 else float('nan')
        mediana_aptitud = np.median(finite_aptitudes_reales) if len(finite_aptitudes_reales) > 0 else float('nan')


        # 3. Actualizar el mejor individuo global
        valid_indices = np.where(np.isfinite(aptitudes_reales))[0]
        if len(valid_indices) > 0:
            if objetivo == 'maximizar':
                current_best_idx_global = valid_indices[np.argmax(aptitudes_reales[valid_indices])]
                if aptitudes_reales[current_best_idx_global] > mejor_aptitud_global:
                    mejor_aptitud_global = aptitudes_reales[current_best_idx_global]
                    mejor_individuo_global = poblacion[current_best_idx_global]
            else: # Minimizar
                current_best_idx_global = valid_indices[np.argmin(aptitudes_reales[valid_indices])]
                if aptitudes_reales[current_best_idx_global] < mejor_aptitud_global:
                    mejor_aptitud_global = aptitudes_reales[current_best_idx_global]
                    mejor_individuo_global = poblacion[current_best_idx_global]
        
        # Imprimir estadísticas de la iteración
        print(f"Generación {generacion + 1}: Max Aptitud={max_aptitud:.4f}, Mediana Aptitud={mediana_aptitud:.4f}, Min Aptitud={min_aptitud:.4f}")

        # 4. Condición de Terminación (basada en aptitudes finitas)
        if len(finite_aptitudes_reales) > 0:
            if (max_aptitud - min_aptitud < umbral_diferencia) and generacion > 0:
                print(f"Convergencia alcanzada. Diferencia entre Max y Min Aptitud ({max_aptitud-min_aptitud:.4f}) menor que el umbral ({umbral_diferencia}).")
                break
        
        if generacion == max_iteraciones - 1:
            print("Número máximo de iteraciones alcanzado.")
            break

        # 5. Selección (Ruleta de la Fortuna)
        if np.sum(aptitudes_para_seleccion) == 0: 
            probabilidades = np.ones(tamano_poblacion) / tamano_poblacion
        else:
            probabilidades = aptitudes_para_seleccion / np.sum(aptitudes_para_seleccion)
        
        probabilidades = np.nan_to_num(probabilidades, nan=1.0/tamano_poblacion, posinf=1.0/tamano_poblacion, neginf=1.0/tamano_poblacion)
        probabilidades = probabilidades / np.sum(probabilidades)

        indices_padres = np.random.choice(range(tamano_poblacion), size=tamano_poblacion, p=probabilidades)
        padres = [poblacion[i] for i in indices_padres]

        nueva_poblacion = []
        
        # Si solo hay una variable, no hay cruce, solo mutación
        if num_variables <= 1: # Cambiado de == 1 a <= 1 por si num_variables es 0 (ej. sin variables)
            for padre in padres:
                hijo = mutar_individuo(padre, intervalo, variabilidad_mutacion)
                nueva_poblacion.append(hijo)
        else: # Para funciones con dos o más variables, realizamos cruce y mutación
            for i in range(0, tamano_poblacion, 2):
                if i + 1 < tamano_poblacion:
                    padre1 = padres[i]
                    padre2 = padres[i+1]

                    # 6. Cruce (Crossover - Punto Único)
                    # Aquí num_variables es garantizado >= 2, por lo que randint(1, num_variables) es seguro
                    punto_cruce = np.random.randint(1, num_variables) 
                    hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
                    hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]

                    # 7. Mutación
                    hijo1 = mutar_individuo(hijo1, intervalo, variabilidad_mutacion)
                    hijo2 = mutar_individuo(hijo2, intervalo, variabilidad_mutacion)

                    nueva_poblacion.append(hijo1)
                    nueva_poblacion.append(hijo2)
                else: # Si queda un padre impar, solo se muta
                    nueva_poblacion.append(mutar_individuo(padres[i], intervalo, variabilidad_mutacion))
        
        # 8. Reemplazo
        poblacion = nueva_poblacion[:tamano_poblacion]

    print("\n--- Algoritmo Genético Finalizado ---")
    if mejor_individuo_global is not None:
        print(f"Mejor individuo encontrado: {mejor_individuo_global}")
        print(f"Mejor aptitud ({objetivo}): {mejor_aptitud_global:.4f}")
        return mejor_individuo_global, mejor_aptitud_global
    else:
        print("No se pudo encontrar un mejor individuo.")
        return None, None