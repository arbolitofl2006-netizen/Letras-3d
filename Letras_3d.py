import math
import unicodedata
import tkinter as tk

ANCHO, ALTO = 1000, 700
TEXTO = "GRAFICACION"      # Cambia el texto del letrero
PROFUNDIDAD = 2.0         
TAMANO_BLOQUE = 18         

COLORES = [
    "#FF33A3",
    "#830472",
    "#FFE61A",  
    "#8CE99C",  
    "#C40FFC",  
    "#DAABFD", 
]

# cada letra es una cuadrícula, "#" = bloque
FUENTE = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ####", "#    ", "#    ", "#  ##", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "Ñ": [" ### ", "     ", "##  #", "# # #", "#  ##", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
    "4": ["#   #", "#   #", "#   #", "#####", "    #", "    #", "    #"],
    "5": ["#####", "#    ", "#    ", "#### ", "    #", "    #", "#### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    " ": ["    "] * 7,
}

def normalizar(texto):
    """Pasa a mayúsculas y quita acentos (excepto la Ñ)."""
    resultado = ""
    for c in texto.upper():
        if c != "Ñ":
            c = unicodedata.normalize("NFD", c)[0]
        resultado += c if c in FUENTE else " "
    return resultado

def suavizar(t):
    """Interpolación suave entre 0 y 1."""
    return (1 - math.cos(math.pi * t)) / 2

# Puntos de traslación (esquinas relativas a la pantalla)
PX_T, PY_T = 280, 180
PUNTOS = [(0, 0), (-PX_T, PY_T), (PX_T, PY_T), (PX_T, -PY_T), (-PX_T, -PY_T), (0, 0)]

FASES = [
    ("Rotacion en Y", 4.0),
    ("Rotacion en Z", 4.0),
    ("Traslacion al punto 1 (arriba izquierda)", 1.5),
    ("Traslacion al punto 2 (arriba derecha)", 1.5),
    ("Traslacion al punto 3 (abajo derecha)", 1.5),
    ("Traslacion al punto 4 (abajo izquierda)", 1.5),
    ("Traslacion de regreso al centro", 1.5),
    ("Aumento de tamano", 4.0),
]

def calcular_transformacion(fase, t):
    tx, ty, rot_y, rot_z, escala = 0.0, 0.0, 0.0, 0.0, 1.0
    s = suavizar(t)
    if fase == 0:
        rot_y = 360 * s
    elif fase == 1:
        rot_z = 360 * s
    elif 2 <= fase <= 6:
        x0, y0 = PUNTOS[fase - 2]
        x1, y1 = PUNTOS[fase - 1]
        tx = x0 + (x1 - x0) * s
        ty = y0 + (y1 - y0) * s
    elif fase == 7:
        escala = 1 + 1.2 * math.sin(math.pi * t)
    return tx, ty, rot_y, rot_z, escala

def generar_geometria_bloques(texto):
    """Genera una lista de cubos base para el texto centrado."""
    texto_norm = normalizar(texto)
    ancho_total = len(texto_norm) * 6 - 1
    alto_total = 7
    bloques = []
    
    for i, letra in enumerate(texto_norm):
        color = COLORES[i % len(COLORES)]
        for fila, linea in enumerate(FUENTE[letra]):
            for col, celda in enumerate(linea):
                if celda == "#":
                    # Coordenadas locales centradas
                    x = i * 6 + col - ancho_total / 2
                    y = (alto_total - 1 - fila) - alto_total / 2
                    bloques.append((x, y, color))
    return bloques

