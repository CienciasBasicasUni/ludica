"""Motor de "Galletas S.A." (Procesos Industriales).

Contiene la lógica pura: datos distintos por equipo, respuestas correctas,
verificación con tolerancia y cálculo de notas. No depende de Streamlit, así
se puede probar con `python test_motor.py`.
"""
import random

# ---------------------------------------------------------------- constantes
FASES = ["setup", "entrada", "R1", "R2", "R3", "R4", "cierre", "fin"]
TITULOS = {
    "setup": "Preparación",
    "entrada": "Ronda 0 · Quiz de entrada",
    "R1": "Ronda 1 · Planta viva (reciclo y purga)",
    "R2": "Ronda 2 · Línea de galletas",
    "R3": "Ronda 3 · Cuello de botella",
    "R4": "Ronda 4 · Crisis relámpago",
    "cierre": "Cierre · Ticket de salida y coevaluación",
    "fin": "Fin de la actividad",
}
DURACION = {"entrada": 20, "R1": 35, "R2": 40, "R3": 25, "R4": 15, "cierre": 20}
ROLES = ["🧮 Ingeniero de balances", "🧱 Jefe de planta (legos)", "🔍 Auditor"]

# Puntos de cada componente (suman 100)
PUNTOS = {"entrada": 15, "salida": 10, "oral": 5, "R1": 20, "R2": 20, "R3": 15, "R4": 10, "coeval": 5}
# Rúbrica de las rondas 1-3: resultado (app) / planteamiento y verificación (profe)
PESO_RESULTADO, PESO_PLAN, PESO_VER = 0.3, 0.5, 0.2

EVENTOS = {
    "E1": "El rechazo en inspección sube",
    "E2": "Suben los recortes",
    "E3": "Se amplía el horno un 10 %",
    "E4": "Se exige menos inerte en el lazo",
}

# Quiz: la primera opción de cada lista es la correcta (la app las baraja).
BANCO = {
    "entrada": [
        ("Sin corriente de reciclo, la conversión por paso y la conversión global son:",
         ["Iguales", "La global siempre es mayor", "La global siempre es menor", "No se pueden comparar"]),
        ("La corriente que devuelve parte de la salida de una unidad a una unidad anterior se llama:",
         ["Reciclo", "Purga", "Bypass", "Divisor"]),
        ("Una purga se necesita cuando:",
         ["Entra un inerte que no sale con el producto y se acumularía en el lazo",
          "La conversión por paso es muy alta",
          "Se quiere ahorrar capacidad del reactor",
          "El producto sale muy diluido"]),
        ("Una corriente que se salta una unidad y se mezcla después con la salida de esa unidad es:",
         ["Bypass", "Reciclo", "Purga", "Alimentación fresca"]),
        ("En estado estacionario y sin reacción, para cada componente:",
         ["Entrada = salida", "Entrada > salida", "Salida = acumulación", "Entrada = 0"]),
    ],
    "salida": [
        ("La purga y el reciclo que salen del mismo divisor tienen:",
         ["La misma composición", "Composición distinta", "El mismo flujo", "Solo inerte"]),
        ("Con alimentación fresca fija de 100 mol/h y sin pérdidas, si la conversión por paso baja de 50 % a 25 %, el reciclo:",
         ["Se triplica", "Se duplica", "Se reduce a la mitad", "No cambia"]),
        ("Para hallar el cuello de botella de una línea con reciclo y pérdidas se compara:",
         ["F_max = capacidad / factor de carga de cada etapa", "La capacidad nominal más baja",
          "La etapa que más opera", "El equipo más caro"]),
        ("TIC-201 se lee como:",
         ["Controlador indicador de temperatura, lazo 201", "Transmisor de corriente, lazo 201",
          "Indicador de conductividad, lazo 201", "Válvula de temperatura, lazo 201"]),
        ("El OEE es el producto de:",
         ["Disponibilidad × desempeño × calidad", "Rendimiento × merma × costo",
          "Capacidad × utilización × α", "Conversión × selectividad × rendimiento"]),
    ],
}


