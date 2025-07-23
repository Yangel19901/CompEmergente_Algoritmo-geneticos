import Herramientas.fun_obj as func
import Herramientas.AG as AG
import numpy as np # Necesario para la comparación, especialmente para np.inf o np.nan

def main():
    
    print("Inicializando el módulo de funciones objetivo\n")
    
    # Cargar las funciones una vez al inicio
    funciones = func.cargar_funciones_desde_csv("fun_obj.csv")
    
    # Variable para almacenar la función objetivo actualmente seleccionada para el AG
    funcion_objetivo_actual = None 

    while True:
        print("\n--- Estudio de Algoritmo Genético ---")
        print("¿Qué te gustaría hacer?")
        print("1. Catálogo de funciones objetivo")
        print("2. Seleccionar una función objetivo")
        print("3. Crear o editar una función objetivo")
        print("4. Inicializar algoritmo genético con una función objetivo")
        print("5. Salir")
        
        option = input("\nIndique su opción: ").strip().lower()
        print("\n") # Espacio para claridad

        if option == '1' or option == 'catalogo' or option == '1.':
            func.print_leg(funciones)
        
        elif option == '2' or option == 'seleccionar' or option == '2.':
            print("Seleccionando una función objetivo...\n")
            # func.select ahora devuelve la función seleccionada y su categoría
            funcion_seleccionada, categoria_seleccionada = func.select(funciones) 
            if funcion_seleccionada:
                funcion_objetivo_actual = funcion_seleccionada # Guarda la función seleccionada para la opción 4
                print(f"Función '{funcion_seleccionada.get('nombre', 'N/A')}' ha sido seleccionada para el algoritmo genético.")
            else:
                print("No se seleccionó ninguna función.")
        
        elif option == '3' or option == 'crear' or option == 'editar' or option == '3.':
            print("--- Gestión de Funciones Objetivo ---")
            sub_option = input("¿Deseas 'crear' una función nueva o 'editar' una existente? (crear/editar): ").strip().lower()

            if sub_option == 'crear':
                print("Creando una nueva función objetivo...")
                nueva_funcion_info, funciones = func.crear_o_editar_funcion_interactivamente(funciones)
                # 'funciones' se actualiza con la versión más reciente tras la operación
                if nueva_funcion_info:
                    print(f"Operación de creación completada.")
                else:
                    print("La creación de la función fue cancelada o falló.")

            elif sub_option == 'editar':
                print("Selecciona la función a editar:")
                funcion_a_editar, categoria_de_funcion_a_editar = func.select(funciones) # Usa func.select para elegir
                
                if funcion_a_editar:
                    print(f"Editando la función '{funcion_a_editar.get('nombre', 'N/A')}'...")
                    funcion_actualizada_info, funciones = func.crear_o_editar_funcion_interactivamente(
                        funciones, 
                        funcion_a_editar=funcion_a_editar, 
                        categoria_actual=categoria_de_funcion_a_editar
                    )
                    # 'funciones' se actualiza con la versión más reciente tras la operación
                    if funcion_actualizada_info:
                        print(f"Operación de edición completada.")
                    else:
                        print("La edición de la función fue cancelada o falló.")
                else:
                    print("No se seleccionó ninguna función para editar.")
            else:
                print("Opción no válida. Volviendo al menú principal.")

        elif option == '4' or option == 'inicializar' or option == '4.':
            print("Inicializando algoritmo genético con una función objetivo...")
            if funcion_objetivo_actual:
                print(f"La función seleccionada es: {funcion_objetivo_actual['nombre']}")
                print(f"Fórmula: {funcion_objetivo_actual['formula_str']}")
                
                # Solicitar parámetros del GA al usuario con valores por defecto
                tamano_poblacion_input = input(f"Ingrese el tamaño de la población (por defecto 10): ").strip()
                tamano_poblacion = int(tamano_poblacion_input) if tamano_poblacion_input else 10

                umbral_diferencia_input = input(f"Ingrese el umbral de diferencia para convergencia (por defecto 0.05): ").strip()
                umbral_diferencia = float(umbral_diferencia_input) if umbral_diferencia_input else 0.05

                max_iteraciones_input = input(f"Ingrese el número máximo de iteraciones (por defecto 500): ").strip()
                max_iteraciones = int(max_iteraciones_input) if max_iteraciones_input else 500

                variabilidad_mutacion_input = input(f"Ingrese la variabilidad de la mutación (por defecto 1.0): ").strip()
                variabilidad_mutacion = float(variabilidad_mutacion_input) if variabilidad_mutacion_input else 1.0

                # Ejecutar el algoritmo genético, llamando a la función desde el módulo AG
                mejor_solucion, mejor_valor = AG.ejecutar_algoritmo_genetico(
                    funcion_objetivo_actual,
                    tamano_poblacion=tamano_poblacion,
                    umbral_diferencia=umbral_diferencia,
                    max_iteraciones=max_iteraciones,
                    variabilidad_mutacion=variabilidad_mutacion
                )
                
                if mejor_solucion is not None:
                    print(f"\n--- Resultados Finales para '{funcion_objetivo_actual['nombre']}' ---")
                    # Mostrar las variables y sus valores
                    variables_nombres = [str(v) for v in funcion_objetivo_actual['variables']]
                    solucion_str = ", ".join([f"{var}={val:.4f}" for var, val in zip(variables_nombres, mejor_solucion)])
                    print(f"Mejor combinación de variables encontrada por el AG: {solucion_str}")
                    print(f"Valor óptimo encontrado por el AG ({funcion_objetivo_actual['objetivo']}): {mejor_valor:.4f}")

                    
                    # Esto actualiza el diccionario 'funcion_objetivo_actual' que es una referencia
                    funcion_objetivo_actual['resultados_optimo_entrada'] = mejor_solucion
                    funcion_objetivo_actual['resultados_optimo_salida'] = mejor_valor
                    print("\n¡Los resultados del algoritmo genético se han guardado como el nuevo óptimo conocido para esta función!")
                    
                    opt_entrada_conocida = funcion_objetivo_actual['resultados_optimo_entrada']
                    opt_salida_conocida = funcion_objetivo_actual['resultados_optimo_salida']

                    if opt_entrada_conocida is not None and opt_salida_conocida is not None:
                        # Para evitar comparaciones redundantes si el "óptimo conocido" era None y ahora se actualizó
                        
                        print(f"\n--- Comparación con Óptimo 'Conocido' (Ahora es el resultado del AG) ---")
                        print(f"Óptimo 'Conocido' (Entrada): {opt_entrada_conocida}")
                        print(f"Óptimo 'Conocido' (Salida): {opt_salida_conocida:.4f}")
                        
                        try:
                            # Intentamos convertir la salida óptima conocida a un número para la comparación
                            known_optimal_value = float(opt_salida_conocida)
                            difference = abs(mejor_valor - known_optimal_value)
                            
                            if np.isinf(mejor_valor) or np.isnan(mejor_valor):
                                print("El resultado del algoritmo genético es infinito o no es un número, no se puede comparar directamente.")
                            else:
                                print(f"Diferencia absoluta con el óptimo 'conocido': {difference:.4f}")
                                if difference < 0.0001: # Un umbral más estricto porque se están comparando consigo mismos
                                    print("¡El algoritmo genético encontró un valor que coincide con el 'óptimo conocido' que acaba de establecerse!")
                                else:
                                    print("Nota: El algoritmo genético encontró un valor ligeramente diferente al óptimo 'conocido' recién establecido.")
                        except ValueError:
                            print("No se pudo comparar el resultado con el óptimo 'conocido' (la salida conocida no es un número válido).")
                    

                else:
                    print("El algoritmo genético no pudo encontrar una solución óptima.")

            else:
                print("Primero debes seleccionar una función objetivo (Opción 2) o crear/editar una (Opción 3) para inicializar el algoritmo genético.")

        elif option == 'salir' or option == '5' or option == '5.':
            guardar = input("¿Deseas guardar los cambios realizados en las funciones objetivo? (s/n): ").strip().lower()
            if guardar == 's':
                func.guardar_funciones_en_csv("fun_obj.csv", funciones)
                print("Cambios guardados exitosamente.")
            else:
                print("Cambios no guardados.")
            print("Saliendo del módulo de funciones objetivo.")
            break
        
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

# Punto de entrada del programa
if __name__ == '__main__':
    main()