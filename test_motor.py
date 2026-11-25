"""Pruebas rápidas del motor: `python test_motor.py`"""
import time
from motor import *

# 1) Las fórmulas reproducen los casos de las diapositivas
r = random.Random(0)
# Caso 3 de la diapositiva 13-14: F0=100, 2 % inerte, 10 % aceptado, X=40 %
f0, y0, yi, x = 100, 0.02, 0.10, 0.4
a = f0 * (1 - y0); p = f0 * y0 / yi; b = a - p * (1 - yi); rr = (b / x - a) / (1 - yi)
assert abs(p - 20) < 1e-9 and abs(b - 80) < 1e-9 and abs(rr - 113.33) < 0.01, (p, b, rr)

# Línea de galletas de la diapositiva 21-24 (F0=1000, 10 %, 12 %, 5 %, 8 operarios, $3000, D=90 %, cap 1050)
f0, rc, h, q, c, disp, cap = 1000, 0.10, 0.12, 0.05, 3000, 0.90, 1050
m = f0 / (1 - rc); bueno = f0 * (1 - h) * (1 - q)
assert abs(m - 1111.1) < 0.1 and abs(bueno - 836) < 1e-9
assert abs(f0 * c / bueno - 3588.5) < 1
assert abs(disp * (f0 / cap) * (1 - q) * 100 - 81.4) < 0.1
caps = {"Mezclado": 1300, "Corte y moldeo": 1250, "Horno": 1050, "Inspección y empaque": 950}
fm = fmax_por_etapa(caps, rc, h)
assert min(fm, key=fm.get) == "Horno" and abs(fm["Horno"] - 1050) < 1e-9
assert abs(fm["Inspección y empaque"] - 1079.5) < 0.1 and abs(fm["Mezclado"] - 1170) < 0.1

# 2) Los datos son reproducibles, distintos entre equipos y consistentes
for sem in ["galletas2026", "otra"]:
    for k in range(1, 5):
        eq = f"Equipo {k}"
        assert datos_r1(sem, eq) == datos_r1(sem, eq)
        d1 = datos_r1(sem, eq)
        assert d1["rb"] >= 0.15 * d1["f0b"] and d1["b"] > 0
        d3 = datos_r3(sem, eq)
        assert d3["cuello"] in d3["caps"]
        for e in EVENTOS:
            txt, resp, un = datos_evento(sem, eq, e)
            assert resp > 0 and txt
print("Datos por equipo (semilla galletas2026):")
for k in range(1, 5):
    d3 = datos_r3("galletas2026", f"Equipo {k}")
    print(f"  Equipo {k}: F0={d3['f0']}, recortes={d3['rc']:.0%}, rechazo={d3['q']:.0%}, cuello={d3['cuello']}, Fmax={d3['fmax']:.0f}")

# 3) Flujo completo con puntajes
est = estado_inicial(); sem = est["cfg"]["semilla"]
nom = lista_generica(12)
est["equipos"] = {f"Equipo {k + 1}": nom[k * 3:(k + 1) * 3] for k in range(4)}  # reparto fijo para la prueba
eq = "Equipo 1"
for ronda in ["R1", "R2", "R3"]:
    for it in items_ronda(sem, eq, ronda):
        assert registrar_intento(est, eq, it["key"], it["resp"], it["resp"], it["tipo"])
est["manual"][eq] = {f"{r}_{s}": 4 for r in ["R1", "R2", "R3"] for s in ["plan", "ver"]}
for e in ["E1", "E2"]:
    txt, resp, _ = datos_evento(sem, eq, e)
    t = time.time(); est["eventos"][e] = {"t0": t, "resp": {}}
    assert registrar_evento(est, e, eq, resp, resp, t + 5)
p = puntos_equipo(est, eq)
assert abs(p["R1"] - 20) < 1e-9 and abs(p["R2"] - 20) < 1e-9 and abs(p["R3"] - 15) < 1e-9
assert abs(p["R4"] - 10) < 1e-9, p  # primer lugar en ambos eventos: 0,7 + 0,3
# un intento fallido baja el crédito (0,8) y un valor cercano dentro de tolerancia cuenta
est2 = estado_inicial()
it = items_ronda(sem, eq, "R2")[1]
assert not registrar_intento(est2, eq, it["key"], it["resp"] * 1.2, it["resp"])
assert registrar_intento(est2, eq, it["key"], it["resp"] * 1.01, it["resp"])
assert abs(est2["intentos"][eq][it["key"]]["credito"] - 0.8) < 1e-9
# nota individual máxima = 100
est["quiz"]["entrada"]["Estudiante 01"] = {"aciertos": 5, "de": 5}
est["quiz"]["salida"]["Estudiante 01"] = {"aciertos": 5, "de": 5}
est["oral"]["Estudiante 01"] = 5
fila = [f for f in notas_individuales(est) if f["Estudiante"] == "Estudiante 01"][0]
assert abs(fila["Total (/100)"] - 100) < 0.05 and fila["Nota (0-5)"] == 5.0, fila
# 4) Quiz proyectado: la clave de letras coincide con las opciones barajadas
for cual in ["entrada", "salida"]:
    kb = quiz_barajado(cual, sem)
    clave = "".join(c for _, _, c in kb)
    assert len(clave) == 5 and set(clave) <= set("ABCD")
    for (q, lst, c), (_, ops) in zip(kb, BANCO[cual]):
        assert lst["ABCD".index(c)] == ops[0] and sorted(lst) == sorted(ops)
    assert calificar_quiz(cual, sem, clave) == (5, 5)
    assert calificar_quiz(cual, sem, " ".join(clave.lower())) == (5, 5)  # tolera espacios y minúsculas
    assert calificar_quiz(cual, sem, "") == (0, 5)
# 5) Coevaluación digitada por el profesor
est["coeval_prom"]["Estudiante 01"] = 4.0
fila = [f for f in notas_individuales(est) if f["Estudiante"] == "Estudiante 01"][0]
assert abs(fila["Coevaluación (/5)"] - 4.0) < 1e-9 and abs(fila["Total (/100)"] - 99.0) < 0.05, fila
# 6) Número flexible de asistentes y carga de nombres
import io, pandas as pd
for n in [1, 2, 5, 7, 11, 12, 13, 17, 25]:
    eqs = formar_equipos(lista_generica(n), 3, random.Random(n))
    tam = [len(v) for v in eqs.values()]
    assert sum(tam) == n and max(tam) - min(tam) <= 1 and min(tam) >= 1, (n, tam)
assert len(formar_equipos(lista_generica(12), 3)) == 4 and len(formar_equipos(lista_generica(10), 3)) == 3
assert limpiar_nombres(["Nombre", "Ana", "  Luis   Pérez ", "", None, "Ana", float("nan")]) == ["Ana", "Luis Pérez", "Ana (2)"]
buf = io.BytesIO(); pd.DataFrame({"Nombre": ["Ana Ruiz", "Luis Gil", "Eva Mora"], "Código": [1, 2, 3]}).to_excel(buf, index=False)
assert nombres_desde_archivo("lista.xlsx", buf.getvalue()) == ["Ana Ruiz", "Luis Gil", "Eva Mora"]
assert nombres_desde_archivo("lista.csv", "Estudiante;Nota\nAna Ruiz;4\nLuis Gil;3\n".encode()) == ["Ana Ruiz", "Luis Gil"]
assert nombres_desde_archivo("lista.txt", "Ana Ruiz\nLuis Gil\n".encode("utf-8-sig")) == ["Ana Ruiz", "Luis Gil"]
print("OK: todas las pruebas pasan")
