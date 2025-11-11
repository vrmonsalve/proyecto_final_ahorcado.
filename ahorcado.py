"""
AHORCADO - Juego modular en Python
Archivos requeridos (misma carpeta):
 - palabras.txt  (formato: 'categoria:frutas' en una línea, la(s) siguientes contienen palabras separadas por comas)
 - puntajes.txt  (formato por línea: apodo,victorias,derrotas)

Ejecución:
    python ahorcado.py

Características:
 - Carga categorías y palabras desde palabras.txt
 - Pide apodo nuevo (único) y lo valida contra puntajes.txt
 - Permite elegir categoría
 - Lógica del juego con tablero, validación de letras y límite de intentos
 - Actualiza puntajes en puntajes.txt (victoria/derrota)
 - Muestra Top 10 de jugadores por victorias

Estructura modular: funciones con docstrings.
"""

import os
import random
import sys

PALABRAS_FILE = 'palabras.txt'
PUNTAJES_FILE = 'puntajes.txt'
INTENTOS_POR_DEFECTO = 6


def cargar_palabras(ruta=PALABRAS_FILE):
    """Lee el archivo de palabras y devuelve un dict: {categoria: [palabra, ...], ...}.

    Formato aceptado (flexible):
      categoria:frutas
      manzana,pera,banano

    Ignora líneas vacías. Maneja mayúsculas/minúsculas.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe el archivo de palabras: {ruta}")

    categorias = {}
    categoria_actual = None

    with open(ruta, 'r', encoding='utf-8') as f:
        for raw in f:
            linea = raw.strip()
            if not linea:
                continue
            if linea.lower().startswith('categoria:'):
                categoria_actual = linea.split(':', 1)[1].strip().lower()
                categorias.setdefault(categoria_actual, [])
            else:
                # Expect comma-separated words; allow spaces
                palabras = [w.strip().lower() for w in linea.split(',') if w.strip()]
                if categoria_actual is None:
                    # Si no hay categoria definida, usar 'sin_categoria'
                    categorias.setdefault('sin_categoria', [])
                    categorias['sin_categoria'].extend(palabras)
                else:
                    categorias[categoria_actual].extend(palabras)

    return categorias


def cargar_puntajes(ruta=PUNTAJES_FILE):
    """Carga puntajes desde archivo. Devuelve dict {apodo: {'v':int,'d':int}}"""
    puntajes = {}
    if not os.path.exists(ruta):
        return puntajes

    with open(ruta, 'r', encoding='utf-8') as f:
        for raw in f:
            linea = raw.strip()
            if not linea:
                continue
            partes = [p.strip() for p in linea.split(',')]
            if len(partes) < 3:
                continue
            apodo, victorias, derrotas = partes[0], partes[1], partes[2]
            try:
                puntajes[apodo] = {'v': int(victorias), 'd': int(derrotas)}
            except ValueError:
                # saltar línea corrupta
                continue
    return puntajes


def guardar_puntajes(puntajes, ruta=PUNTAJES_FILE):
    """Guarda el dict de puntajes en el archivo en formato apodo,victorias,derrotas por línea."""
    with open(ruta, 'w', encoding='utf-8') as f:
        for apodo, stats in puntajes.items():
            f.write(f"{apodo},{stats['v']},{stats['d']}\n")


def gestionar_jugador(puntajes):
    """Solicita un apodo y valida que sea único. Si apodo no existe, lo añade con 0,0 y devuelve apodo y puntajes actualizado."""
    while True:
        apodo = input('Ingresa tu apodo (sin comas): ').strip()
        if not apodo:
            print('Apodo vacío. Ingresa uno válido.')
            continue
        if ',' in apodo:
            print('El apodo no puede contener comas.')
            continue
        if apodo in puntajes:
            print('Ese apodo ya existe. Elige otro.')
            continue
        # Apodo nuevo: añadir
        puntajes[apodo] = {'v': 0, 'd': 0}
        guardar_puntajes(puntajes)
        return apodo


def elegir_categoria(categorias):
    """Muestra las categorías disponibles y permite elegir. Devuelve la clave de categoría seleccionada."""
    claves = list(categorias.keys())
    if not claves:
        raise ValueError('No hay categorías disponibles en el archivo de palabras.')

    print('\nCategorías disponibles:')
    for i, c in enumerate(claves, start=1):
        print(f"  {i}. {c} ({len(categorias[c])} palabras)")
    print(f"  {len(claves)+1}. Aleatoria (cualquier categoría)")

    while True:
        try:
            sel = input(f'Selecciona categoría [1-{len(claves)+1}]: ').strip()
            if not sel:
                print('Seleccion vacía. Ingresa un número.')
                continue
            idx = int(sel)
            if 1 <= idx <= len(claves):
                return claves[idx-1]
            if idx == len(claves)+1:
                return random.choice(claves)
            print('Número fuera de rango.')
        except ValueError:
            print('Entrada inválida. Ingresa un número.')


def mostrar_tablero(palabra, letras_acertadas):
    """Devuelve la representación con guiones y letras acertadas."""
    return ' '.join([ch if ch in letras_acertadas else '_' for ch in palabra])


def jugar_partida(palabras_categoria, apodo, puntajes, intentos_max=INTENTOS_POR_DEFECTO):
    """Lógica principal del juego. Devuelve True si gana, False si pierde."""
    palabra = random.choice(palabras_categoria).lower()
    palabra = palabra.strip()
    letras_acertadas = set()
    letras_erradas = set()

    intentos_restantes = intentos_max

    # Considerar caracteres especiales (espacios) como ya descubiertos
    for ch in palabra:
        if not ch.isalpha():
            letras_acertadas.add(ch)

    while True:
        print('\n' + mostrar_tablero(palabra, letras_acertadas))
        print(f'Intentos restantes: {intentos_restantes} | Errores: {", ".join(sorted(letras_erradas)) if letras_erradas else "ninguno"}')

        # Revisar victoria
        if all((ch in letras_acertadas) for ch in palabra):
            print(f'¡Felicidades {apodo}! Adivinaste la palabra: {palabra}')
            actualizar_puntajes(puntajes, apodo, True)
            return True

        if intentos_restantes <= 0:
            print(f'Has perdido. La palabra era: {palabra}')
            actualizar_puntajes(puntajes, apodo, False)
            return False

        entrada = input('Ingresa una letra: ').strip().lower()
        if not entrada:
            print('Entrada vacía. Intenta otra vez.')
            continue
        if len(entrada) != 1:
            print('Ingresa solo una letra a la vez.')
            continue
        if not entrada.isalpha():
            print('Ingresa solo letras del alfabeto.')
            continue
        if entrada in letras_acertadas or entrada in letras_erradas:
            print('Ya ingresaste esa letra. Prueba otra.')
            continue

        if entrada in palabra:
            letras_acertadas.add(entrada)
            print('Letra correcta.')
        else:
            letras_erradas.add(entrada)
            intentos_restantes -= 1
            print('Letra incorrecta.')


def actualizar_puntajes(puntajes, apodo, gano):
    """Actualiza el dict de puntajes y lo guarda en archivo."""
    if apodo not in puntajes:
        puntajes[apodo] = {'v': 0, 'd': 0}
    if gano:
        puntajes[apodo]['v'] += 1
    else:
        puntajes[apodo]['d'] += 1
    guardar_puntajes(puntajes)


def mostrar_top_10(ruta=PUNTAJES_FILE):
    """Lee puntajes y muestra top 10 ordenado por victorias desc, luego derrotas asc."""
    puntajes = cargar_puntajes(ruta)
    if not puntajes:
        print('No hay puntajes registrados.')
        return

    lista = [(apodo, s['v'], s['d']) for apodo, s in puntajes.items()]
    lista.sort(key=lambda x: (-x[1], x[2], x[0]))

    print('\n===== TOP 10 JUGADORES =====')
    print('Pos | Jugador | Victorias | Derrotas')
    for i, (apodo, v, d) in enumerate(lista[:10], start=1):
        print(f'{i:>3} | {apodo} | {v} | {d}')
    print('============================\n')


def mostrar_menu():
    print('\n--- MENÚ ---')
    print('1. Jugar partida')
    print('2. Mostrar Top 10')
    print('3. Salir')


def main():
    try:
        categorias = cargar_palabras()
    except Exception as e:
        print('Error al cargar palabras:', e)
        sys.exit(1)

    puntajes = cargar_puntajes()

    while True:
        mostrar_menu()
        opcion = input('Elige una opción [1-3]: ').strip()
        if opcion == '1':
            apodo = gestionar_jugador(puntajes)
            categoria_clave = elegir_categoria(categorias)
            palabras_categoria = categorias.get(categoria_clave, [])
            if not palabras_categoria:
                print('La categoría seleccionada no contiene palabras. Elige otra.')
                continue
            jugar_partida(palabras_categoria, apodo, puntajes)
        elif opcion == '2':
            mostrar_top_10()
        elif opcion == '3':
            print('Adiós.')
            break
        else:
            print('Opción inválida.')


if __name__ == '__main__':
    main()

