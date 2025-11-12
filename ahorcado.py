import random
import sys
import os
import time
import tempfile

PALABRAS_FILE = 'palabras.txt'
PUNTAJES_FILE = 'puntajes.txt'

# ---------------------- UTILIDADES DE ENTRADA ----------------------

def safe_input(prompt, default=None):
    try:
        return input(prompt)
    except (EOFError, OSError):
        return default

def is_interactive():
    try:
        return sys.stdin.isatty()
    except Exception:
        return False

# ---------------------- CARGA DE ARCHIVOS ----------------------

def cargar_palabras(path=PALABRAS_FILE, crear_si_falta=True):
    if not os.path.exists(path):
        if crear_si_falta:
            ejemplo = """categoria:frutas
manzana,pera,banano,naranja,fresa,mango,piña,melocoton,kiwi,uva

categoria:animales
perro,gato,elefante,tigre,leon,cebra,jirafa,caballo,cocodrilo,pinguino
"""
            with open(path, 'w', encoding='utf-8') as f:
                f.write(ejemplo)
            print(f"[i] Archivo '{path}' no encontrado: se ha creado un ejemplo en la carpeta actual.")
        else:
            raise FileNotFoundError(path)

    categorias = {}
    categoria_actual = None
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            linea = raw.strip()
            if not linea:
                continue
            if linea.lower().startswith('categoria:'):
                categoria_actual = linea.split(':', 1)[1].strip().lower()
                categorias.setdefault(categoria_actual, [])
            else:
                palabras = [w.strip().lower() for w in linea.split(',') if w.strip()]
                if categoria_actual is None:
                    categorias.setdefault('sin_categoria', []).extend(palabras)
                else:
                    categorias[categoria_actual].extend(palabras)
    return categorias

def cargar_puntajes(path=PUNTAJES_FILE):
    puntajes = {}
    if not os.path.exists(path):
        return puntajes
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            linea = raw.strip()
            if not linea or ',' not in linea:
                continue
            partes = [p.strip() for p in linea.split(',')]
            if len(partes) < 3:
                continue
            apodo = partes[0]
            try:
                v = int(partes[1]); d = int(partes[2])
            except ValueError:
                continue
            puntajes[apodo] = [v, d]
    return puntajes

def guardar_puntajes(puntajes, path=PUNTAJES_FILE):
    with open(path, 'w', encoding='utf-8') as f:
        for apodo, (v, d) in puntajes.items():
            f.write(f"{apodo},{v},{d}\n")

# ---------------------- INTERFAZ ----------------------

def dibujar_cabecera():
    return r'''
     █████╗ ██╗  ██╗ ██████╗ ██████╗  █████╗  ██████╗ ██████╗  █████╗ ██████╗ 
    ██╔══██╗██║  ██║██╔════╝ ██╔══██╗██╔══██╗██╔════╝ ██╔══██╗██╔══██╗██╔══██╗
    ███████║███████║██║  ███╗██████╔╝███████║██║  ███╗██████╔╝███████║██║  ██║
    ██╔══██║██╔══██║██║   ██║██╔══██╗██╔══██║██║   ██║██╔══██╗██╔══██║██║  ██║
    ██║  ██║██║  ██║╚██████╔╝██║  ██║██║  ██║╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
                            
                    AHORCADO - VERSIÓN MEJORADA
    '''

def mostrar_menu():
    print(dibujar_cabecera())
    print('--- MENÚ ---')
    print('1. Jugar partida')
    print('2. Mostrar Top 10')
    print('3. Salir')

# ---------------------- LÓGICA DEL JUEGO ----------------------

def elegir_dificultad(input_fn=safe_input):
    prompt = ('\nSeleccione dificultad:\n'
              '  1. Fácil (8 intentos)\n'
              '  2. Normal (6 intentos)\n'
              '  3. Difícil (4 intentos)\n'
              '→ ')
    sel = input_fn(prompt, '2')
    if sel is None:
        sel = '2'
    sel = sel.strip()
    return {'1': 8, '2': 6, '3': 4}.get(sel, 6)

def pedir_pista(palabra, letras_descubiertas):
    opciones = [c for c in set(palabra) if c.isalpha() and c not in letras_descubiertas]
    if not opciones:
        return None
    return random.choice(opciones)

