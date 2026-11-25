"""Identidad visual de Galletas S.A. (sin dependencias de Streamlit).

Idea: sala de control de una fábrica de galletas. Chrome neutro (azul grisáceo y chocolate) para que los colores de
las corrientes (azul, rojo, amarillo, verde = fichas de lego) conserven su significado; cada equipo tiene un ícono
de panadería y un color propio; el ranking es una barra por equipo; las fases son estaciones de una cinta.
"""
import html as _h

ICONOS = ["🍪", "🧁", "🍩", "🥐", "🥨", "🎂", "🥧", "🍰"]
COLORES = ["#8A5A2B", "#C2185B", "#6A3FB5", "#0E7C86", "#B23A48", "#3F51B5", "#2E7D5B", "#A23FA8"]
CORTO = {"setup": "Preparación", "entrada": "Quiz de entrada", "R1": "Reciclo y purga", "R2": "Línea de galletas",
         "R3": "Cuello de botella", "R4": "Crisis", "cierre": "Cierre", "fin": "Resultados"}
FICHAS = [("#2563EB", "Fresco"), ("#DC2626", "Reciclo / recortes"), ("#D97706", "Purga y pérdidas"), ("#16A34A", "Bypass")]


def esc(x):
    return _h.escape(str(x), quote=True)


def ico_col(idx):
    return ICONOS[idx % len(ICONOS)], COLORES[idx % len(COLORES)]