def quiz_barajado(cual, sem):
    """Quiz para proyectar: [(pregunta, opciones barajadas, letra correcta)]. Orden fijo por semilla."""
    out = []
    for i, (q, ops) in enumerate(BANCO[cual]):
        lst = ops[:]
        random.Random(f"{sem}|{cual}|{i}").shuffle(lst)
        out.append((q, lst, "ABCD"[lst.index(ops[0])]))
    return out


def calificar_quiz(cual, sem, respuestas):
    """`respuestas` es un texto como 'ABDCA'. Devuelve (aciertos, total)."""
    clave = [c for _, _, c in quiz_barajado(cual, sem)]
    resp = [ch for ch in str(respuestas).upper() if ch in "ABCD"]
    return sum(1 for a, b in zip(resp, clave) if a == b), len(clave)


def lista_generica(n):
    return [f"Estudiante {i:02d}" for i in range(1, int(n) + 1)]


def limpiar_nombres(valores):
    """Quita vacíos, encabezados típicos y repetidos (los repetidos reciben ' (2)', ' (3)'...)."""
    out, vistos = [], {}
    cab = {"nombre", "nombres", "estudiante", "estudiantes", "name", "names", "alumno", "alumnos"}
    for i, v in enumerate(valores):
        if v is None or (isinstance(v, float) and v != v):
            continue
        t = " ".join(str(v).split())
        if not t or t.lower() == "nan" or (i == 0 and t.lower() in cab):
            continue
        vistos[t] = vistos.get(t, 0) + 1
        out.append(t if vistos[t] == 1 else f"{t} ({vistos[t]})")
    return out


def nombres_desde_archivo(nombre_archivo, contenido):
    """Lee nombres de un .xlsx/.xls, .csv o .txt (primera columna / una línea por nombre)."""
    import io
    import pandas as pd
    ext = nombre_archivo.lower().rsplit(".", 1)[-1]
    if ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(contenido), header=None)
        return limpiar_nombres(df.iloc[:, 0].tolist())
    texto = contenido.decode("utf-8-sig", errors="replace")
    if ext == "csv":
        df = pd.read_csv(io.StringIO(texto), header=None, sep=None, engine="python")
        return limpiar_nombres(df.iloc[:, 0].tolist())
    return limpiar_nombres(texto.splitlines())


def formar_equipos(nombres, tam=3, azar=None):
    """Reparte al azar en equipos de tamaño parecido a `tam` (difieren como máximo en 1)."""
    nombres = list(nombres)
    if not nombres:
        return {}
    (azar or random).shuffle(nombres)
    n_eq = max(1, min(len(nombres), int(len(nombres) / max(tam, 1) + 0.5)))
    return {f"Equipo {k + 1}": nombres[k::n_eq] for k in range(n_eq)}


def estado_inicial():
    nombres = lista_generica(12)
    equipos = formar_equipos(nombres, 3, random.Random(1))
    return {
        "lista": [{"Estudiante": n, "Presente": True} for n in nombres],
        "cfg": {"semilla": "galletas2026", "fase": "setup",
                "fin_fase": None, "evento_activo": None},
        "equipos": equipos,
        "quiz": {"entrada": {}, "salida": {}},   # estudiante -> {aciertos, de}
        "quiz_raw": {"entrada": {}, "salida": {}},  # estudiante -> "ABDCA" (lo digita el profesor)
        "intentos": {},     # equipo -> clave_item -> {fallos, ok, credito}
        "manual": {},       # equipo -> {R1_plan, R1_ver, R2_plan, ...} (0-4)
        "eventos": {},      # eid -> {t0, resp: {equipo: {fallos, ok, t}}}
        "oral": {},         # estudiante -> 0-5
        "coeval_prom": {},  # estudiante -> promedio 1-5 de las hojas de coevaluación
    }


# --------------------------------------------------------- datos por equipo
def datos_r1(sem, eq):
    r = random.Random(f"{sem}|{eq}|R1")
    f0a = r.choice([100, 150, 200, 250, 300])
    xa = r.choice([0.25, 0.4, 0.5, 0.8])
    fa = f0a / xa
    ra = fa - f0a
    while True:
        f0b = r.choice([100, 200])
        y0 = r.choice([0.02, 0.04, 0.05])
        yi = r.choice([0.10, 0.20, 0.25])
        xb = r.choice([0.4, 0.5])
        a_fresco = f0b * (1 - y0)
        p = f0b * y0 / yi
        b = a_fresco - p * (1 - yi)
        rb = (b / xb - a_fresco) / (1 - yi)
        if rb >= 0.15 * f0b:
            break
    return dict(f0a=f0a, xa=xa, fa=fa, ra=ra,
                f0b=f0b, y0=y0, yi=yi, xb=xb, p=p, b=b, rb=rb, xg=b / a_fresco * 100)