def jugar_partida(categorias, input_fn=safe_input, nombre_jugador='Anon'):
    claves = list(categorias.keys())
    if not claves:
        print('[!] No hay categorías cargadas.')
        return False
    if is_interactive():
        print('\nCategorías:')
        for c in claves:
            print(f' - {c} ({len(categorias[c])} palabras)')
        elec = input_fn('\nEscribe el nombre de la categoría o deja vacío para aleatoria: ', '')
        if elec is None or elec.strip() == '':
            categoria = random.choice(claves)
        else:
            categoria = elec.strip().lower()
            if categoria not in categorias:
                print('[!] Categoría no encontrada — se usará una aleatoria.')
                categoria = random.choice(claves)
    else:
        categoria = random.choice(claves)

    palabra = random.choice(categorias[categoria]).lower().strip()
    intentos = elegir_dificultad(input_fn)
    letras_acertadas = set(ch for ch in palabra if not ch.isalpha())
    letras_erradas = set()
    inicio = time.time()

    while True:
        tablero = ' '.join([ch if ch in letras_acertadas else '_' for ch in palabra])
        print('\n' + tablero)
        print(f'Intentos: {intentos} | Errores: {", ".join(sorted(letras_erradas)) if letras_erradas else "ninguno"}')

        if all((ch in letras_acertadas) for ch in palabra):
            tiempo = int(time.time() - inicio)
            bonus = max(0, 5 - tiempo // 10)
            print(f'¡Felicidades {nombre_jugador}! Adivinaste la palabra: {palabra} (+{bonus} puntos bonus)')
            return True
        if intentos <= 0:
            print(f'Has perdido. La palabra era: {palabra}')
            return False

        entrada = input_fn("Ingresa una letra, '/pista' o '/salir': ", '')
        if entrada is None:
            print('[!] Entrada no disponible, saliendo de la partida.')
            return False
        entrada = entrada.strip().lower()

        if entrada == '/salir':
            print('Abandonando...')
            return False
        if entrada == '/pista':
            pista = pedir_pista(palabra, letras_acertadas)
            if pista:
                letras_acertadas.add(pista)
                intentos -= 1
                print(f'Pista: la letra {pista}')
            else:
                print('No hay pistas disponibles.')
            continue
        if len(entrada) != 1 or not entrada.isalpha():
            print('Ingresa una letra válida.')
            continue
        letra = entrada
        if letra in letras_acertadas or letra in letras_erradas:
            print('Ya intentaste esa letra.')
            continue
        if letra in palabra:
            letras_acertadas.add(letra)
            print('Letra correcta!')
        else:
            letras_erradas.add(letra)
            intentos -= 1
            print('Letra incorrecta.')

# ---------------------- TOP 10 ----------------------

def mostrar_top10(path=PUNTAJES_FILE):
    if not os.path.exists(path):
        print('\nAún no hay registros de jugadores.\n')
        return
    puntajes = cargar_puntajes(path)
    lista = sorted(puntajes.items(), key=lambda kv: (-kv[1][0], kv[1][1], kv[0]))
    print('\n===== TOP 10 =====')
    for i, (apodo, (v, d)) in enumerate(lista[:10], start=1):
        print(f'{i}. {apodo} - {v} victorias, {d} derrotas')

def guardar_resultado(nombre, gano, path=PUNTAJES_FILE):
    datos = cargar_puntajes(path)
    if nombre not in datos:
        datos[nombre] = [0, 0]
    if gano:
        datos[nombre][0] += 1
    else:
        datos[nombre][1] += 1
    guardar_puntajes(datos, path)

# ---------------------- SECRETO OCULTO ----------------------

def mostrar_secreto(categorias):
    print("\n🔒 SECRETO OCULTO ACTIVADO 🔒")
    print("Todas las palabras cargadas:\n")
    for cat, palabras in categorias.items():
        print(f"[{cat.upper()}]: {', '.join(palabras)}")
    input("\nPresiona ENTER para volver al menú...")

# ---------------------- MAIN ----------------------

def main(argv):
    if '--test' in argv:
        return

    categorias = cargar_palabras()

    while True:
        mostrar_menu()
        opcion = safe_input('→ ', '1')
        if opcion is None:
            print('[!] Entrada no disponible; saliendo.')
            break
        opcion = opcion.strip().lower()

        if opcion == '1':
            nombre = safe_input('\nIngresa tu apodo: ', 'Anon') or 'Anon'
            gano = jugar_partida(categorias, input_fn=safe_input, nombre_jugador=nombre)
            guardar_resultado(nombre, gano)
        elif opcion == '2':
            mostrar_top10()
        elif opcion == '3':
            print('\nGracias por jugar. ¡Hasta pronto!')
            break
        elif opcion == 'secreto':
            mostrar_secreto(categorias)
        else:
            print('[!] Opción inválida.')

if __name__ == '__main__':
    main(sys.argv)
