import streamlit as st
import math

# Función matemática
def probabilidad_poisson(lmbda, goles):
    return (math.exp(-lmbda) * (lmbda ** goles)) / math.factorial(goles)

# Interfaz de Usuario en Streamlit
st.title("⚽ Simulador Mundial 2026")
st.write("Calculadora de probabilidad de marcadores exactos (Modelo de Poisson)")

st.sidebar.header("Pesos del Modelo (%)")
peso_elo = st.sidebar.slider("Diferencia Elo", 0, 100, 30) / 100
peso_xg = st.sidebar.slider("Goles Esperados (xG)", 0, 100, 25) / 100
peso_valor = st.sidebar.slider("Valor del Plantel", 0, 100, 25) / 100
peso_forma = st.sidebar.slider("Forma Reciente", 0, 100, 10) / 100
peso_localia = st.sidebar.slider("Localía", 0, 100, 5) / 100
peso_h2h = st.sidebar.slider("Historial (H2H)", 0, 100, 5) / 100

st.subheader("Datos de los Equipos (Escala 1 al 10)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Equipo A**")
    nombre_a = st.text_input("Nombre Eq. A", "Colombia")
    elo_a = st.number_input("Elo A", 1.0, 10.0, 8.5)
    xg_a = st.number_input("xG A", 1.0, 10.0, 7.5)
    valor_a = st.number_input("Valor A", 1.0, 10.0, 7.0)

with col2:
    st.markdown("**Equipo B**")
    nombre_b = st.text_input("Nombre Eq. B", "Australia")
    elo_b = st.number_input("Elo B", 1.0, 10.0, 6.5)
    xg_b = st.number_input("xG B", 1.0, 10.0, 6.0)
    valor_b = st.number_input("Valor B", 1.0, 10.0, 5.0)

if st.button("Calcular Marcador"):
    # Cálculo de fuerzas
    fuerza_a = (elo_a*peso_elo + xg_a*peso_xg + valor_a*peso_valor + 8.0*peso_forma + 5.0*peso_localia + 6.0*peso_h2h) / 3.5
    fuerza_b = (elo_b*peso_elo + xg_b*peso_xg + valor_b*peso_valor + 6.0*peso_forma + 5.0*peso_localia + 4.0*peso_h2h) / 3.5
    
    probabilidad_maxima = 0
    marcador_probable = ""

    for goles_a in range(6):
        for goles_b in range(6):
            prob = probabilidad_poisson(fuerza_a, goles_a) * probabilidad_poisson(fuerza_b, goles_b)
            if prob > probabilidad_maxima:
                probabilidad_maxima = prob
                marcador_probable = f"{nombre_a} {goles_a} - {goles_b} {nombre_b}"

    st.success(f"**Marcador más probable:** {marcador_probable}")
    st.info(f"**Probabilidad Matemática:** {probabilidad_maxima * 100:.2f}%")