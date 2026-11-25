"""Galletas S.A. · Lúdica de Procesos Industriales (balances de masa).

Pensada para UN solo computador (el del profesor) y un televisor:
  - Ventana de CONTROL (en el PC):        http://localhost:8501
  - Ventana de PROYECCIÓN (en el TV):     http://localhost:8501/?modo=tv
Si el TV solo duplica la pantalla, usa el selector "Pantalla" de la barra lateral
para alternar entre Control y Proyección en la misma ventana.

Ejecutar:  streamlit run app.py
"""
import io
import json
import os
import random
import threading
import time

import pandas as pd
import streamlit as st

import diagramas as D
import estilo as S
import motor as M

ARCHIVO = "estado_galletas.json"

st.set_page_config(page_title="Galletas S.A.", page_icon="🍪", layout="wide")


# ------------------------------------------------------ estado compartido
class Almacen:
    """Estado único en memoria (compartido por las ventanas), con respaldo en JSON."""

    def __init__(self):
        self.lock = threading.RLock()
        self.estado = M.estado_inicial()
        if os.path.exists(ARCHIVO):
            try:
                with open(ARCHIVO, encoding="utf-8") as f:
                    guardado = json.load(f)
                self.estado.update(guardado)
            except Exception:
                pass

    def guardar(self):
        with self.lock:
            tmp = ARCHIVO + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.estado, f, ensure_ascii=False, indent=1)
            os.replace(tmp, ARCHIVO)


@st.cache_resource
def get_almacen():
    return Almacen()


A = get_almacen()


def E():
    return A.estado


def SEM():
    return E()["cfg"]["semilla"]


def a_num(s):
    try:
        return float(str(s).strip().replace(",", ".").replace("%", "").replace("$", "").replace(" ", ""))
    except ValueError:
        return None


def h(html):
    st.markdown(html, unsafe_allow_html=True)


def idx_eq(eq):
    claves = list(E()["equipos"])
    return claves.index(eq) if eq in claves else 0


def nombre_eq(eq):
    return f"{S.ico_col(idx_eq(eq))[0]} {eq}"


def nombres_todos():
    return [m for eq in E()["equipos"].values() for m in eq]


# ------------------------------------------------ contenidos reutilizables
def enunciado(ronda, eq):
    sem = SEM()
    if ronda == "R1":
        d = M.datos_r1(sem, eq)
        st.markdown(
            f"**Caso 1 · Reciclo.** A → B. Entran **{d['f0a']} mol/h** de A puro (fresco); conversión por paso "
            f"**{d['xa']:.0%}**. El separador entrega todo el B y devuelve todo el A sin reaccionar al mezclador.\n\n"
            f"**Caso 2 · Purga.** A → B en gas. Fresco: **{d['f0b']} mol/h** con **{d['y0']:.0%}** de inerte. "
            f"Conversión por paso **{d['xb']:.0%}**. El separador retira todo el B; el gas restante pasa a un divisor "
            f"(purga + reciclo). Se acepta **{d['yi']:.0%}** de inerte en esa corriente.")
        st.caption("🧱 1 ficha = 10 mol/h · azul fresco · rojo reciclo · amarillo purga · verde bypass")
    elif ronda == "R2":
        d = M.datos_r2(sem, eq)
        st.markdown(
            f"Mezclado → corte y moldeo → horno → inspección. Fresco **{d['f0']} kg/h**. Recortes "
            f"(**{d['rc']:.0%}** de lo que entra al corte) regresan al mezclado. El horno pierde **{d['h']:.0%}** de "
            f"agua. Inspección rechaza **{d['q']:.0%}** de lo horneado. **{d['n']} operarios**, materia prima "
            f"**${d['c']:,} COP/kg**, disponibilidad **{d['disp']:.0%}**, horno de **{d['cap']} kg/h** "
            f"(desempeño = alimentación / capacidad).".replace(",", "."))
        st.caption(f"🧱 1 ficha = {d['f0'] / 20:.0f} kg/h (el fresco son 20 fichas)")
    elif ronda == "R3":
        d = M.datos_r3(sem, eq)
        st.markdown(f"Misma línea (recortes **{d['rc']:.0%}**, agua **{d['h']:.0%}**, rechazo **{d['q']:.0%}**). "
                    "Capacidad de cada etapa en kg/h de lo que le llega:")
        st.dataframe(pd.DataFrame({"Etapa": list(d["caps"]), "kg/h": list(d["caps"].values())}),
                     hide_index=True, use_container_width=True)
        st.caption("🧱 Limiten cada estación de la maqueta a su capacidad antes de probar.")