def datos_r2(sem, eq):
    r = random.Random(f"{sem}|{eq}|R2")
    f0 = r.choice([1000, 1500, 2000])
    rc = r.choice([0.10, 0.15, 0.20])
    h = r.choice([0.10, 0.12, 0.15])
    q = r.choice([0.04, 0.05, 0.06, 0.08])
    n = r.choice([6, 8, 10])
    c = r.choice([2500, 3000, 3500])
    disp = r.choice([0.85, 0.90, 0.92])
    cap = round(f0 * 1.05 / 10) * 10
    m = f0 / (1 - rc)
    horneado = f0 * (1 - h)
    bueno = horneado * (1 - q)
    return dict(f0=f0, rc=rc, h=h, q=q, n=n, c=c, disp=disp, cap=cap, m=m,
                horneado=horneado, bueno=bueno,
                rend=bueno / f0 * 100, costo=f0 * c / bueno,
                oee=disp * (f0 / cap) * (1 - q) * 100)


def alfas(rc, h):
    return {"Mezclado": 1 / (1 - rc), "Corte y moldeo": 1 / (1 - rc),
            "Horno": 1.0, "Inspección y empaque": 1 - h}


def fmax_por_etapa(caps, rc, h):
    al = alfas(rc, h)
    return {e: caps[e] / al[e] for e in caps}


def datos_r3(sem, eq):
    d = datos_r2(sem, eq)
    r = random.Random(f"{sem}|{eq}|R3")
    al = alfas(d["rc"], d["h"])
    fb = d["cap"]
    cuello = r.choice(["Horno", "Horno", "Mezclado", "Corte y moldeo", "Inspección y empaque"])
    ks = [0.05, 0.08, 0.11, 0.14]
    r.shuffle(ks)
    caps = {}
    for e in al:
        k = 0 if e == cuello else ks.pop()
        caps[e] = round(al[e] * fb * (1 + k) / 10) * 10
    fm = fmax_por_etapa(caps, d["rc"], d["h"])
    cuello_real = min(fm, key=fm.get)
    fmax = fm[cuello_real]
    return dict(d, caps=caps, al=al, fm=fm, cuello=cuello_real, fmax=fmax,
                bueno_max=fmax * (1 - d["h"]) * (1 - d["q"]))


def datos_evento(sem, eq, eid):
    """Devuelve (texto, respuesta, unidad) del evento para ese equipo."""
    d1, d3 = datos_r1(sem, eq), datos_r3(sem, eq)
    if eid == "E1":
        q2 = round(d3["q"] + 0.03, 2)
        return (f"¡Crisis! El rechazo en inspección sube de {d3['q']:.0%} a {q2:.0%}. "
                f"Con {d3['f0']} kg/h de alimentación fresca, ¿cuánto producto bueno sale?",
                d3["f0"] * (1 - d3["h"]) * (1 - q2), "kg/h")
    if eid == "E2":
        r2 = round(d3["rc"] + 0.05, 2)
        return (f"¡Crisis! Los recortes en el corte suben de {d3['rc']:.0%} a {r2:.0%} de lo que entra. "
                f"Con {d3['f0']} kg/h frescos, ¿cuántos kg/h salen del mezclado?",
                d3["f0"] / (1 - r2), "kg/h")
    if eid == "E3":
        caps = dict(d3["caps"])
        caps["Horno"] = caps["Horno"] * 1.10
        fm = fmax_por_etapa(caps, d3["rc"], d3["h"])
        return ("¡Buena noticia! El horno amplía su capacidad un 10 %. "
                "¿Cuál es ahora la alimentación fresca máxima de toda la línea?",
                min(fm.values()), "kg/h")
    if eid == "E4":
        yi2 = round(d1["yi"] / 2, 3)
        return (f"¡Crisis! Calidad exige que el inerte en el lazo baje de {d1['yi']:.0%} a {yi2:.1%} "
                f"(caso de la purga: {d1['f0b']} mol/h frescos con {d1['y0']:.0%} de inerte). "
                f"¿Cuál es el nuevo flujo de purga?",
                d1["f0b"] * d1["y0"] / yi2, "mol/h")
    raise ValueError(eid)


