import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

st.title("Optimizador de Rendimiento de Transmisión")

st.header("Función Objetivo")

c1 = st.number_input("Coeficiente de x1 (Coaxial)", value=15.0)
c2 = st.number_input("Coeficiente de x2 (4G)", value=20.0)
c3 = st.number_input("Coeficiente de x3 (5G)", value=100.0)
c4 = st.number_input("Coeficiente de x4 (Satélite)", value=50.0)
c5 = st.number_input("Coeficiente de x5 (Fibra Óptica)", value=1000.0)

st.header("Restricción de Presupuesto")

a11 = st.number_input("Costo x1", value=2.0)
a12 = st.number_input("Costo x2", value=5.0)
a13 = st.number_input("Costo x3", value=15.0)
a14 = st.number_input("Costo x4", value=30.0)
a15 = st.number_input("Costo x5", value=10.0)

presupuesto = st.number_input(
    "Presupuesto máximo ($/h)",
    value=1500.0
)

st.header("Restricción de Capacidad del Switch")

a21 = st.number_input("Capacidad x1", value=20.0)
a22 = st.number_input("Capacidad x2", value=25.0)
a23 = st.number_input("Capacidad x3", value=110.0)
a24 = st.number_input("Capacidad x4", value=60.0)
a25 = st.number_input("Capacidad x5", value=1050.0)

capacidad = st.number_input(
    "Capacidad máxima del switch (Mbps)",
    value=15000.0
)

variables_enteras = st.checkbox(
    "Forzar variables enteras",
    value=False
)

if st.button("Resolver problema"):

    # Función objetivo (negativa porque milp minimiza)
    c = [-c1, -c2, -c3, -c4, -c5]

    # Matriz de restricciones
    A = [
        [a11, a12, a13, a14, a15],
        [a21, a22, a23, a24, a25]
    ]

    bl = [-np.inf, -np.inf]
    bu = [presupuesto, capacidad]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [0, 0, 0, 0, 0],
        [np.inf, np.inf, np.inf, np.inf, np.inf]
    )

    integrality = [1, 1, 1, 1, 1] if variables_enteras else [0, 0, 0, 0, 0]

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integrality
    )

    if res.success:

        st.success("Optimización completada")

        st.metric(
            "Rendimiento máximo",
            f"{-res.fun:.2f} Mbps"
        )

        st.subheader("Solución óptima")

        st.write(f"Coaxial (x1): {res.x[0]:.2f}")
        st.write(f"4G (x2): {res.x[1]:.2f}")
        st.write(f"5G (x3): {res.x[2]:.2f}")
        st.write(f"Satélite (x4): {res.x[3]:.2f}")
        st.write(f"Fibra Óptica (x5): {res.x[4]:.2f}")

        st.subheader("Vector solución")
        st.write(res.x)

    else:
        st.error(f"No se encontró solución: {res.message}")