def estado_items(eq, ronda):
    di = E()["intentos"].get(eq, {})
    lista = [(it["texto"], it["unidad"], bool(di.get(it["key"], {}).get("ok"))) for it in M.items_ronda(SEM(), eq, ronda)]
    h(S.items(lista))


# ------------------------------------------------------------ PROYECCIÓN
def reloj_partes():
    fin = E()["cfg"]["fin_fase"]
    if not fin:
        return "", ""
    resto = int(fin - time.time())
    r = max(resto, 0)
    clase = "alerta" if resto <= 0 else ("aviso" if resto <= 120 else "")
    return f"{r // 60:02d}:{r % 60:02d}", clase


def encabezado(sub):
    cfg = E()["cfg"]
    txt, clase = reloj_partes()
    h(S.banda(M.TITULOS[cfg["fase"]], sub, txt, clase))
    h(S.cinta(M.FASES, cfg["fase"]))


def tv_quiz(cual):
    st.caption("Respondan en su hoja con las letras (A, B, C o D), sin ayuda. Una sola respuesta por pregunta.")
    preguntas = M.quiz_barajado(cual, SEM())
    cols = st.columns(2)
    for i, (q, ops, _) in enumerate(preguntas):
        with cols[0 if i < 3 else 1]:
            h(S.pregunta(i + 1, q, ops))


def filas_equipos(equipos, n=4):
    items = list(equipos.items())
    return [items[i:i + n] for i in range(0, len(items), n)]


def tv_ronda(ronda):
    idx_ronda = ["R1", "R2", "R3"].index(ronda)
    for fila in filas_equipos(E()["equipos"]):
        cols = st.columns(len(fila))
        for col, (eq, miembros) in zip(cols, fila):
            with col:
                with st.container(border=True):
                    h(S.cab_eq(eq, idx_eq(eq)) + S.roles(miembros, idx_ronda, M.ROLES))
                    enunciado(ronda, eq)
                    estado_items(eq, ronda)


def tv_crisis():
    cfg = E()["cfg"]
    eid = cfg["evento_activo"]
    if not eid:
        h(S.espera("Preparen calculadoras y maqueta..."))
        return
    h(S.alerta(M.EVENTOS[eid]))
    resp = E()["eventos"].get(eid, {}).get("resp", {})
    for fila in filas_equipos(E()["equipos"]):
        cols = st.columns(len(fila))
        for col, (eq, _) in zip(cols, fila):
            with col:
                with st.container(border=True):
                    d = resp.get(eq, {})
                    chip = S.chip(f"✅ {d['t']:.0f} s", True) if d.get("ok") else S.chip("⏳ calculando")
                    h(S.cab_eq(eq, idx_eq(eq), chip))
                    texto, _, _ = M.datos_evento(SEM(), eq, eid)
                    st.markdown(texto)


def tv_diagramas(ronda):
    st.markdown("### Diagrama de referencia · corrijan el suyo")
    if ronda == "R1":
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Caso 1 · Reciclo**")
            st.graphviz_chart(D.dot_reciclo(), use_container_width=True)
        with c2:
            st.markdown("**Caso 2 · Purga**")
            st.graphviz_chart(D.dot_purga(), use_container_width=True)
    else:
        st.graphviz_chart(D.dot_galletas(), use_container_width=True)
    h(f"<div>{S.leyenda_fichas()}</div>")


def tv_ranking():
    df = tabla_equipos()
    filas = [(r["Equipo"], idx_eq(r["Equipo"]), float(r["Total equipo"])) for _, r in df.iterrows()]
    h(S.ranking(filas, 65.0))