# ----------------------------------------------------------------- ítems
def items_ronda(sem, eq, ronda):
    """Lista de ítems: dict(key, texto, resp, unidad, tipo, pista, opciones?)."""
    if ronda == "R1":
        d = datos_r1(sem, eq)
        return [
            dict(key="r1a_F", texto="Caso 1: flujo que entra al reactor, F", resp=d["fa"], unidad="mol/h", tipo="num",
                 pista="Base: alimentación fresca. F = F0 / X_paso cuando todo el A sin reaccionar regresa."),
            dict(key="r1a_R", texto="Caso 1: flujo de reciclo, R", resp=d["ra"], unidad="mol/h", tipo="num",
                 pista="Balance en el mezclador: F = fresco + R."),
            dict(key="r1a_X", texto="Caso 1: conversión global de A", resp=100.0, unidad="%", tipo="num",
                 pista="¿Cuánto A sale del proceso sin reaccionar?"),
            dict(key="r1b_P", texto="Caso 2: flujo de purga, P", resp=d["p"], unidad="mol/h", tipo="num",
                 pista="Balance global del inerte: lo que entra sale todo por la purga."),
            dict(key="r1b_B", texto="Caso 2: producto B", resp=d["b"], unidad="mol/h", tipo="num",
                 pista="Balance global de A: fresco = A en la purga + B."),
            dict(key="r1b_R", texto="Caso 2: flujo de reciclo, R", resp=d["rb"], unidad="mol/h", tipo="num",
                 pista="Balance de A en el reactor: B = X · (A fresco + A en el reciclo)."),
            dict(key="r1b_X", texto="Caso 2: conversión global de A", resp=d["xg"], unidad="%", tipo="num",
                 pista="X_global = B / A fresco."),
        ]
    if ronda == "R2":
        d = datos_r2(sem, eq)
        return [
            dict(key="r2_M", texto="Masa que sale del mezclado, M", resp=d["m"], unidad="kg/h", tipo="num",
                 pista="M = fresco + recortes, y los recortes son un % de M."),
            dict(key="r2_B", texto="Producto bueno", resp=d["bueno"], unidad="kg/h", tipo="num",
                 pista="Al horno entra solo la alimentación fresca. Luego pérdida de agua y rechazo."),
            dict(key="r2_Y", texto="Rendimiento (bueno / alimentación fresca)", resp=d["rend"], unidad="%", tipo="num",
                 pista="Y = m_bueno / m_fresca."),
            dict(key="r2_C", texto="Costo de materia prima por kg bueno", resp=d["costo"], unidad="COP/kg", tipo="num",
                 pista="(Alimentación fresca × costo por kg) / producto bueno."),
            dict(key="r2_O", texto="OEE", resp=d["oee"], unidad="%", tipo="num",
                 pista="Disponibilidad × desempeño × calidad; desempeño = alimentación / capacidad del horno."),
        ]
    if ronda == "R3":
        d = datos_r3(sem, eq)
        return [
            dict(key="r3_E", texto="Etapa que es el cuello de botella", resp=d["cuello"], unidad="", tipo="opc",
                 opciones=list(d["caps"]),
                 pista="No compares capacidades nominales: divide cada capacidad por su factor de carga α."),
            dict(key="r3_F", texto="Alimentación fresca máxima de la línea, F_max", resp=d["fmax"], unidad="kg/h", tipo="num",
                 pista="F_max = mínimo de (capacidad / α) entre todas las etapas."),
            dict(key="r3_B", texto="Producto bueno con esa alimentación", resp=d["bueno_max"], unidad="kg/h", tipo="num",
                 pista="Aplica la misma cascada de pérdidas (agua y rechazo) a F_max."),
        ]
    raise ValueError(ronda)