def main():
    root = tk.Tk()
    root.title("Letrero 3D con Transformaciones - Tkinter")
    root.geometry(f"{ANCHO}x{ALTO}")
    root.resizable(False, False)

    canvas = tk.Canvas(root, width=ANCHO, height=ALTO, bg="#14141F", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    bloques_base = generar_geometria_bloques(TEXTO)

    fase = 0
    tiempo_fase = 0.0
    pausado = False
    reloj_previo = root.tk.call('clock', 'milliseconds')

    def al_presionar_tecla(evento):
        nonlocal pausado
        if evento.keysym == "Escape":
            root.destroy()
        elif evento.keysym == "space":
            pausado = not pausado

    root.bind("<KeyPress>", al_presionar_tecla)

    def actualizar():
        nonlocal fase, tiempo_fase, reloj_previo
        ahora = root.tk.call('clock', 'milliseconds')
        dt = (ahora - reloj_previo) / 1000.0
        reloj_previo = ahora

        if not pausado:
            tiempo_fase += dt
            if tiempo_fase >= FASES[fase][1]:
                tiempo_fase = 0.0
                fase = (fase + 1) % len(FASES)

        t = tiempo_fase / FASES[fase][1]
        tx, ty, rot_y, rot_z, escala = calcular_transformacion(fase, t)

        canvas.delete("all")

        centro_x, centro_y = ANCHO // 2 + tx, ALTO // 2 + ty

        # Convertir ángulos a radianes
        rad_y = math.radians(rot_y)
        rad_z = math.radians(rot_z)
        # Inclinaciones fijas estéticas de referencia
        inc_x = math.radians(15)
        inc_y = math.radians(-20)

        # rotaciones globales
        # bloque ordenado por profundidad 
        elementos_render = []

        for bx, by, color in bloques_base:
            # Escalamiento del bloque individual
            x = bx * TAMANO_BLOQUE * escala
            y = by * TAMANO_BLOQUE * escala
            z = 0.0  # Centro de profundidad

            #Rotación en Z
            cos_z, sin_z = math.cos(rad_z), math.sin(rad_z)
            rx1 = x * cos_z - y * sin_z
            ry1 = x * sin_z + y * cos_z
            rz1 = z

            #Rotación en Y
            cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
            rx2 = rx1 * cos_y + rz1 * sin_y
            ry2 = ry1
            rz2 = -rx1 * sin_y + rz1 * cos_y

            # Inclinación en X
            cos_ix, sin_ix = math.cos(inc_x), math.sin(inc_x)
            ry3 = ry2 * cos_ix - rz2 * sin_ix
            rz3 = ry2 * sin_ix + rz2 * cos_ix
            rx3 = rx2

            # Inclinación en Y
            cos_iy, sin_iy = math.cos(inc_y), math.sin(inc_y)
            rx4 = rx3 * cos_iy + rz3 * sin_iy
            ry4 = ry3
            rz4 = -rx3 * sin_iy + rz3 * cos_iy

            # Proyección final en pantalla
            screen_x = centro_x + rx4
            screen_y = centro_y - ry4  # Invertir Y de pantalla

            elementos_render.append((rz4, screen_x, screen_y, color))

        # Ordenar por profundidad (Painter's algorithm: los más lejanos primero)
        elementos_render.sort(key=lambda item: item[0])

        # Dibujar bloques en pantalla
        t_cubo = (TAMANO_BLOQUE * escala) / 2
        for z_prof, sx, sy, color in elementos_render:
            # Dibujar un pequeño rectángulo simulando el bloque 3D plano con relieve
            canvas.create_rectangle(
                sx - t_cubo, sy - t_cubo,
                sx + t_cubo, sy + t_cubo,
                fill=color, outline="#222222", width=1
            )

        # Textos de interfaz en pantalla
        canvas.create_text(20, 25, anchor="nw", text=f"Fase: {FASES[fase][0]}", fill="white", font=("Arial", 14, "bold"))
        valores = f"x={tx:+.1f}  y={ty:+.1f}  rotY={rot_y:.0f}  rotZ={rot_z:.0f}  escala={escala:.2f}"
        canvas.create_text(20, ALTO - 30, anchor="nw", text=valores, fill="#AAAAAA", font=("Arial", 11))
        
        if pausado:
            canvas.create_text(ANCHO - 90, 25, anchor="ne", text="PAUSA", fill="#FF5555", font=("Arial", 14, "bold"))
        root.after(16, actualizar)

    root.after(16, actualizar)
    root.mainloop()
if __name__ == "__main__":
    main()