@st.fragment(run_every=3)
def pantalla_tv():
    cfg = E()["cfg"]
    f = cfg["fase"]
    encabezado("🍪 Galletas S.A. · Balances de masa")
    if f == "setup":
        h(S.hero(M.ROLES))
        h(S.equipos_resumen(E()["equipos"]))
    elif f == "entrada":
        tv_quiz("entrada")
    elif f in ("R1", "R2", "R3"):
        if cfg.get("mostrar_diagrama"):
            tv_diagramas(f)
        else:
            tv_ronda(f)
    elif f == "R4":
        tv_crisis()
    elif f == "cierre":
        tv_quiz("salida")
        st.info("Cuando terminen: coevaluación en papel (1–5 a cada compañero) y entrega al profesor.")
    else:
        st.markdown("## 🏆 Resultados por equipo")
        tv_ranking()
    if f in ("R1", "R2", "R3", "R4"):
        st.markdown("### Marcador")
        tv_ranking()


# ----------------------------------------------------------- CONTROL
def tabla_equipos(icons=False):
    filas = []
    for eq in E()["equipos"]:
        p = M.puntos_equipo(E(), eq)
        filas.append({"Equipo": eq, **{k: round(v, 1) for k, v in p.items()}})
    df = pd.DataFrame(filas).sort_values("Total equipo", ascending=False)
    if icons:
        df["Equipo"] = df["Equipo"].map(nombre_eq)
    return df


@st.fragment(run_every=2)
def cabecera_control():
    encabezado("Panel del profesor")


def panel_control():
    cfg = E()["cfg"]
    cols = st.columns(4)
    for i, f in enumerate(M.FASES):
        actual = cfg["fase"] == f
        if cols[i % 4].button(("● " if actual else "") + M.TITULOS[f], key=f"fase_{f}", use_container_width=True,
                              type="primary" if actual else "secondary"):
            with A.lock:
                cfg["fase"] = f
                cfg["fin_fase"] = time.time() + M.DURACION[f] * 60 if f in M.DURACION else None
                cfg["evento_activo"] = None
                cfg["mostrar_diagrama"] = False
                A.guardar()
            st.rerun()
    c1, c2, _ = st.columns(3)
    if c1.button("➕ 5 min"):
        with A.lock:
            cfg["fin_fase"] = (cfg["fin_fase"] or time.time()) + 300
            A.guardar()
        st.rerun()
    if c2.button("⏹ Quitar reloj"):
        with A.lock:
            cfg["fin_fase"] = None
            A.guardar()
        st.rerun()
    st.caption("Duración por defecto (min): " + ", ".join(f"{k}={v}" for k, v in M.DURACION.items()))
    st.divider()
    st.markdown("#### Marcador")
    st.dataframe(tabla_equipos(icons=True), hide_index=True, use_container_width=True)


def panel_ventanilla():
    est = E()
    st.write("Un equipo viene al PC (o tú digitas lo que te dicen) y valida sus resultados.")
    eq = st.selectbox("Equipo que entrega", list(est["equipos"]), key="vent_eq", format_func=nombre_eq)
    fase = est["cfg"]["fase"]
    ronda = st.radio("Ronda", ["R1", "R2", "R3"], index=["R1", "R2", "R3"].index(fase) if fase in ("R1", "R2", "R3") else 0,
                     horizontal=True, key="vent_ronda")
    for it in M.items_ronda(SEM(), eq, ronda):
        formulario_item(eq, it)


def formulario_item(eq, it):
    est = E()
    d = est["intentos"].get(eq, {}).get(it["key"], {})
    if d.get("ok"):
        st.success(f"✅ {it['texto']} · crédito {d['credito']:.0%}")
        return
    with st.form(f"f_{eq}_{it['key']}"):
        c1, c2 = st.columns([4, 1])
        if it["tipo"] == "num":
            v = c1.text_input(f"{it['texto']}  [{it['unidad']}]")
        else:
            v = c1.selectbox(it["texto"], it["opciones"], index=None)
        enviar = c2.form_submit_button("Verificar")
    if enviar:
        if it["tipo"] == "num":
            valor = a_num(v)
            if valor is None:
                st.warning("Escribe un número.")
                return
        else:
            valor = v
            if valor is None:
                st.warning("Elige una opción.")
                return
        with A.lock:
            ok = M.registrar_intento(est, eq, it["key"], valor, it["resp"], it["tipo"])
            A.guardar()
        if ok:
            st.rerun()
        n = est["intentos"][eq][it["key"]]["fallos"]
        st.error(f"No coincide (fallo {n}). Pista para el equipo: {it['pista']}")


