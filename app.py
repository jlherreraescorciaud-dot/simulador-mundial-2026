
"""
app_mundial2026_realdata.py

Versión preparada para datos reales.
Actualización recomendada:
- Elo: diaria
- Resultados/Forma: diaria
- Valor plantel: semanal
- H2H: diaria
"""

import streamlit as st
import pandas as pd
import math
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Mundial 2026 Predictor", layout="wide")

# ======== CONFIG ========

CACHE_HOURS = 24

WORLD_CUP_2026_TEAMS = sorted([
"Argentina","Brasil","Colombia","Ecuador","Paraguay","Uruguay",
"Alemania","Austria","Bélgica","Bosnia y Herzegovina","Croacia","España",
"Escocia","Francia","Países Bajos","Noruega","Portugal","República Checa",
"Suecia","Suiza","Turquía","Inglaterra","Argelia","Cabo Verde",
"Costa de Marfil","Egipto","Ghana","Marruecos","RD del Congo",
"Senegal","Sudáfrica","Túnez","Arabia Saudita","Australia","Catar",
"Corea del Sur","Irak","Irán","Japón","Jordania","Uzbekistán",
"Canadá","Curazao","Estados Unidos","Haití","México","Panamá","Nueva Zelanda"
])

# ====================================================
# FUNCIONES PARA CONECTAR FUENTES REALES
# ====================================================

@st.cache_data(ttl=60*60*24)
def get_team_data(team):
    """
    Sustituir aquí por tus fuentes reales.

    Ejemplos recomendados:

    Elo:
        eloratings.net

    Resultados:
        football-data.org
        api-football.com

    Valor:
        Transfermarkt (dataset propio)

    H2H:
        api-football
    """

    # FALLBACK TEMPORAL
    seed = sum(ord(c) for c in team)

    return {
        "elo": 1700 + (seed % 500),
        "forma": 60 + (seed % 40),
        "gf": 8 + (seed % 18),
        "gc": 4 + (seed % 12),
        "valor": 100 + (seed % 1200),
        "h2h": 40 + (seed % 40)
    }

def poisson(lmbda, goals):
    return (math.exp(-lmbda) * (lmbda ** goals)) / math.factorial(goals)

def lambda_from_strength(x):
    return 0.6 + (x / 10.0) * 2.2

def score(data):

    elo = min(10, data["elo"] / 220)
    forma = data["forma"] / 10
    goles = min(10, (data["gf"] / max(1, data["gc"])) * 2)
    valor = min(10, data["valor"] / 140)

    return (
        elo * 0.40 +
        forma * 0.30 +
        goles * 0.20 +
        valor * 0.10
    )

# ====================================================

st.title("⚽ Predictor Mundial 2026")

c1, c2 = st.columns(2)

with c1:
    team_a = st.selectbox("Selección A", WORLD_CUP_2026_TEAMS)

with c2:
    team_b = st.selectbox(
        "Selección B",
        [x for x in WORLD_CUP_2026_TEAMS if x != team_a]
    )

a = get_team_data(team_a)
b = get_team_data(team_b)

st.subheader("Datos utilizados")

st.dataframe(
    pd.DataFrame({
        team_a: a,
        team_b: b
    })
)

if st.button("Calcular Pronóstico"):

    sa = score(a)
    sb = score(b)

    la = lambda_from_strength(sa)
    lb = lambda_from_strength(sb)

    p_win_a = 0
    p_draw = 0
    p_win_b = 0

    over25 = 0
    btts = 0

    rows = []

    for ga in range(8):
        for gb in range(8):

            p = poisson(la, ga) * poisson(lb, gb)

            rows.append([f"{ga}-{gb}", p])

            if ga > gb:
                p_win_a += p
            elif ga == gb:
                p_draw += p
            else:
                p_win_b += p

            if ga + gb > 2:
                over25 += p

            if ga > 0 and gb > 0:
                btts += p

    top10 = (
        pd.DataFrame(rows, columns=["Marcador","Prob"])
        .sort_values("Prob", ascending=False)
        .head(10)
    )

    top10["Prob"] = (top10["Prob"] * 100).round(2)

    x1,x2,x3 = st.columns(3)

    x1.metric(f"Gana {team_a}", f"{p_win_a*100:.1f}%")
    x2.metric("Empate", f"{p_draw*100:.1f}%")
    x3.metric(f"Gana {team_b}", f"{p_win_b*100:.1f}%")

    st.subheader("Top 10 Marcadores")
    st.dataframe(top10, use_container_width=True)

    y1,y2 = st.columns(2)

    y1.metric("Over 2.5", f"{over25*100:.1f}%")
    y2.metric("BTTS Sí", f"{btts*100:.1f}%")

    st.caption(
        "Recomendación: programar una actualización automática diaria. "
        "Valor de plantel puede actualizarse semanalmente."
    )
