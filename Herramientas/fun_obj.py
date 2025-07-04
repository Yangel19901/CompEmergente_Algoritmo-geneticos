import csv
import sympy
import numpy as np 

import csv
import sympy
import numpy as np # Necesario para sympy.lambdify en el backend 'numpy'

def cargar_funciones_desde_csv(nombre_archivo_csv="fun_obj.csv"):
    
    funciones_cargadas = {}
    try:
        with open(nombre_archivo_csv, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nombre = row['nombre'].strip()
                formula_str = row['formula'].strip()
                
                # Procesar variables
                variables_str = [v.strip() for v in row['variables'].split(',')]
                sympy_vars = [sympy.Symbol(v) for v in variables_str]
                num_genes = len(sympy_vars)

                # Convertir la fórmula a una expresión simbólica de sympy
                try:
                    # Asegurarse de que las funciones comunes como sin, cos, pi estén disponibles para sympy.sympify
                    expr_simbolica = sympy.sympify(formula_str, locals={
                        'pi': sympy.pi, 'E': sympy.E, # Constantes
                        'sin': sympy.sin, 'cos': sympy.cos, 'tan': sympy.tan, # Trigonométricas
                        'asin': sympy.asin, 'acos': sympy.acos, 'atan': sympy.atan, 'atan2': sympy.atan2, # Inversas trigonométricas
                        'sinh': sympy.sinh, 'cosh': sympy.cosh, 'tanh': sympy.tanh, # Hiperbólicas
                        'asinh': sympy.asinh, 'acosh': sympy.acosh, 'atanh': sympy.atanh, # Inversas hiperbólicas
                        'exp': sympy.exp, 'log': sympy.log,  # Exponenciales y logarítmicas
                        'sqrt': sympy.sqrt, 'abs': sympy.Abs, 'Abs': sympy.Abs, # Raíz cuadrada y valor absoluto
                        'floor': sympy.floor, 'ceil': sympy.ceiling, # Redondeo
                        'sign': sympy.sign, # Signo
                        'Max': sympy.Max, 'Min': sympy.Min, # Máximo y mínimo de una lista de argumentos
                        'pow': sympy.Pow, # Potencia simbólica (a**b)
                        'beta': sympy.beta, 'gamma': sympy.gamma, 'factorial': sympy.factorial, # Funciones especiales
                        'binomial': sympy.binomial, 'mod': sympy.Mod, # Combinatoria y módulo
                        'gcd': sympy.gcd, 'lcm': sympy.lcm, # Teoría de números
                        'isprime': sympy.isprime, # Funciones de números primos
                        'prime': sympy.prime, 'nextprime': sympy.nextprime, 'prevprime': sympy.prevprime,
                        'factorint': sympy.factorint, 'primefactors': sympy.primefactors,
                        'combsimp': sympy.combsimp, 'simplify': sympy.simplify, 'factor': sympy.factor, # Simplificación
                        'collect': sympy.collect, # Coleccionar términos
                        'besselj': sympy.besselj, 'bessely': sympy.bessely # Funciones de Bessel (ejemplos de funciones especiales)
                    })
                except sympy.SympifyError as e:
                    print(f"Error: La fórmula '{formula_str}' para la función '{nombre}' no es válida. Detalles: {e}")
                    continue # Salta esta función y ve a la siguiente

                # Crear una función callable que el AG pueda usar para evaluar la aptitud
                funcion_callable = sympy.lambdify(sympy_vars, expr_simbolica, 'numpy')

                # Procesar intervalos
                intervalo_min_str = [rm.strip() for rm in row['rango_min'].split(',')]
                intervalo_max_str = [rm.strip() for rm in row['rango_max'].split(',')]
                intervalo = []
                try:
                    for i in range(num_genes):
                        min_val = float(intervalo_min_str[i])
                        max_val = float(intervalo_max_str[i])
                        intervalo.append((min_val, max_val))
                except (ValueError, IndexError) as e:
                    print(f"Error: Los intervalos para '{nombre}' no son válidos. Detalles: {e}. Asegúrate que sean números y coincidan con el número de variables.")
                    continue

                objetivo = row['objetivo'].strip().lower()
                if objetivo not in ['maximizar', 'minimizar']:
                    print(f"Advertencia: Objetivo '{objetivo}' no reconocido para '{nombre}'. Por defecto se asume 'maximizar'.")
                    objetivo = 'maximizar'

                # Leer la categoría si existe
                categoria = row.get('categoria', 'Sin Categoria').strip()

                # Leer los resultados óptimos de entrada y salida (usando .get para evitar KeyError si la columna no existe)
                resultados_optimo_entrada = row.get('resultados_optimo_entrada', '').strip()
                resultados_optimo_salida = row.get('resultados_optimo_salida', '').strip()
                
                if categoria not in funciones_cargadas:
                    funciones_cargadas[categoria] = []
                
                
                funciones_cargadas[categoria].append({
                    'nombre': nombre,
                    'formula_str': formula_str,
                    'variables': sympy_vars,
                    'intervalo': intervalo,
                    'funcion_callable': funcion_callable,
                    'objetivo': objetivo,
                    'resultados_optimo_entrada': resultados_optimo_entrada,
                    'resultados_optimo_salida': resultados_optimo_salida,
                    'categoria': categoria 
                })
    except FileNotFoundError:
        print(f"Error: El archivo '{nombre_archivo_csv}' no se encontró en el directorio actual.")
        print("Por favor, asegúrate de que el archivo existe y está en el mismo directorio que el script principal.")
        return {} # Retorna un diccionario vacío en caso de error
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer el archivo CSV: {e}")
        return {} # Retorna un diccionario vacío en caso de error
    return funciones_cargadas

def guardar_funciones_en_csv(nombre_archivo_csv, funciones_dict):
   
    # Definir los nombres de las columnas que queremos en el CSV
    fieldnames = [
        'nombre', 'formula', 'variables', 'rango_min', 'rango_max', 
        'objetivo', 'categoria', 'resultados_optimo_entrada', 'resultados_optimo_salida'
    ]
    
    try:
        with open(nombre_archivo_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader() # Escribir la fila de encabezados
            
            for categoria, funciones_lista in funciones_dict.items():
                for func_dict in funciones_lista:
                    # Convertir las variables de sympy.Symbol a strings separadas por comas
                    variables_str = ', '.join([str(v) for v in func_dict['variables']])
                    
                    # Convertir los intervalos a strings separadas por comas
                    rango_min_str = ', '.join([str(i[0]) for i in func_dict['intervalo']])
                    rango_max_str = ', '.join([str(i[1]) for i in func_dict['intervalo']])
                    
                    writer.writerow({
                        'nombre': func_dict['nombre'],
                        'formula': func_dict['formula_str'],
                        'variables': variables_str,
                        'rango_min': rango_min_str,
                        'rango_max': rango_max_str,
                        'objetivo': func_dict['objetivo'],
                        'categoria': func_dict.get('categoria', 'Sin Categoria'), # Usar .get por si no existe
                        'resultados_optimo_entrada': func_dict.get('resultados_optimo_entrada', ''),
                        'resultados_optimo_salida': func_dict.get('resultados_optimo_salida', '')
                    })
        print(f"Funciones guardadas exitosamente en '{nombre_archivo_csv}'.")
    except Exception as e:
        print(f"Error al guardar las funciones en el archivo CSV: {e}")


def mostrar(funcion):
    
    print(f"\n--- Información de la Función: {funcion['nombre']} ---")
    print(f"Nombre: {funcion['nombre']}")
    print(f"Categoría: {funcion.get('categoria', 'Sin Categoria')}")
    print(f"Objetivo: {funcion['objetivo']}")
    print(f"Fórmula: {funcion['formula_str']}")
    
    # Convertir las variables simbólicas a strings para una mejor visualización
    variables_str = ', '.join([str(v) for v in funcion['variables']])
    print(f"Variables: {variables_str}")
    
    # Formatear el intervalo para una mejor visualización
    intervalo_str = []
    for i, (min_val, max_val) in enumerate(funcion['intervalo']):
        var_name = str(funcion['variables'][i]) if i < len(funcion['variables']) else f"var_{i+1}"
        intervalo_str.append(f"{var_name} ∈ [{min_val}, {max_val}]")
    print(f"Intervalo: {', '.join(intervalo_str)}")
    
    # Las funciones callable no se imprimen bien, pero puedes confirmar que existen
    # print(f"Función callable (lista para usar): {funcion['funcion_callable']}") 
    
    print(f"Resultados óptimo entrada: {funcion['resultados_optimo_entrada']}")
    print(f"Resultados óptimo salida: {funcion['resultados_optimo_salida']}")
    print("--------------------------------------------------")

def print_leg(funciones):
    """
    Carga el catálogo de funciones y permite al usuario navegar por categorías y ver detalles.
    """
    print("\n--- Catálogo de funciones objetivo ---\n")
    
    if not funciones:
        print("No hay funciones cargadas. Por favor, asegúrate de que 'fun_obj.csv' existe y tiene datos válidos.")
        return

    while True:
        print("\n--- Categorías Disponibles ---")
        # Obtener una lista de nombres de categorías para mostrarlas numeradas
        categorias_list = list(funciones.keys()) 
        for i, categoria_nombre in enumerate(categorias_list):
            print(f" {i+1}.- Categoría: {categoria_nombre} ({len(funciones[categoria_nombre])} funciones")
        print("\n")

        try:
            categoria_input = input("Ingrese el NÚMERO de la categoría que desea ver (o 'salir' para salir): ").strip()
            
            if categoria_input.lower() == 'salir':
                print("Saliendo del catálogo de funciones. \n\n")
                break # Rompe el bucle exterior y termina la función print_leg

            categoria_idx = int(categoria_input) - 1 # Convertir a índice basado en 0

            if 0 <= categoria_idx < len(categorias_list):
                categoria_seleccionada = categorias_list[categoria_idx] # Obtener el nombre de la categoría real
                
                # Si la categoría existe, mostrar las funciones de esa categoría
                while True:
                    print(f"\n--- Funciones en la categoría '{categoria_seleccionada}' ---")
                    # Mostrar las funciones dentro de la categoría con números
                    funciones_en_categoria = funciones[categoria_seleccionada]
                    if not funciones_en_categoria:
                        print("No hay funciones en esta categoría.")
                        break
                    for i, f_dict in enumerate(funciones_en_categoria):
                        print(f"{i+1}.- {f_dict['nombre']}")
                    print("\n")

                    try:
                        funcion_input = input("Ingrese el NÚMERO de la función que desea ver su información (o '0' para volver a las categorías): ").strip()
                        funcion_idx = int(funcion_input) - 1 # Convertir a índice basado en 0

                        if funcion_idx == -1: # Si el usuario ingresó '0'
                            print("Volviendo a mostrar las categorías... \n\n")
                            break # Rompe el bucle interno y vuelve al bucle de categorías
                        
                        if 0 <= funcion_idx < len(funciones_en_categoria):
                            funcion_encontrada = funciones_en_categoria[funcion_idx]
                            mostrar(funcion_encontrada)
                            # Aquí no hay lógica de selección para el AG, solo se muestra la información
                            input("\nPresione Enter para continuar...") # Pausa para que el usuario lea
                        else:
                            print(f"Número de función no válido. Por favor, ingrese un número entre 1 y {len(funciones_en_categoria)} (o '0' para volver).")
                    except ValueError:
                        print("Entrada no válida. Por favor, ingrese un número.")
                    except Exception as e:
                        print(f"Ocurrió un error al mostrar la función: {e}\n\n")
            else:
                print(f"Número de categoría no válido. Por favor, ingrese un número entre 1 y {len(categorias_list)} (o 'salir').")
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número o 'salir'.")
        except Exception as e:
            print(f"Ocurrió un error al procesar la categoría: {e}\n\n")

def select(funciones):
    """
    Permite al usuario seleccionar una función específica del catálogo.
    Retorna la función seleccionada (como un diccionario) y su categoría,
    o (None, None) si el usuario decide salir o no se selecciona ninguna.
    """
    print("\n--- Seleccionar una función objetivo ---")
    
    if not funciones:
        print("No hay funciones cargadas para seleccionar.")
        return None, None # Retorna (None, None) si no hay funciones

    while True:
        print("\n--- Categorías Disponibles ---")
        categorias_list = list(funciones.keys()) 
        for i, categoria_nombre in enumerate(categorias_list):
            print(f" {i+1}.- Categoría: {categoria_nombre} ({len(funciones[categoria_nombre])} funciones)")
        print("\n")

        try:
            categoria_input = input("Ingrese el NÚMERO de la categoría que desea ver (o 'salir' para cancelar): ").strip()
            
            if categoria_input.lower() == 'salir':
                print("Selección de función cancelada.")
                return None, None # Retorna (None, None) si el usuario decide salir

            categoria_idx = int(categoria_input) - 1 # Convertir a índice basado en 0

            if 0 <= categoria_idx < len(categorias_list):
                categoria_seleccionada = categorias_list[categoria_idx] # Obtener el nombre de la categoría real
                
                while True:
                    print(f"\n--- Funciones en la categoría '{categoria_seleccionada}' ---")
                    funciones_en_categoria = funciones[categoria_seleccionada]
                    if not funciones_en_categoria:
                        print("No hay funciones en esta categoría.")
                        break
                    for i, f_dict in enumerate(funciones_en_categoria):
                        print(f"{i+1}.- {f_dict['nombre']}")
                    print("\n")

                    try:
                        funcion_input = input("Ingrese el NÚMERO de la función que desea seleccionar (o '0' para volver a las categorías): ").strip()
                        funcion_idx = int(funcion_input) - 1 # Convertir a índice basado en 0

                        if funcion_idx == -1: # Si el usuario ingresó '0'
                            print("Volviendo a mostrar las categorías... \n\n")
                            break # Rompe el bucle interno y vuelve al bucle de categorías
                        
                        if 0 <= funcion_idx < len(funciones_en_categoria):
                            funcion_encontrada = funciones_en_categoria[funcion_idx]
                            mostrar(funcion_encontrada) # Muestra la información de la función
                            
                            while True: # Bucle para la confirmación
                                continuar = input("¿Deseas seleccionar esta función? (s/n): ").strip().lower()
                                if continuar == 's':
                                    print(f"Función '{funcion_encontrada['nombre']}' seleccionada.")
                                    return funcion_encontrada, categoria_seleccionada # Retorna la función y su categoría
                                elif continuar == 'n':
                                    print("Función no seleccionada. Volviendo a la lista de funciones en esta categoría.")
                                    break # Vuelve al bucle de selección de función en la misma categoría
                                else:
                                    print("Por favor, ingrese 's' para sí o 'n' para no.")
                        else:
                            print(f"Número de función no válido. Por favor, ingrese un número entre 1 y {len(funciones_en_categoria)} (o '0' para volver).")
                    except ValueError:
                        print("Entrada no válida. Por favor, ingrese un número.")
                    except Exception as e:
                        print(f"Ocurrió un error al seleccionar la función: {e}\n\n")
            else:
                print(f"Número de categoría no válido. Por favor, ingrese un número entre 1 y {len(categorias_list)} (o 'salir').")
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número o 'salir'.")
        except Exception as e:
            print(f"Ocurrió un error al procesar la categoría: {e}\n\n")

    return None, None # Si se sale del bucle principal, no se seleccionó nada

def crear_o_editar_funcion_interactivamente(funciones_dict, funcion_a_editar=None, categoria_actual=None):
    
    
    es_edicion = funcion_a_editar is not None
    accion = "Editar" if es_edicion else "Crear"
    
    print(f"\n--- {accion} una Función Objetivo ---")

    if es_edicion:
        print(f"Estás a punto de editar la función: '{funcion_a_editar.get('nombre', 'N/A')}'")
        nombre_default = funcion_a_editar.get('nombre', '')
        formula_default = funcion_a_editar.get('formula_str', '')
        variables_default = ', '.join([str(v) for v in funcion_a_editar.get('variables', [])])
        objetivo_default = funcion_a_editar.get('objetivo', '')
        categoria_default = funcion_a_editar.get('categoria', '')
        
        rango_min_default = ', '.join([str(i[0]) for i in funcion_a_editar.get('intervalo', [])])
        rango_max_default = ', '.join([str(i[1]) for i in funcion_a_editar.get('intervalo', [])])
        
        # Opcional: mostrar los resultados óptimos actuales para referencia
        resultados_optimo_entrada_default = funcion_a_editar.get('resultados_optimo_entrada', '')
        resultados_optimo_salida_default = funcion_a_editar.get('resultados_optimo_salida', '')

    else:
        nombre_default = ""
        formula_default = ""
        variables_default = ""
        objetivo_default = "maximizar"
        categoria_default = "Personalizadas"
        rango_min_default = ""
        rango_max_default = ""
        resultados_optimo_entrada_default = ""
        resultados_optimo_salida_default = ""

    while True:
        nombre = input(f"Ingrese el nombre de la función [{nombre_default}]: ").strip()
        if not nombre and es_edicion:
            nombre = nombre_default
        if not nombre:
            print("El nombre de la función no puede estar vacío.")
            continue
        
        # Validar si el nombre ya existe (solo para creación o si se cambia el nombre en edición)
        nombre_ya_existe = False
        for cat_name, funcs_in_cat in funciones_dict.items():
            for f in funcs_in_cat:
                if f['nombre'] == nombre and (not es_edicion or f['nombre'] != funcion_a_editar.get('nombre')):
                    nombre_ya_existe = True
                    break
            if nombre_ya_existe:
                break
        
        if nombre_ya_existe:
            print(f"Ya existe una función con el nombre '{nombre}'. Por favor, elija un nombre diferente.")
            continue
        break
    
    while True:
        formula_str = input(f"Ingrese la fórmula de la función (ej. 'x**2 + y**2') [{formula_default}]: ").strip()
        if not formula_str and es_edicion:
            formula_str = formula_default
        if not formula_str:
            print("La fórmula no puede estar vacía.")
            continue
        break

    while True:
        variables_str_input = input(f"Ingrese las variables separadas por comas (ej. 'x,y') [{variables_default}]: ").strip()
        if not variables_str_input and es_edicion:
            variables_str_input = variables_default
        if not variables_str_input:
            print("Las variables no pueden estar vacías.")
            continue
        variables_list = [v.strip() for v in variables_str_input.split(',')]
        if not variables_list or any(not v for v in variables_list):
            print("Debe ingresar al menos una variable y no puede haber variables vacías.")
            continue
        try:
            sympy_vars = [sympy.Symbol(v) for v in variables_list]
            break
        except Exception:
            print("Error al procesar las variables. Asegúrese de que sean nombres válidos.")
            continue

    num_genes = len(sympy_vars)
    intervalo = []
    for i, var in enumerate(sympy_vars):
        while True:
            try:
                min_default = ""
                max_default = ""
                if es_edicion and i < len(funcion_a_editar.get('intervalo', [])):
                    min_default = str(funcion_a_editar['intervalo'][i][0])
                    max_default = str(funcion_a_editar['intervalo'][i][1])

                min_val_str = input(f"Ingrese el rango mínimo para la variable '{var}' [{min_default}]: ").strip()
                if not min_val_str and es_edicion: min_val_str = min_default
                min_val = float(min_val_str)

                max_val_str = input(f"Ingrese el rango máximo para la variable '{var}' [{max_default}]: ").strip()
                if not max_val_str and es_edicion: max_val_str = max_default
                max_val = float(max_val_str)

                if min_val >= max_val:
                    print("El valor mínimo debe ser menor que el valor máximo.")
                else:
                    intervalo.append((min_val, max_val))
                    break
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número.")
            except Exception as e:
                print(f"Error al ingresar el intervalo: {e}")

    while True:
        objetivo_input = input(f"Ingrese el objetivo (maximizar/minimizar) [{objetivo_default}]: ").strip().lower()
        if not objetivo_input and es_edicion:
            objetivo_input = objetivo_default
        if objetivo_input in ['maximizar', 'minimizar']:
            objetivo = objetivo_input
            break
        else:
            print("Objetivo no válido. Por favor, ingrese 'maximizar' o 'minimizar'.")

    categoria = input(f"Ingrese la categoría de la función (ej. 'Matemáticas', 'Finanzas') [{categoria_default}]: ").strip()
    if not categoria and es_edicion:
        categoria = categoria_default
    if not categoria:
        categoria = "Sin Categoria" # Categoría por defecto si no se ingresa nada

    
    # Convertir la fórmula a una expresión simbólica y luego a una función callable
    try:
        expr_simbolica = sympy.sympify(formula_str, locals={
            'pi': sympy.pi, 'E': sympy.E, # Constantes
            'sin': sympy.sin, 'cos': sympy.cos, 'tan': sympy.tan, # Trigonométricas
            'asin': sympy.asin, 'acos': sympy.acos, 'atan': sympy.atan, 'atan2': sympy.atan2, # Inversas trigonométricas
            'sinh': sympy.sinh, 'cosh': sympy.cosh, 'tanh': sympy.tanh, # Hiperbólicas
            'asinh': sympy.asinh, 'acosh': sympy.acosh, 'atanh': sympy.atanh, # Inversas hiperbólicas
            'exp': sympy.exp, 'log': sympy.log,  # Exponenciales y logarítmicas
            'sqrt': sympy.sqrt, 'abs': sympy.Abs, 'Abs': sympy.Abs, # Raíz cuadrada y valor absoluto
            'floor': sympy.floor, 'ceil': sympy.ceiling, # Redondeo
            'sign': sympy.sign, # Signo
            'Max': sympy.Max, 'Min': sympy.Min, # Máximo y mínimo de una lista de argumentos
            'pow': sympy.Pow, # Potencia simbólica (a**b)
            'beta': sympy.beta, 'gamma': sympy.gamma, 'factorial': sympy.factorial, # Funciones especiales
            'binomial': sympy.binomial, 'mod': sympy.Mod, # Combinatoria y módulo
            'gcd': sympy.gcd, 'lcm': sympy.lcm, # Teoría de números
            'isprime': sympy.isprime, # Funciones de números primos
            'prime': sympy.prime, 'nextprime': sympy.nextprime, 'prevprime': sympy.prevprime,
            'factorint': sympy.factorint, 'primefactors': sympy.primefactors,
            'combsimp': sympy.combsimp, 'simplify': sympy.simplify, 'factor': sympy.factor, # Simplificación
            'collect': sympy.collect, # Coleccionar términos
            'besselj': sympy.besselj, 'bessely': sympy.bessely # Funciones de Bessel (ejemplos de funciones especiales)
        })
        funcion_callable = sympy.lambdify(sympy_vars, expr_simbolica, 'numpy')
    except (sympy.SympifyError, Exception) as e:
        print(f"Error al procesar la fórmula: {e}. Por favor, verifique la sintaxis.")
        return None, funciones_dict # Cancela la operación y devuelve el diccionario sin cambios

    nueva_funcion_info = {
        'nombre': nombre,
        'formula_str': formula_str,
        'variables': sympy_vars,
        'intervalo': intervalo,
        'funcion_callable': funcion_callable,
        'objetivo': objetivo,
        'categoria': categoria,
        'resultados_optimo_entrada': [],
        'resultados_optimo_salida':  []
    }

    if es_edicion:
        # Remover la función de su categoría original
        if categoria_actual in funciones_dict and funcion_a_editar in funciones_dict[categoria_actual]:
            funciones_dict[categoria_actual].remove(funcion_a_editar)
            if not funciones_dict[categoria_actual]: # Si la categoría queda vacía, eliminarla
                del funciones_dict[categoria_actual]

    # Añadir la función a la nueva categoría (o la misma si no cambió)
    if categoria not in funciones_dict:
        funciones_dict[categoria] = []
    
    # Añadir la nueva/actualizada función
    # Para la edición, podríamos buscar y reemplazar, pero un remove + append es más directo
    # Aseguramos que no haya duplicados por nombre en la misma categoría (aunque la validación anterior ya lo evita para nombres nuevos)
    
    # Primero, intentamos eliminar si ya existe por nombre en la nueva categoría (manejo de caso de nombre pre-existente en la misma categoría si se re-edita)
    for i, func_in_list in enumerate(funciones_dict[categoria]):
        if func_in_list['nombre'] == nombre:
            funciones_dict[categoria][i] = nueva_funcion_info # Reemplazar el diccionario
            print(f"Función '{nombre}' actualizada exitosamente.")
            guardar_funciones_en_csv("fun_obj.csv", funciones_dict)
            return nueva_funcion_info, funciones_dict
            
    # Si no se encontró (es una nueva función o cambió de categoría), la añadimos
    funciones_dict[categoria].append(nueva_funcion_info)
    print(f"Función '{nombre}' {'creada' if not es_edicion else 'actualizada'} exitosamente.")
    
    # Guardar los cambios al CSV
    guardar_funciones_en_csv("fun_obj.csv", funciones_dict)
    
    return nueva_funcion_info, funciones_dict