def panel_crisis():
    est = E()
    cfg = est["cfg"]
    st.write("En la **Ronda 4** lanza una crisis: cada equipo la ve en el TV con sus números. "
             "Cuando un equipo diga su respuesta, digítala aquí **en el orden en que la dan**: el tiempo cuenta desde el lanzamiento.")
    cols = st.columns(4)
    for i, (eid, nombre) in enumerate(M.EVENTOS.items()):
        lanzado = eid in est["eventos"]
        if cols[i].button(f"{'✔ ' if lanzado else ''}{eid} · {nombre}", key=f"ev_{eid}", use_container_width=True):
            with A.lock:
                if not lanzado:
                    est["eventos"][eid] = {"t0": time.time(), "resp": {}}
                cfg["evento_activo"] = eid
                A.guardar()
            st.rerun()
    eid = cfg["evento_activo"]
    st.info(f"Evento activo: **{eid or 'ninguno'}**")
    if eid:
        eq = st.selectbox("Equipo que responde", list(est["equipos"]), key="crisis_eq", format_func=nombre_eq)
        texto, resp, unidad = M.datos_evento(SEM(), eq, eid)
        d = est["eventos"].get(eid, {}).get("resp", {}).get(eq, {})
        if d.get("ok"):
            st.success(f"✅ {eq} resolvió en {d['t']:.0f} s.")
        else:
            with st.form(f"ev_{eid}_{eq}"):
                v = st.text_input(f"Respuesta de {eq} [{unidad}]")
                enviar = st.form_submit_button("Verificar")
            if enviar:
                valor = a_num(v)
                if valor is None:
                    st.warning("Escribe un número.")
                else:
                    with A.lock:
                        ok = M.registrar_evento(est, eid, eq, valor, resp, time.time())
                        A.guardar()
                    if ok:
                        st.rerun()
                    st.error("No coincide (cada fallo resta 0,1).")
        if st.button("Cerrar evento activo"):
            with A.lock:
                cfg["evento_activo"] = None
                A.guardar()
            st.rerun()


def panel_quices():
    est = E()
    cual = st.radio("Quiz", ["entrada", "salida"], horizontal=True, format_func=lambda x: f"Quiz de {x}")
    clave = M.quiz_barajado(cual, SEM())
    st.caption("Clave (solo para ti): " + "  ·  ".join(f"{i + 1}{c}" for i, (_, _, c) in enumerate(clave)))
    with st.expander("👁 Ver las preguntas de este quiz (con la respuesta correcta marcada)"):
        for i, (q, ops, letra) in enumerate(clave, 1):
            st.markdown(f"**{i}. {q}**")
            for L, op in zip("ABCD", ops):
                st.write(f"{'✅' if L == letra else '▫️'} **{L}.** {op}")
    st.caption("Los estudiantes las ven en la ventana de Proyección cuando activas la fase "
               "'Ronda 0 · Quiz de entrada' (o 'Cierre' para el quiz de salida), en la pestaña Control.")
    st.write("Digita las 5 letras de cada hoja (por ejemplo `ABDCA`). La app califica sola.")
    raw = est["quiz_raw"][cual]
    df = pd.DataFrame([{"Estudiante": n, "Respuestas": raw.get(n, "")} for n in nombres_todos()])
    ed = st.data_editor(df, hide_index=True, disabled=["Estudiante"], key=f"ed_quiz_{cual}", use_container_width=True)
    if st.button("💾 Calificar y guardar", key=f"sv_quiz_{cual}"):
        with A.lock:
            for _, r in ed.iterrows():
                txt = str(r["Respuestas"] or "").strip()
                if txt:
                    a, d = M.calificar_quiz(cual, SEM(), txt)
                    est["quiz"][cual][r["Estudiante"]] = {"aciertos": a, "de": d}
                    est["quiz_raw"][cual][r["Estudiante"]] = txt
            A.guardar()
        st.rerun()
    res = [{"Estudiante": n, "Aciertos": f"{est['quiz'][cual][n]['aciertos']}/{est['quiz'][cual][n]['de']}"}
           for n in nombres_todos() if n in est["quiz"][cual]]
    if res:
        st.dataframe(pd.DataFrame(res), hide_index=True)


