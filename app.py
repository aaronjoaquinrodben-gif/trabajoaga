import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

st.set_page_config(
    page_title="Optimizador de Rendimiento de Transmisión",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Optimizador de Rendimiento de Transmisión")

st.markdown("""
Modifica los parámetros del modelo y presiona **Resolver Problema**
para encontrar la asignación óptima de canales.
""")

# =========================
# FUNCIÓN OBJETIVO
# =========================

st.header("Función Objetivo (Mbps por canal)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    c1 = st.number_input(
        "Coaxial (x1)",
        value=15,
        step=1,
        format="%d"
    )

with col2:
    c2 = st.number_input(
        "4G (x2)",
        value=20,
        step=1,
        format="%d"
    )

with col3:
    c3 = st.number_input(
        "5G (x3)",
        value=100,
        step=1,
        format="%d"
    )

with col4:
    c4 = st.number_input(
        "Satélite (x4)",
        value=50,
        step=1,
        format="%d"
    )

with col5:
    c5 = st.number_input(
        "Fibra Óptica (x5)",
        value=1000,
        step=1,
        format="%d"
    )

# =========================
# CAPACIDAD DEL SWITCH
# =========================

st.header("Restricción de Capacidad del Switch")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    a21 = st.number_input(
        "Capacidad x1",
        value=20,
        step=1,
        format="%d"
    )

with col2:
    a22 = st.number_input(
        "Capacidad x2",
        value=25,
        step=1,
        format="%d"
    )

with col3:
    a23 = st.number_input(
        "Capacidad x3",
        value=110,
        step=1,
        format="%d"
    )

with col4:
    a24 = st.number_input(
        "Capacidad x4",
        value=60,
        step=1,
        format="%d"
    )

with col5:
    a25 = st.number_input(
        "Capacidad x5",
        value=1050,
        step=1,
        format="%d"
    )

capacidad = st.number_input(
    "Capacidad máxima del Switch (Mbps)",
    value=15000,
    step=1,
    format="%d"
)

# =========================
# RESOLVER
# =========================

if st.button("🚀 Resolver Problema", use_container_width=True):

    # Función objetivo (negativa porque milp minimiza)
    c = [-c1, -c2, -c3, -c4, -c5]

    # Única restricción: capacidad del switch
    A = [
        [a21, a22, a23, a24, a25]
    ]

    bl = [-np.inf]
    bu = [capacidad]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [0, 0, 0, 0, 0],
        [np.inf, np.inf, np.inf, np.inf, np.inf]
    )

    # Variables enteras
    integrality = [1, 1, 1, 1, 1]

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integrality
    )

    if res.success:

        st.success("Optimización completada correctamente")

        st.metric(
            label="Rendimiento Máximo",
            value=f"{int(round(-res.fun))} Mbps"
        )

        st.subheader("Asignación Óptima de Canales")

        resultados = {
            "Cable Coaxial (x1)": int(round(res.x[0])),
            "4G (x2)": int(round(res.x[1])),
            "5G (x3)": int(round(res.x[2])),
            "Satélite (x4)": int(round(res.x[3])),
            "Fibra Óptica (x5)": int(round(res.x[4]))
        }

        st.table(resultados)

        st.subheader("Vector Solución")

        st.write([
            int(round(valor))
            for valor in res.x
        ])

    else:
        st.error(f"No se encontró solución: {res.message}")