CSS_BASE = """
<style>
:root{--tinta:#1F2A37;--choco:#3B2A24;--mant:#F2C14E;--papel:#F4F6F8;--linea:#D9DFE6;--suave:#66727F;}
.stApp{background:var(--papel);color:var(--tinta);}
.stApp,.stApp button,.stApp input,.stApp textarea,[data-testid="stMarkdownContainer"]{font-family:'Segoe UI','Helvetica Neue',system-ui,sans-serif;}
h1,h2,h3,h4,.titulo{font-family:'Bahnschrift','Segoe UI Semibold','Segoe UI',system-ui,sans-serif !important;letter-spacing:-.01em;}
.block-container{padding-top:1.1rem !important;padding-bottom:2rem !important;max-width:1650px;}
footer,#MainMenu{visibility:hidden;}
section[data-testid="stSidebar"]{background:#E9EDF1;}
button[data-baseweb="tab"]{font-family:'Bahnschrift','Segoe UI',sans-serif;font-weight:600;font-size:1rem;}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--choco) !important;}
[data-baseweb="tab-highlight"]{background-color:var(--choco) !important;height:3px !important;}
[data-testid="stBaseButton-primary"],button[kind="primary"],[data-testid="stFormSubmitButton"] button{background:var(--choco) !important;border:1px solid var(--choco) !important;color:#fff !important;border-radius:10px !important;font-weight:600 !important;}
[data-testid="stBaseButton-secondary"],button[kind="secondary"]{background:#fff !important;border:1px solid var(--linea) !important;color:var(--tinta) !important;border-radius:10px !important;font-weight:600 !important;}
[data-testid="stBaseButton-secondary"]:hover,button[kind="secondary"]:hover{border-color:var(--choco) !important;color:var(--choco) !important;}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{border-radius:10px !important;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px !important;background:#fff;border-color:var(--linea) !important;}

.banda{background:var(--choco);color:#fff;border-radius:14px;padding:16px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:5px solid var(--mant);}
.banda .t{font-family:'Bahnschrift','Segoe UI Semibold','Segoe UI',sans-serif;font-size:1.75rem;font-weight:700;line-height:1.1;}
.banda .s{opacity:.8;font-size:.95rem;margin-top:5px;}
.reloj{font-family:'Bahnschrift','Consolas',monospace;font-size:2rem;font-weight:700;background:#fff;color:var(--choco);border-radius:12px;padding:4px 18px;min-width:130px;text-align:center;font-variant-numeric:tabular-nums;}
.reloj.aviso{background:var(--mant);}
.reloj.alerta{background:#C62828;color:#fff;}

.cinta{display:flex;margin:16px 4px 18px;}
.est{flex:1;text-align:center;position:relative;font-size:.8rem;color:var(--suave);}
.est:before{content:"";position:absolute;top:12px;left:-50%;width:100%;height:4px;background:var(--linea);z-index:0;}
.est:first-child:before{display:none;}
.est .pt{width:28px;height:28px;border-radius:50%;background:#fff;border:3px solid var(--linea);margin:0 auto 6px;position:relative;z-index:1;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;}
.est.hecho:before,.est.actual:before{background:var(--choco);}
.est.hecho .pt{background:var(--choco);border-color:var(--choco);color:#fff;}
.est.actual .pt{background:var(--mant);border-color:var(--choco);color:var(--choco);}
.est.actual{color:var(--choco);font-weight:700;}

.eqcab{display:flex;align-items:center;gap:12px;padding:2px 0 10px;border-bottom:4px solid #999;margin-bottom:8px;}
.eqico{width:54px;height:54px;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:1.9rem;flex:none;}
.eqnom{font-family:'Bahnschrift','Segoe UI Semibold',sans-serif;font-size:1.5rem;font-weight:700;flex:1;}
.rol{display:flex;gap:8px;align-items:center;font-size:.95rem;margin:3px 0;}
.rol .r{background:#EEF1F4;border-radius:8px;padding:1px 8px;font-size:.82rem;color:#44505C;white-space:nowrap;}
.chip{display:inline-block;padding:3px 12px;border-radius:999px;font-size:.85rem;font-weight:600;background:#EEF1F4;color:#44505C;}
.chip.ok{background:#DDF3E6;color:#14633F;}
.item{display:flex;gap:8px;align-items:center;padding:6px 10px;border-radius:8px;margin:4px 0;font-size:.92rem;background:#F1F4F7;color:#44505C;}
.item.ok{background:#DDF3E6;color:#14633F;font-weight:600;}

.preg{background:#fff;border:1px solid var(--linea);border-radius:14px;padding:16px 20px;margin-bottom:14px;}
.preg .q{font-family:'Bahnschrift','Segoe UI Semibold',sans-serif;font-size:1.25rem;font-weight:700;margin-bottom:10px;display:flex;gap:12px;align-items:flex-start;}
.preg .n{background:var(--choco);color:#fff;border-radius:10px;min-width:34px;height:34px;display:flex;align-items:center;justify-content:center;flex:none;}
.op{display:flex;gap:12px;align-items:center;padding:8px 12px;border-radius:10px;margin:6px 0;background:#F4F6F8;font-size:1.05rem;}
.op .l{font-weight:800;width:30px;height:30px;border-radius:8px;background:var(--mant);color:var(--choco);display:flex;align-items:center;justify-content:center;flex:none;}
.op.cl{background:#DDF3E6;}

.rk{display:grid;grid-template-columns:52px 250px 1fr 84px;align-items:center;gap:14px;margin:12px 0;}
.rk .pos{font-size:1.8rem;text-align:center;}
.rk .nom{display:flex;align-items:center;gap:10px;font-family:'Bahnschrift','Segoe UI Semibold',sans-serif;font-size:1.25rem;font-weight:700;}
.rk .barra{height:28px;border-radius:14px;background:#E3E8ED;overflow:hidden;}
.rk .barra>div{height:100%;border-radius:14px;}
.rk .pts{font-family:'Bahnschrift','Consolas',monospace;font-size:1.4rem;font-weight:700;text-align:right;}

.hero{background:#fff;border:1px solid var(--linea);border-radius:18px;padding:26px 30px;}
.hero h2{margin:0 0 6px;font-size:2.1rem;}
.hero p{font-size:1.1rem;color:#44505C;margin:0 0 14px;}
.rolcards{display:flex;gap:14px;margin:16px 0;}
.rolcard{flex:1;background:#F4F6F8;border-radius:14px;padding:14px 16px;border:1px solid var(--linea);}
.rolcard .e{font-size:2rem;}
.rolcard b{display:block;font-family:'Bahnschrift','Segoe UI Semibold',sans-serif;font-size:1.15rem;margin:4px 0 2px;}
.rolcard span{font-size:.95rem;color:#44505C;}
.ficha{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--linea);border-radius:999px;padding:5px 14px 5px 8px;margin:4px 8px 4px 0;font-size:.95rem;font-weight:600;}
.ficha i{width:20px;height:20px;border-radius:5px;display:inline-block;}

.alertaband{background:#C62828;color:#fff;border-radius:14px;padding:14px 22px;font-family:'Bahnschrift','Segoe UI Semibold',sans-serif;font-size:1.7rem;font-weight:700;margin:6px 0 14px;}
.espera{background:#fff;border:2px dashed var(--linea);border-radius:18px;padding:60px 20px;text-align:center;font-family:'Bahnschrift','Segoe UI Semibold',sans-serif;font-size:2rem;color:var(--suave);}
.gente{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;}
.mini{background:#fff;border:1px solid var(--linea);border-radius:14px;padding:12px 14px;}
</style>
"""

CSS_TV = "<style>html{font-size:118%;}.block-container{padding-top:.5rem !important;}</style>"


def css(tv=False):
    return CSS_BASE + (CSS_TV if tv else "")


# ------------------------------------------------------- constructores HTML
def banda(titulo, sub="", reloj_txt="", reloj_clase=""):
    r = f'<div class="reloj {esc(reloj_clase)}">{esc(reloj_txt)}</div>' if reloj_txt else ""
    return (f'<div class="banda"><div><div class="t">{esc(titulo)}</div><div class="s">{esc(sub)}</div></div>{r}</div>')