def panel_calificar():
    est = E()
    st.markdown("#### Planteamiento y verificación por equipo (0–4)")
    st.caption("Planteamiento = diagrama rotulado, base de cálculo, GL = 0 (50 % de la ronda). "
               "Verificación = balance no usado y maqueta que cierra (20 %). El resultado numérico lo califica la app (30 %).")
    cols = [f"{r}_{s}" for r in ["R1", "R2", "R3"] for s in ["plan", "ver"]]
    df = pd.DataFrame([{"Equipo": eq, **{c: est["manual"].get(eq, {}).get(c, 0) for c in cols}} for eq in est["equipos"]])
    ed = st.data_editor(df, hide_index=True, disabled=["Equipo"], key="ed_manual",
                        column_config={c: st.column_config.NumberColumn(min_value=0, max_value=4, step=1) for c in cols})
    st.markdown("#### Individual: pregunta oral (0–5) y coevaluación (promedio 1–5)")
    dfo = pd.DataFrame([{"Estudiante": n, "Oral": est["oral"].get(n, 0),
                         "Coev. promedio": est["coeval_prom"].get(n)} for n in nombres_todos()])
    edo = st.data_editor(dfo, hide_index=True, disabled=["Estudiante"], key="ed_oral",
                         column_config={"Oral": st.column_config.NumberColumn(min_value=0, max_value=5, step=1),
                                        "Coev. promedio": st.column_config.NumberColumn(min_value=1, max_value=5, step=0.1)})
    if st.button("💾 Guardar calificaciones"):
        with A.lock:
            for _, row in ed.iterrows():
                est["manual"][row["Equipo"]] = {c: int(row[c]) for c in cols}
            for _, row in edo.iterrows():
                est["oral"][row["Estudiante"]] = int(row["Oral"])
                if pd.notna(row["Coev. promedio"]):
                    est["coeval_prom"][row["Estudiante"]] = float(row["Coev. promedio"])
                else:
                    est["coeval_prom"].pop(row["Estudiante"], None)
            A.guardar()
        st.success("Guardado.")


def _nueva_version():
    st.session_state["v_tablas"] = st.session_state.get("v_tablas", 0) + 1


def _aplicar_nombres(nombres, tam):
    """Reemplaza la lista de asistentes (todos presentes) y forma equipos al azar."""
    est = E()
    with A.lock:
        est["lista"] = [{"Estudiante": n, "Presente": True} for n in nombres]
        est["equipos"] = M.formar_equipos(nombres, tam)
        A.guardar()
    _nueva_version()
    st.rerun()


