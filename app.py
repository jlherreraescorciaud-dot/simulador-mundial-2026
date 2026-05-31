
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Simulador Mundial 2026", page_icon="⚽", layout="wide")

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

BASE_WEIGHTS = {
    "elo": 35,
    "forma": 25,
    "goles": 20,
    "valor": 10,
    "descanso": 5,
    "localia": 3,
    "h2h": 2
}

CONF = {
    "Argentina":"CONMEBOL","Brasil":"CONMEBOL","Colombia":"CONMEBOL","Ecuador":"CONMEBOL","Paraguay":"CONMEBOL","Uruguay":"CONMEBOL",
    "Alemania":"UEFA","Austria":"UEFA","Bélgica":"UEFA","Bosnia y Herzegovina":"UEFA","Croacia":"UEFA","España":"UEFA",
    "Escocia":"UEFA","Francia":"UEFA","Países Bajos":"UEFA","Noruega":"UEFA","Portugal":"UEFA","República Checa":"UEFA",
    "Suecia":"UEFA","Suiza":"UEFA","Turquía":"UEFA","Inglaterra":"UEFA",
    "Argelia":"CAF","Cabo Verde":"CAF","Costa de Marfil":"CAF","Egipto":"CAF","Ghana":"CAF","Marruecos":"CAF",
    "RD del Congo":"CAF","Senegal":"CAF","Sudáfrica":"CAF","Túnez":"CAF",
    "Arabia Saudita":"AFC","Australia":"AFC","Catar":"AFC","Corea del Sur":"AFC","Irak":"AFC","Irán":"AFC",
    "Japón":"AFC","Jordania":"AFC","Uzbekistán":"AFC",
    "Canadá":"CONCACAF","Curazao":"CONCACAF","Estados Unidos":"CONCACAF","Haití":"CONCACAF","México":"CONCACAF","Panamá":"CONCACAF",
    "Nueva Zelanda":"OFC"
}

def poisson(lmbda, goles):
    return (math.exp(-lmbda) * (lmbda ** goles)) / math.factorial(goles)

def fuerza_a_lambda(score):
    return 0.60 + (score / 10.0) * 2.20

def recalcular_pesos(disponibles):
    activos = {k:v for k,v in BASE_WEIGHTS.items() if disponibles.get(k,False)}
    total = sum(activos.values())
    return {k:v/total for k,v in activos.items()}

def mock_data(team):
    seed = sum(ord(c) for c in team)
    return {
        "elo": 1700 + (seed % 500),
        "forma": 60 + (seed % 40),
        "gf": 8 + (seed % 18),
        "gc": 4 + (seed % 12),
        "valor": 100 + (seed % 1200),
        "descanso": 3 + (seed % 5),
        "h2h": 40 + (seed % 40),
        "conf": CONF.get(team, "UEFA")
    }

def score_team(d, pesos):
    ataque = min(10, max(1, d["gf"]/2))
    defensa = min(10, max(1, 10 - d["gc"]/2))
    goles_score = (ataque + defensa)/2

    localia_map = {"CONCACAF":9,"CONMEBOL":7,"UEFA":5,"CAF":4,"AFC":4,"OFC":3}

    valores = {
        "elo": min(10, d["elo"]/220),
        "forma": d["forma"]/10,
        "goles": goles_score,
        "valor": min(10, d["valor"]/140),
        "descanso": min(10, d["descanso"]*1.5),
        "localia": localia_map.get(d["conf"],5),
        "h2h": d["h2h"]/10
    }

    return sum(valores[k]*pesos[k] for k in pesos)

st.title("⚽ Simulador Mundial 2026")

a_col,b_col = st.columns(2)

with a_col:
    equipo_a = st.selectbox("País A", WORLD_CUP_2026_TEAMS)

with b_col:
    equipo_b = st.selectbox("País B",[x for x in WORLD_CUP_2026_TEAMS if x != equipo_a])

a = mock_data(equipo_a)
b = mock_data(equipo_b)

st.subheader("Disponibilidad de Variables")

disp = {
    "elo": True,
    "forma": True,
    "goles": True,
    "valor": True,
    "descanso": True,
    "localia": True,
    "h2h": False
}

pesos = recalcular_pesos(disp)

st.dataframe(pd.DataFrame({
    "Variable": list(disp.keys()),
    "Disponible": ["✅" if v else "❌" for v in disp.values()],
    "Peso Ajustado (%)": [round(pesos.get(k,0)*100,2) for k in disp.keys()]
}), use_container_width=True)

comp = pd.DataFrame({
    equipo_a:[a["elo"],a["forma"],a["gf"],a["gc"],a["valor"]],
    equipo_b:[b["elo"],b["forma"],b["gf"],b["gc"],b["valor"]]
}, index=["Elo","Forma","GF(10)","GC(10)","Valor"])

st.subheader("Comparación")
st.dataframe(comp, use_container_width=True)

if st.button("Calcular Pronóstico"):
    fuerza_a = score_team(a,pesos)
    fuerza_b = score_team(b,pesos)

    la = fuerza_a_lambda(fuerza_a)
    lb = fuerza_a_lambda(fuerza_b)

    mejor = ""
    prob_max = 0

    for ga in range(8):
        for gb in range(8):
            p = poisson(la,ga) * poisson(lb,gb)
            if p > prob_max:
                prob_max = p
                mejor = f"{equipo_a} {ga} - {gb} {equipo_b}"

    st.success(f"Marcador más probable: {mejor}")
    st.info(f"Probabilidad: {prob_max*100:.2f}%")

    c1,c2,c3 = st.columns(3)
    c1.metric("λ Equipo A", round(la,2))
    c2.metric("λ Equipo B", round(lb,2))
    c3.metric("Dif. Elo", a["elo"]-b["elo"])

    st.warning(
        "Versión preparada para conectar fuentes reales (Elo, resultados, valor de mercado, descanso e historial). "
        "Actualmente utiliza datos simulados para evitar dependencias externas."
    )