def cercano(valor, resp):
    """Tolerancia: 2 % relativo o 0,5 unidades, lo que sea mayor."""
    return abs(valor - resp) <= max(0.02 * abs(resp), 0.5)


def registrar_intento(est, eq, key, valor, resp, tipo="num"):
    """Registra un intento. Devuelve True si es correcto. `est` es el estado (dict)."""
    d = est["intentos"].setdefault(eq, {}).setdefault(key, {"fallos": 0, "ok": False, "credito": 0.0})
    if d["ok"]:
        return True
    ok = (valor == resp) if tipo == "opc" else cercano(valor, resp)
    if ok:
        d["ok"] = True
        d["credito"] = max(0.4, 1 - 0.2 * d["fallos"])
    else:
        d["fallos"] += 1
    return ok


def registrar_evento(est, eid, eq, valor, resp, t_ahora):
    ev = est["eventos"].setdefault(eid, {"t0": t_ahora, "resp": {}})
    d = ev["resp"].setdefault(eq, {"fallos": 0, "ok": False, "t": None})
    if d["ok"]:
        return True
    if cercano(valor, resp):
        d["ok"] = True
        d["t"] = t_ahora - ev["t0"]
        return True
    d["fallos"] += 1
    return False


# ---------------------------------------------------------------- puntajes
def frac_resultado(est, eq, sem, ronda):
    items = items_ronda(sem, eq, ronda)
    di = est["intentos"].get(eq, {})
    return sum(di.get(it["key"], {}).get("credito", 0.0) for it in items) / len(items)


def frac_eventos(est, eq):
    lanzados = [e for e, v in est["eventos"].items() if v.get("t0") is not None]
    if not lanzados:
        return 0.0
    total = 0.0
    for eid in lanzados:
        resp = est["eventos"][eid]["resp"]
        ok = sorted((v["t"], e) for e, v in resp.items() if v["ok"])
        orden = [e for _, e in ok]
        if eq in orden:
            bonus = [0.3, 0.2, 0.1][orden.index(eq)] if orden.index(eq) < 3 else 0.0
            total += min(1.0, max(0.3, 0.7 + bonus - 0.1 * resp[eq]["fallos"]))
    return total / len(lanzados)


def puntos_equipo(est, eq):
    sem = est["cfg"]["semilla"]
    man = est["manual"].get(eq, {})
    out = {}
    for r in ["R1", "R2", "R3"]:
        fr = frac_resultado(est, eq, sem, r)
        plan = man.get(f"{r}_plan", 0) / 4
        ver = man.get(f"{r}_ver", 0) / 4
        out[r] = PUNTOS[r] * (PESO_RESULTADO * fr + PESO_PLAN * plan + PESO_VER * ver)
    out["R4"] = PUNTOS["R4"] * frac_eventos(est, eq)
    out["Total equipo"] = sum(out.values())
    return out


def notas_individuales(est):
    filas = []
    for eq, miembros in est["equipos"].items():
        pe = puntos_equipo(est, eq)["Total equipo"]
        for m in miembros:
            qe = est["quiz"]["entrada"].get(m)
            qs = est["quiz"]["salida"].get(m)
            pe_q = PUNTOS["entrada"] * (qe["aciertos"] / qe["de"]) if qe else 0.0
            ps_q = PUNTOS["salida"] * (qs["aciertos"] / qs["de"]) if qs else 0.0
            oral = PUNTOS["oral"] * est["oral"].get(m, 0) / 5
            prom = est.get("coeval_prom", {}).get(m)
            # Sin promedio digitado se da el beneficio de la duda (puntaje completo).
            coev = PUNTOS["coeval"] * prom / 5 if prom is not None else float(PUNTOS["coeval"])
            total = pe_q + ps_q + oral + pe + coev
            filas.append({
                "Estudiante": m, "Equipo": eq,
                "Quiz entrada (/15)": round(pe_q, 2), "Quiz salida (/10)": round(ps_q, 2),
                "Pregunta oral (/5)": round(oral, 2), "Equipo (/65)": round(pe, 2),
                "Coevaluación (/5)": round(coev, 2), "Coev. promedio (1-5)": prom,
                "Total (/100)": round(total, 2), "Nota (0-5)": round(total / 20, 1),
            })
    return filas