def panel_equipos():
    est = E()
    v = st.session_state.get("v_tablas", 0)
    tam = st.session_state.get("tam_equipo", 3)
    presentes = [r["Estudiante"] for r in est["lista"] if r.get("Presente")]
    st.info(f"Ahora hay **{len(presentes)} presentes** en **{len(est['equipos'])} equipos**.")
    h(S.equipos_resumen(est["equipos"]))

    st.markdown("#### 1. ¿Quiénes asistieron?")
    c1, c2 = st.columns(2)
    with c1:
        n = st.number_input("Número de asistentes", 1, 60, max(len(presentes), 1), key=f"n_asist_{v}")
        if st.button("Crear lista genérica (Estudiante 01, 02...)"):
            _aplicar_nombres(M.lista_generica(n), tam)
    with c2:
        archivo = st.file_uploader("…o carga los nombres (.xlsx, .csv o .txt; primera columna)",
                                   type=["xlsx", "xls", "csv", "txt"], key=f"up_{v}")
        pegado = st.text_area("…o pégalos aquí, uno por línea", height=110, key=f"pega_{v}")
        if st.button("Usar estos nombres"):
            try:
                nombres = (M.nombres_desde_archivo(archivo.name, archivo.getvalue())
                           if archivo else M.limpiar_nombres(pegado.splitlines()))
            except Exception as e:
                st.error(f"No pude leer el archivo: {e}")
                nombres = []
            if nombres:
                _aplicar_nombres(nombres, tam)
            else:
                st.warning("No encontré nombres. Carga un archivo o pega una lista.")

    st.markdown("#### 2. Lista del curso (marca quién está presente)")
    st.caption("Puedes cargar toda la lista del curso y desmarcar a los ausentes: los equipos se forman solo con los presentes.")
    df = st.data_editor(pd.DataFrame(est["lista"]), hide_index=True, num_rows="dynamic", key=f"ed_lista_{v}",
                        column_config={"Presente": st.column_config.CheckboxColumn(default=True)},
                        use_container_width=True)
    tam = st.number_input("Tamaño ideal de equipo", 2, 6, 3, key="tam_equipo")
    if st.button("🎲 Guardar lista y formar equipos al azar"):
        filas = [{"Estudiante": " ".join(str(r["Estudiante"]).split()), "Presente": bool(r["Presente"])}
                 for _, r in df.iterrows() if pd.notna(r["Estudiante"]) and str(r["Estudiante"]).strip()]
        pres = [r["Estudiante"] for r in filas if r["Presente"]]
        if not pres:
            st.warning("Marca al menos un presente.")
        elif len(set(pres)) != len(pres):
            st.warning("Hay nombres repetidos entre los presentes: hazlos únicos (por ejemplo, agrega la inicial del apellido).")
        else:
            with A.lock:
                est["lista"] = filas
                est["equipos"] = M.formar_equipos(pres, tam)
                A.guardar()
            _nueva_version()
            st.rerun()

    st.markdown("#### 3. Ajustar equipos a mano (opcional)")
    filas_eq = [{"Estudiante": m, "Equipo": eq} for eq, ms in est["equipos"].items() for m in ms]
    ed = st.data_editor(pd.DataFrame(filas_eq), hide_index=True, key=f"ed_roster_{v}", disabled=["Estudiante"],
                        use_container_width=True)
    if st.button("💾 Guardar equipos"):
        nuevo = {}
        for _, r in ed.dropna().iterrows():
            nuevo.setdefault(str(r["Equipo"]).strip(), []).append(r["Estudiante"])
        with A.lock:
            est["equipos"] = nuevo
            A.guardar()
        _nueva_version()
        st.rerun()
    st.caption("Con equipos de 2 o de 4, los roles se reparten igual (en 4, el auditor se comparte). "
               "Conviene definir los equipos **antes** de empezar: los puntajes quedan ligados al nombre del equipo.")

    st.divider()
    s = st.text_input("Semilla de datos (cambiarla genera otros números)", est["cfg"]["semilla"])
    if st.button("Guardar semilla"):
        with A.lock:
            est["cfg"]["semilla"] = s
            A.guardar()
        st.success("Listo.")
    with st.expander("⚠ Reiniciar toda la actividad"):
        if st.button("Borrar todo y empezar de cero"):
            with A.lock:
                A.estado = M.estado_inicial()
                A.guardar()
            _nueva_version()
            st.rerun()


