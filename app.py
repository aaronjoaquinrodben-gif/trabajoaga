import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import pandas as pd

st.set_page_config(
    page_title="Optimización de Enlaces Mixtos",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Optimización de Enlaces Mixtos")

st.markdown("""
Modifique los parámetros del sistema y presione **Resolver Problema**
para obtener la asignación óptima de canales.
""")

# =====================================================
# FUNCIÓN OBJETIVO
# =====================================================

st.header("Función Objetivo (Mbps por canal)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    c1 = st.number_input("Coaxial (x1)", value=15, step=1, format="%d")

with col2:
    c2 = st.number_input("4G (x2)", value=20, step=1, format="%d")

with col3:
    c3 = st.number_input("5G (x3)", value=100, step=1, format="%d")

with col4:
    c4 = st.number_input("Satélite (x4)", value=50, step=1, format="%d")

with col5:
    c5 = st.number_input("Fibra Óptica (x5)", value=1000, step=1, format="%d")

# =====================================================
# RESTRICCIÓN DE PRESUPUESTO
# =====================================================

st.header("Restricción de Presupuesto")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    costo_x1 = st.number_input("Costo x1", value=2, step=1, format="%d")

with col2:
    costo_x2 = st.number_input("Costo x2", value=5, step=1, format="%d")

with col3:
    costo_x3 = st.number_input("Costo x3", value=15, step=1, format="%d")

with col4:
    costo_x4 = st.number_input("Costo x4", value=30, step=1, format="%d")

with col5:
    costo_x5 = st.number_input("Costo x5", value=10, step=1, format="%d")

presupuesto = st.number_input(
    "Presupuesto máximo ($/h)",
    value=1500,
    step=1,
    format="%d"
)

# =====================================================
# CAPACIDAD DEL SWITCH
# =====================================================

st.header("Capacidad del Switch")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    cap_x1 = st.number_input("Capacidad x1", value=20, step=1, format="%d")

with col2:
    cap_x2 = st.number_input("Capacidad x2", value=25, step=1, format="%d")

with col3:
    cap_x3 = st.number_input("Capacidad x3", value=110, step=1, format="%d")

with col4:
    cap_x4 = st.number_input("Capacidad x4", value=60, step=1, format="%d")

with col5:
    cap_x5 = st.number_input("Capacidad x5", value=1050, step=1, format="%d")

capacidad_switch = st.number_input(
    "Capacidad máxima del Switch (Mbps)",
    value=15000,
    step=1,
    format="%d"
)

# =====================================================
# RESTRICCIONES OPERATIVAS
# =====================================================

st.header("Restricciones Operativas")

col1, col2 = st.columns(2)

with col1:

    limite_coaxial = st.number_input(
        "Máximo canales Coaxial (x1)",
        value=8,
        step=1,
        format="%d"
    )

    redundancia_movil = st.number_input(
        "Mínimo canales 4G y 5G",
        value=15,
        step=1,
        format="%d"
    )

with col2:

    limite_fibra = st.number_input(
        "Máximo canales Fibra (x5)",
        value=12,
        step=1,
        format="%d"
    )

    minimo_satelite = st.number_input(
        "Mínimo canales Satélite (x4)",
        value=3,
        step=1,
        format="%d"
    )

factor_balanceo = st.number_input(
    "Factor de balanceo (cantidad de 5G para cada 4G",
    value=2,
    step=1,
    format="%d",
    min_value=1
)

# =====================================================
# RESOLVER
# =====================================================

if st.button("🚀 Resolver Problema", use_container_width=True):

    c = [-c1, -c2, -c3, -c4, -c5]

    A = [

        # Presupuesto
        [costo_x1, costo_x2, costo_x3, costo_x4, costo_x5],

        # Capacidad
        [cap_x1, cap_x2, cap_x3, cap_x4, cap_x5],

        # x1 <= límite
        [1, 0, 0, 0, 0],

        # x5 <= límite
        [0, 0, 0, 0, 1],

        # x2 + x3 >= redundancia
        [0, 1, 1, 0, 0],

        # x4 >= mínimo
        [0, 0, 0, 1, 0],

        # x2 - factor*x3 <= 0
        [0, 1, -factor_balanceo, 0, 0]
    ]

    bl = [
        -np.inf,
        -np.inf,
        -np.inf,
        -np.inf,
        redundancia_movil,
        minimo_satelite,
        -np.inf
    ]

    bu = [
        presupuesto,
        capacidad_switch,
        limite_coaxial,
        limite_fibra,
        np.inf,
        np.inf,
        0
    ]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [0, 0, 0, 0, 0],
        [np.inf, np.inf, np.inf, np.inf, np.inf]
    )

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
            "Rendimiento Máximo",
            f"{int(round(-res.fun))} Mbps"
        )

        df = pd.DataFrame({
            "Tecnología": [
                "Cable Coaxial",
                "4G",
                "5G",
                "Satélite",
                "Fibra Óptica"
            ],
            "Canales Asignados": [
                int(round(res.x[0])),
                int(round(res.x[1])),
                int(round(res.x[2])),
                int(round(res.x[3])),
                int(round(res.x[4]))
            ]
        })

        st.subheader("Asignación Óptima de Canales")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.error(f"No se encontró solución: {res.message}")
