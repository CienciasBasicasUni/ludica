"""Diagramas de referencia de Galletas S.A. en formato Graphviz DOT.

Colores de corriente = colores de las fichas de lego:
  azul = alimentación fresca · rojo = reciclo / recortes · amarillo = purga y pérdidas · verde = bypass
Si se pasa un diccionario de datos `d` (de motor.datos_r1 / datos_r2) el diagrama sale con los números del equipo;
sin `d` sale con símbolos (es la solución de referencia del planteamiento).
"""

AZUL, ROJO, AMARILLO, VERDE = "#2563eb", "#dc2626", "#d97706", "#16a34a"

_CAB = ('digraph G {\n  rankdir=LR; bgcolor="transparent"; nodesep=0.5; ranksep=0.7;\n'
        '  node [shape=box, style="rounded,filled", fillcolor="#e5e7eb", color="#374151", fontname="Helvetica", '
        'fontsize=15, margin="0.25,0.15"];\n'
        '  edge [fontname="Helvetica", fontsize=13, penwidth=3];\n')


def _n(x):
    return f"{x:,.1f}".replace(",", " ").rstrip("0").rstrip(".") if x != int(x) else f"{int(x):,}".replace(",", " ")


def _entrada(nombre, color):
    return f'  "{nombre}" [shape=plaintext, style="", fontcolor="{color}", fontsize=14];\n'


def dot_reciclo(d=None):
    f0 = f"F0 = {_n(d['f0a'])} mol/h\\n(A puro, fresco)" if d else "F0\\n(A puro, fresco)"
    f = f"F = {_n(d['fa'])} mol/h" if d else "F"
    r = f"R = {_n(d['ra'])} mol/h\\n(A sin reaccionar)" if d else "R\\n(A sin reaccionar)"
    b = f"B = {_n(d['f0a'])} mol/h\\n(producto)" if d else "B\\n(producto)"
    x = f"\\nX paso = {d['xa']:.0%}" if d else "\\nX paso"
    return (_CAB + _entrada("fresco", AZUL) +
            '  fresco [label="' + f0 + '"];\n'
            '  Mezclador; Reactor [label="Reactor' + x + '"]; Separador;\n'
            '  producto [shape=plaintext, style="", label="' + b + '"];\n'
            '  fresco -> Mezclador [color="' + AZUL + '"];\n'
            '  Mezclador -> Reactor [label="' + f + '", color="#111827"];\n'
            '  Reactor -> Separador [label="A + B", color="#111827"];\n'
            '  Separador -> producto [color="#111827"];\n'
            '  Separador -> Mezclador [label="' + r + '", color="' + ROJO + '", constraint=false];\n}\n')


def dot_purga(d=None):
    f0 = f"F0 = {_n(d['f0b'])} mol/h\\nA + {d['y0']:.0%} inerte" if d else "F0\\nA + inerte"
    f = f"F" if not d else "F"
    r = f"R = {_n(d['rb'])} mol/h" if d else "R (reciclo)"
    p = f"P = {_n(d['p'])} mol/h\\n(purga, {d['yi']:.0%} inerte)" if d else "P (purga)\\nmisma composición que R"
    b = f"B = {_n(d['b'])} mol/h\\n(producto)" if d else "B\\n(producto)"
    x = f"\\nX paso = {d['xb']:.0%}" if d else "\\nX paso"
    return (_CAB + _entrada("fresco", AZUL) +
            '  fresco [label="' + f0 + '"];\n'
            '  Mezclador; Reactor [label="Reactor' + x + '"]; Separador; Divisor;\n'
            '  producto [shape=plaintext, style="", label="' + b + '"];\n'
            '  purga [shape=plaintext, style="", fontcolor="' + AMARILLO + '", label="' + p + '"];\n'
            '  fresco -> Mezclador [color="' + AZUL + '"];\n'
            '  Mezclador -> Reactor [label="' + f + '", color="#111827"];\n'
            '  Reactor -> Separador [label="A + B + inerte", color="#111827"];\n'
            '  Separador -> producto [color="#111827"];\n'
            '  Separador -> Divisor [label="gas: A + inerte", color="#111827"];\n'
            '  Divisor -> purga [color="' + AMARILLO + '"];\n'
            '  Divisor -> Mezclador [label="' + r + '", color="' + ROJO + '", constraint=false];\n}\n')