def panel_diagramas():
    est = E()
    cfg = est["cfg"]
    st.write("Diagramas de referencia: **lo que cada equipo debe dibujar** como planteamiento. "
             "Úsalos para calificar y, al terminar una ronda, proyéctalos en el TV para corregir.")
    st.caption("Colores = fichas de lego: azul fresco · rojo reciclo/recortes · amarillo purga y pérdidas · verde bypass.")
    clave = st.radio("Diagrama", list(D.DIAGRAMAS), format_func=lambda k: D.DIAGRAMAS[k][0], horizontal=True)
    titulo, fn, tipo = D.DIAGRAMAS[clave]
    opciones = ["Símbolos (referencia)"] + (list(est["equipos"]) if tipo else [])
    quien = st.selectbox("Mostrar con…", opciones,
                         format_func=lambda x: x if x.startswith("Símbolos") else nombre_eq(x))
    d = None
    if quien != "Símbolos (referencia)":
        d = M.datos_r1(SEM(), quien) if tipo == "r1" else M.datos_r2(SEM(), quien)
    st.graphviz_chart(fn(d), use_container_width=True)
    st.divider()
    activo = cfg.get("mostrar_diagrama", False)
    st.markdown(f"**TV:** {'🟢 mostrando diagramas de referencia' if activo else '⚪ no se muestran diagramas'}")
    c1, c2 = st.columns(2)
    if c1.button("📺 Proyectar diagramas de la ronda actual", disabled=cfg["fase"] not in ("R1", "R2", "R3")):
        with A.lock:
            cfg["mostrar_diagrama"] = True
            A.guardar()
        st.rerun()
    if c2.button("Ocultar diagramas en el TV"):
        with A.lock:
            cfg["mostrar_diagrama"] = False
            A.guardar()
        st.rerun()
    st.caption("El botón de proyectar solo sirve en las rondas 1 a 3. Al cambiar de fase, el TV vuelve a su vista normal.")


def panel_solucionario():
    est = E()
    st.caption("Datos y respuestas de cada equipo, para revisar las maquetas.")
    for eq in est["equipos"]:
        with st.expander(nombre_eq(eq)):
            for r in ["R1", "R2", "R3"]:
                st.markdown(f"**{M.TITULOS[r]}**")
                for it in M.items_ronda(SEM(), eq, r):
                    resp = it["resp"] if it["tipo"] == "opc" else f"{it['resp']:,.1f} {it['unidad']}"
                    st.write(f"- {it['texto']}: **{resp}**")
            st.markdown("**Crisis**")
            for eid in M.EVENTOS:
                _, rsp, u = M.datos_evento(SEM(), eq, eid)
                st.write(f"- {eid}: **{rsp:,.1f} {u}**")


def panel_notas():
    df = pd.DataFrame(M.notas_individuales(E()))
    vista = df.copy()
    if "Equipo" in vista:
        vista["Equipo"] = vista["Equipo"].map(nombre_eq)
    st.dataframe(vista, hide_index=True, use_container_width=True)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Notas individuales", index=False)
        tabla_equipos().to_excel(w, sheet_name="Equipos", index=False)
        det = [{"Equipo": eq, "Ítem": k, "Fallos": v["fallos"], "Correcto": v["ok"], "Crédito": v["credito"]}
               for eq, d in E()["intentos"].items() for k, v in d.items()]
        pd.DataFrame(det).to_excel(w, sheet_name="Detalle ítems", index=False)
    st.download_button("⬇ Descargar Excel", buf.getvalue(), "notas_galletas_sa.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.caption("Total sobre 100 = quiz entrada 15 + quiz salida 10 + oral 5 + equipo 65 + coevaluación 5. "
               "Nota (0–5) = total / 20. Sin coevaluación digitada se da el puntaje completo.")


def vista_control():
    cabecera_control()
    t = st.tabs(["🎛 Control", "🧾 Ventanilla", "📝 Quices", "🗺 Diagramas", "🚨 Crisis", "✍ Calificar",
                 "👥 Equipos y ajustes", "🔑 Solucionario", "📊 Notas y Excel"])
    with t[0]:
        panel_control()
    with t[1]:
        panel_ventanilla()
    with t[2]:
        panel_quices()
    with t[3]:
        panel_diagramas()
    with t[4]:
        panel_crisis()
    with t[5]:
        panel_calificar()
    with t[6]:
        panel_equipos()
    with t[7]:
        panel_solucionario()
    with t[8]:
        panel_notas()


# ------------------------------------------------------------------ main
es_tv = st.query_params.get("modo") == "tv"
modo = st.sidebar.radio("Pantalla", ["🎛 Control (profesor)", "📺 Proyección (TV)"], index=1 if es_tv else 0)
h(S.css(tv=modo.startswith("📺")))
if modo.startswith("📺"):
    pantalla_tv()
else:
    vista_control()
