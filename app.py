import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Mundial 2026 Predictor de Jean y José Luis",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Mundial 2026 - Predictor de Marcadores de Jean y José Luis")

# =====================================================
# CARGA CSV
# =====================================================

@st.cache_data
def cargar_datos():
    return pd.read_csv(
        "mundial2026_top3_marcadores.csv"
    )

df = cargar_datos()

# =====================================================
# SELECTORES
# =====================================================

equipos = sorted(df["seleccion"].unique())

col1, col2 = st.columns(2)

with col1:
    local = st.selectbox(
        "Equipo Local",
        equipos
    )

with col2:
    visitante = st.selectbox(
        "Equipo Visitante",
        equipos,
        index=1
    )

# =====================================================
# FUNCIONES
# =====================================================

def obtener_equipo(nombre):

    return df[
        df["seleccion"] == nombre
    ].iloc[0]


def expected_goals(eq_local, eq_visitante):

    lambda_local = (
        0.65
        + (eq_local["ataque_rating"] / 100)
        + (
            (100 - eq_visitante["defensa_rating"])
            / 100
        )
    )

    lambda_visitante = (
        0.65
        + (eq_visitante["ataque_rating"] / 100)
        + (
            (100 - eq_local["defensa_rating"])
            / 100
        )
    )

    lambda_local *= (
        1
        + eq_local["ventaja_continental"] * 0.08
    )

    lambda_local *= (
        1
        - eq_local["fatiga_score"] * 0.05
    )

    lambda_visitante *= (
        1
        - eq_visitante["fatiga_score"] * 0.05
    )

    lambda_local = max(0.30, lambda_local)
    lambda_visitante = max(0.30, lambda_visitante)

    return (
        lambda_local,
        lambda_visitante
    )

def generar_matriz(
    lambda_local,
    lambda_visitante
):

    matriz = np.zeros((7,7))

    for i in range(7):

        for j in range(7):

            p_home = poisson.pmf(
                i,
                lambda_local
            )

            p_away = poisson.pmf(
                j,
                lambda_visitante
            )

            tau = dixon_coles_correction(
                i,
                j,
                lambda_local,
                lambda_visitante,
                rho=-0.08
            )

            matriz[i,j] = (
                p_home
                *
                p_away
                *
                tau
            )

    matriz = matriz / matriz.sum()

    return matriz



def probabilidades_1x2(matriz):

    local = 0
    empate = 0
    visitante = 0

    filas, columnas = matriz.shape

    for i in range(filas):

        for j in range(columnas):

            if i > j:
                local += matriz[i, j]

            elif i == j:
                empate += matriz[i, j]

            else:
                visitante += matriz[i, j]

    return (
        local,
        empate,
        visitante
    )


def top3_scores(matriz):

    resultados = []

    filas, columnas = matriz.shape

    for i in range(filas):

        for j in range(columnas):

            resultados.append(
                (
                    f"{i}-{j}",
                    matriz[i, j]
                )
            )

    resultados.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return resultados[:3]


def over25(matriz):

    prob = 0

    filas, columnas = matriz.shape

    for i in range(filas):

        for j in range(columnas):

            if (i + j) > 2:

                prob += matriz[i, j]

    return prob

def dixon_coles_correction(
    home_goals,
    away_goals,
    lambda_home,
    lambda_away,
    rho=-0.08
):

    if home_goals == 0 and away_goals == 0:
        return 1 - (lambda_home * lambda_away * rho)

    elif home_goals == 0 and away_goals == 1:
        return 1 + (lambda_home * rho)

    elif home_goals == 1 and away_goals == 0:
        return 1 + (lambda_away * rho)

    elif home_goals == 1 and away_goals == 1:
        return 1 - rho

    return 1

def ambos_marcan(matriz):

    prob = 0

    filas, columnas = matriz.shape

    for i in range(1, filas):

        for j in range(1, columnas):

            prob += matriz[i, j]

    return prob
def confianza(top3):

    p = top3[0][1]

    if p > 0.16:
        return "★★★★★"

    elif p > 0.13:
        return "★★★★☆"

    elif p > 0.10:
        return "★★★☆☆"

    elif p > 0.08:
        return "★★☆☆☆"

    return "★☆☆☆☆"

# =====================================================
# BOTÓN
# =====================================================

if st.button("Generar Predicción"):

    if local == visitante:

        st.warning(
            "Selecciona equipos distintos."
        )

        st.stop()

    eq_local = obtener_equipo(local)
    eq_visitante = obtener_equipo(
        visitante
    )

    lambda_local, lambda_visitante = (
        expected_goals(
            eq_local,
            eq_visitante
        )
    )

    matriz = generar_matriz(
        lambda_local,
        lambda_visitante
    )

    p_local, p_empate, p_visitante = (
        probabilidades_1x2(matriz)
    )

    top3 = top3_scores(matriz)

    st.subheader("Probabilidades")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Victoria Local",
        f"{p_local*100:.1f}%"
    )

    c2.metric(
        "Empate",
        f"{p_empate*100:.1f}%"
    )

    c3.metric(
        "Victoria Visitante",
        f"{p_visitante*100:.1f}%"
    )

    st.divider()

    st.subheader(
        "🏆 Top 3 Marcadores"
    )
    st.subheader("Probabilidades")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Victoria Local",
        f"{p_local*100:.1f}%"
    )

    c2.metric(
        "Empate",
        f"{p_empate*100:.1f}%"
    )

    c3.metric(
        "Victoria Visitante",
        f"{p_visitante*100:.1f}%"
    )

    st.divider()

    st.subheader(
        "🏆 Top 3 Marcadores"
    )

    for marcador, prob in top3:

        st.write(
            f"**{marcador}** → "
            f"{prob*100:.2f}%"
        )

    st.metric(
        "Confianza",
        confianza(top3)
    )

    st.divider()

    st.subheader(
        "Marcadores Adicionales"
    )

    st.write(
        f"Over 2.5: "
        f"{over25(matriz)*100:.1f}%"
    )

    st.write(
        f"Ambos marcan: "
        f"{ambos_marcan(matriz)*100:.1f}%"
    )

    st.divider()

    st.subheader(
        "Goles Esperados"
    )

    st.write(
        f"{local}: "
        f"{lambda_local:.2f}"
    )

    st.write(
        f"{visitante}: "
        f"{lambda_visitante:.2f}"
    )