def dot_galletas(d=None):
    if d:
        f0 = f"F0 = {_n(d['f0'])} kg/h"
        m = f"M = {_n(d['m'])} kg/h"
        rec = f"Recortes = {_n(d['m'] - d['f0'])} kg/h\\n({d['rc']:.0%} de M)"
        vapor = f"Agua perdida = {_n(d['f0'] * d['h'])} kg/h\\n({d['h']:.0%})"
        hor = f"Horneado = {_n(d['horneado'])} kg/h"
        rech = f"Rechazo = {_n(d['horneado'] * d['q'])} kg/h\\n({d['q']:.0%})"
        bue = f"Producto bueno\\n{_n(d['bueno'])} kg/h"
        al_h = f"{_n(d['f0'])} kg/h"
    else:
        f0, m = "F0 (fresco)", "M"
        rec = "Recortes = r · M"
        vapor = "Agua perdida = h · F0"
        hor = "Horneado = F0 (1 − h)"
        rech = "Rechazo = q · horneado"
        bue = "Producto bueno\\nF0 (1 − h)(1 − q)"
        al_h = "F0\\n(M − recortes)"
    return (_CAB + _entrada("fresco", AZUL) +
            '  fresco [label="' + f0 + '"];\n'
            '  Mezclado; "Corte y moldeo"; Horno; "Inspección\\ny empaque";\n'
            '  vapor [shape=plaintext, style="", fontcolor="' + AMARILLO + '", label="' + vapor + '"];\n'
            '  rechazo [shape=plaintext, style="", fontcolor="' + AMARILLO + '", label="' + rech + '"];\n'
            '  bueno [shape=plaintext, style="", label="' + bue + '"];\n'
            '  fresco -> Mezclado [color="' + AZUL + '"];\n'
            '  Mezclado -> "Corte y moldeo" [label="' + m + '", color="#111827"];\n'
            '  "Corte y moldeo" -> Horno [label="' + al_h + '", color="#111827"];\n'
            '  "Corte y moldeo" -> Mezclado [label="' + rec + '", color="' + ROJO + '", constraint=false];\n'
            '  Horno -> "Inspección\\ny empaque" [label="' + hor + '", color="#111827"];\n'
            '  Horno -> vapor [color="' + AMARILLO + '"];\n'
            '  "Inspección\\ny empaque" -> bueno [color="#111827"];\n'
            '  "Inspección\\ny empaque" -> rechazo [color="' + AMARILLO + '"];\n}\n')


def dot_bypass():
    return (_CAB + _entrada("alim", AZUL) +
            '  alim [label="Alimentación F"];\n'
            '  Divisor; Unidad [label="Unidad\\n(reactor, filtro...)"]; Mezclador;\n'
            '  salida [shape=plaintext, style="", label="Salida"];\n'
            '  alim -> Divisor [color="' + AZUL + '"];\n'
            '  Divisor -> Unidad [label="(1 − f) F", color="#111827"];\n'
            '  Divisor -> Mezclador [label="Bypass f · F\\n(se salta la unidad)", color="' + VERDE + '"];\n'
            '  Unidad -> Mezclador [color="#111827"];\n'
            '  Mezclador -> salida [color="#111827"];\n}\n')


DIAGRAMAS = {
    "R1a": ("Caso 1 · Reciclo", dot_reciclo, "r1"),
    "R1b": ("Caso 2 · Purga", dot_purga, "r1"),
    "R2": ("Línea de galletas (rondas 2 y 3)", dot_galletas, "r2"),
    "BP": ("Bypass (concepto, para el quiz)", dot_bypass, None),
}