def cinta(fases, actual):
    i_act = fases.index(actual)
    partes = []
    for i, f in enumerate(fases):
        cl = "hecho" if i < i_act else ("actual" if i == i_act else "")
        marca = "✓" if i < i_act else str(i + 1)
        partes.append(f'<div class="est {cl}"><div class="pt">{marca}</div>{esc(CORTO[f])}</div>')
    return '<div class="cinta">' + "".join(partes) + "</div>"


def cab_eq(nombre, idx, chip=""):
    ico, col = ico_col(idx)
    return (f'<div class="eqcab" style="border-color:{col}"><div class="eqico" style="background:{col}24">{ico}</div>'
            f'<div class="eqnom" style="color:{col}">{esc(nombre)}</div>{chip}</div>')


def chip(txt, ok=False):
    return f'<span class="chip{" ok" if ok else ""}">{esc(txt)}</span>'


def roles(miembros, idx_ronda, lista_roles):
    out = []
    for i, m in enumerate(miembros):
        out.append(f'<div class="rol"><span class="r">{esc(lista_roles[(i + idx_ronda) % len(lista_roles)])}</span>{esc(m)}</div>')
    return "".join(out)


def items(lista):
    """lista = [(texto, unidad, ok)]"""
    out = []
    for texto, unidad, ok in lista:
        extra = "" if ok or not unidad else f" [{esc(unidad)}]"
        out.append(f'<div class="item{" ok" if ok else ""}">{"✅" if ok else "⬜"} {esc(texto)}{extra}</div>')
    return "".join(out)


def pregunta(i, q, ops, letra_correcta=None):
    filas = "".join(
        f'<div class="op{" cl" if L == letra_correcta else ""}"><div class="l">{L}</div><div>{esc(op)}</div></div>'
        for L, op in zip("ABCD", ops))
    return f'<div class="preg"><div class="q"><div class="n">{i}</div><div>{esc(q)}</div></div>{filas}</div>'


def ranking(filas, maximo=65.0):
    """filas = [(nombre, idx_color, puntos)] ya ordenadas de mayor a menor."""
    medallas = ["🥇", "🥈", "🥉"]
    out = []
    for pos, (nombre, idx, pts) in enumerate(filas):
        ico, col = ico_col(idx)
        ancho = max(2, min(100, pts / maximo * 100)) if maximo else 2
        out.append(
            f'<div class="rk"><div class="pos">{medallas[pos] if pos < 3 else pos + 1}</div>'
            f'<div class="nom"><span>{ico}</span><span style="color:{col}">{esc(nombre)}</span></div>'
            f'<div class="barra"><div style="width:{ancho:.1f}%;background:{col}"></div></div>'
            f'<div class="pts">{pts:.1f}</div></div>')
    return "".join(out)


def leyenda_fichas():
    return "".join(f'<span class="ficha"><i style="background:{c}"></i>{esc(n)}</span>' for c, n in FICHAS)


def hero(lista_roles):
    detalle = ["Plantea los balances y calcula.", "Mueve las fichas en la maqueta.", "Verifica con un balance no usado."]
    emo = ["🧮", "🧱", "🔍"]
    tarjetas = "".join(
        f'<div class="rolcard"><div class="e">{emo[i]}</div><b>{esc(lista_roles[i].split(" ", 1)[1])}</b>'
        f'<span>{detalle[i]}</span></div>' for i in range(3))
    return (
        '<div class="hero"><h2>Bienvenidos a Galletas S.A.</h2>'
        '<p>Cada equipo gerencia una planta con sus propios datos. Calculen en papel, armen la maqueta con fichas y '
        'demuestren que el balance cierra.</p>'
        f'<div class="rolcards">{tarjetas}</div>'
        '<p>Los roles rotan en cada ronda. Ganan puntos por <b>planteamiento</b>, <b>verificación</b> y <b>resultado</b>.</p>'
        f'<div>{leyenda_fichas()}</div></div>')


def alerta(texto):
    return f'<div class="alertaband">🚨 {esc(texto)}</div>'


def espera(texto):
    return f'<div class="espera">{esc(texto)}</div>'


def equipos_resumen(equipos):
    """equipos = {nombre: [miembros]} -> tarjetas con ícono, color y nombres."""
    out = []
    for idx, (eq, ms) in enumerate(equipos.items()):
        gente = "".join(chip(m) for m in ms)
        out.append(f'<div class="mini">{cab_eq(eq, idx)}<div class="gente">{gente}</div></div>')
    return ('<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin:8px 0 14px">'
            + "".join(out) + "</div>")
