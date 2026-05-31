import streamlit as st
import pandas as pd
import math

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Simulador Mundial 2026",
    page_icon="⚽",
    layout="wide"
)

# ==========================================
# CLASIFICADOS MUNDIAL 2026
# (actualizar según FIFA)
# ==========================================

WORLD_CUP_2026_TEAMS = [
    "Argentina",
    "Australia",
    "Brasil",
    "Canadá",
    "Colombia",
    "Corea del Sur",
    "Ecuador",
    "España",
    "Estados Unidos",
    "Francia",
    "Inglaterra",
    "Japón",
    "México",
    "Marruecos",
    "Portugal",
    "Uruguay"
]

# ==========================================
# DATOS MOCK
# REEMPLAZAR POR APIs
# ==========================================

TEAM_DATA = {

    "Argentina": {
        "elo": 2145,
        "xg": 2.15,
        "valor": 890,
        "forma": 92,
        "confederacion": "CONMEBOL",
        "h2h": 70
    },

    "Brasil": {
        "elo": 2100,
        "xg": 2.05,
        "valor": 1180,
        "forma": 88,
        "confederacion": "CONMEBOL",
        "h2h": 65
    },

    "Colombia": {
        "elo": 1935,
        "xg": 1.75,
        "valor": 360,
        "forma": 85,
        "confederacion": "CONMEBOL",
        "h2h": 55
    },

    "España": {
        "elo": 2080,
        "xg": 2.00,
        "valor": 1250,
        "forma": 90,
        "confederacion": "UEFA",
        "h2h": 60
    },

    "Francia": {
        "elo": 2095,
        "xg": 2.10,
        "valor": 1320,
        "forma": 91,
        "confederacion": "UEFA",
        "h2h": 62
    },

    "Inglaterra": {
        "elo": 2050,
        "xg": 1.95,
        "valor": 1400,
        "forma": 87,
        "confederacion": "UEFA",
        "h2h": 58
    },

    "Portugal": {
        "elo": 2010,
        "xg": 1.85,
        "valor": 980,
        "forma": 86,
        "confederacion": "UEFA",
        "h2h": 55
    },

    "Uruguay": {
        "elo": 1980,
        "xg": 1.90,
        "valor": 540,
        "forma": 84,
        "confederacion": "CONMEBOL",
        "h2h": 57
    }
}

# ==========================================
# FUNCIONES
# ==========================================

def probabilidad_poisson(lmbda, goles):
    return (
        math.exp(-lmbda)
        * (lmbda ** goles)
        / math.factorial(goles)
    )


def obtener_datos_equipo(pais):

    default = {
        "elo": 1800,
        "xg": 1.4,
        "valor": 250,
        "forma": 70,
        "confederacion": "UEFA",
        "h2h": 50
    }

    return TEAM_DATA.get(pais, default)


def score_elo(elo):
    return min(10, max(1, elo / 220))


def score_xg(xg):
    return min(10, max(1, xg * 4))


def score_valor(valor):
    return min(10, max(1, valor / 140))


def score_forma(forma):
    return forma / 10


def score_h2h(valor):
    return valor / 10


def score_localia(confederacion):

    bonus = {
        "CONCACAF": 9,
        "CONMEBOL": 7,
        "UEFA": 5,
        "CAF": 4,
        "AFC": 4
    }

    return bonus.get(confederacion, 5)


# ==========================================
# INTERFAZ
# ==========================================

st.title("⚽ Simulador Mundial FIFA 2026")
st.write("Modelo híbrido Elo + xG + Valor + Forma + Localía + Historial")

# ==========================================
# PESOS
# ==========================================

st.sidebar.header("Pesos del Modelo")

peso_elo = st.sidebar.slider("Elo", 0, 100, 30)
peso_xg = st.sidebar.slider("xG", 0, 100, 25)
peso_valor = st.sidebar.slider("Valor Plantel", 0, 100, 20)
peso_forma = st.sidebar.slider("Forma", 0, 100, 15)
peso_localia = st.sidebar.slider("Localía", 0, 100, 5)
peso_h2h = st.sidebar.slider("Historial", 0, 100, 5)

peso_total = (
    peso_elo
    + peso_xg
    + peso_valor
    + peso_forma
    + peso_localia
    + peso_h2h
)

# ==========================================
# SELECCIÓN EQUIPOS
# ==========================================

col1, col2 = st.columns(2)

with col1:

    equipo_a = st.selectbox(
        "País A",
        WORLD_CUP_2026_TEAMS
    )

with col2:

    disponibles = [
        x for x in WORLD_CUP_2026_TEAMS
        if x != equipo_a
    ]

    equipo_b = st.selectbox(
        "País B",
        disponibles
    )

# ==========================================
# CARGA DATOS
# ==========================================

a = obtener_datos_equipo(equipo_a)
b = obtener_datos_equipo(equipo_b)

# ==========================================
# TABLA COMPARATIVA
# ==========================================

st.subheader("Comparación de Variables")

df = pd.DataFrame({

    equipo_a: [
        a["elo"],
        a["xg"],
        a["valor"],
        a["forma"],
        a["h2h"]
    ],

    equipo_b: [
        b["elo"],
        b["xg"],
        b["valor"],
        b["forma"],
        b["h2h"]
    ]

},
index=[
    "Elo",
    "xG",
    "Valor Plantel (€M)",
    "Forma",
    "Historial"
])

st.dataframe(df, use_container_width=True)

# ==========================================
# CÁLCULO FUERZA
# ==========================================

if st.button("Calcular Marcador Probable"):

    fuerza_a = (

        score_elo(a["elo"]) * peso_elo +
        score_xg(a["xg"]) * peso_xg +
        score_valor(a["valor"]) * peso_valor +
        score_forma(a["forma"]) * peso_forma +
        score_localia(a["confederacion"]) * peso_localia +
        score_h2h(a["h2h"]) * peso_h2h

    ) / peso_total

    fuerza_b = (

        score_elo(b["elo"]) * peso_elo +
        score_xg(b["xg"]) * peso_xg +
        score_valor(b["valor"]) * peso_valor +
        score_forma(b["forma"]) * peso_forma +
        score_localia(b["confederacion"]) * peso_localia +
        score_h2h(b["h2h"]) * peso_h2h

    ) / peso_total

    marcador = ""
    prob_max = 0

    for goles_a in range(6):

        for goles_b in range(6):

            prob = (
                probabilidad_poisson(
                    fuerza_a,
                    goles_a
                )
                *
                probabilidad_poisson(
                    fuerza_b,
                    goles_b
                )
            )

            if prob > prob_max:

                prob_max = prob

                marcador = (
                    f"{equipo_a} {goles_a}"
                    f" - "
                    f"{goles_b} {equipo_b}"
                )

    st.success(
        f"Marcador más probable: {marcador}"
    )

    st.info(
        f"Probabilidad: {prob_max*100:.2f}%"
    )

    st.subheader("Indicadores")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Diferencia Elo",
        a["elo"] - b["elo"]
    )

    c2.metric(
        "Diferencia xG",
        round(a["xg"] - b["xg"], 2)
    )

    c3.metric(
        "Valor Plantel (€M)",
        a["valor"] - b["valor"]
    )
