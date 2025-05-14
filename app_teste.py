import streamlit as st
import simpy
import random
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Simulação de Fila", page_icon="📈", layout="wide")

st.title("📊 Simulação de Fila de Atendimento com Apoio de Sistema")

st.markdown("""
Este aplicativo simula o fluxo de clientes em um centro de atendimento com base em diferentes cenários:

- **Parâmetros Originais**: Representam a situação atual do centro, com 120 clientes diários, 2 funcionários ativos e tempo médio de atendimento de 10 minutos.
- **Solução Escolhida**: Introduz melhorias via um sistema de apoio, reduzindo o tempo de atendimento para 6 minutos e permitindo que os 3 guichês sejam usados simultaneamente.
- **Simulação Editável**: Permite que você experimente diferentes parâmetros para avaliar o impacto de mudanças no atendimento.

Cada simulação assume **120 clientes por dia**, mantendo a coerência na comparação entre os cenários.
""")

def atendimento_cliente(env, guiches, tempos_fila, tempo_atendimento_medio, tempo_maximo_espera, estatisticas):
    chegada = env.now
    with guiches.request() as request:
        resultado = yield request | env.timeout(tempo_maximo_espera)

        if request in resultado:
            espera = env.now - chegada
            tempos_fila.append((env.now, len(guiches.queue)))
            yield env.timeout(random.expovariate(1.0 / tempo_atendimento_medio))
            estatisticas["atendidos"] += 1
        else:
            tempos_fila.append((env.now, len(guiches.queue)))
            estatisticas["desistentes"] += 1

def gerar_clientes(env, guiches, tempo_atendimento_medio, tempo_maximo_espera, tempos_fila, estatisticas, total_clientes):
    for _ in range(total_clientes):
        yield env.timeout(random.expovariate(120 / 480))
        env.process(atendimento_cliente(env, guiches, tempos_fila, tempo_atendimento_medio, tempo_maximo_espera, estatisticas))

def rodar_simulacao(taxa_chegada, tempo_atendimento_medio, num_guiches, tempo_funcionamento, tempo_maximo_espera, total_clientes):
    env = simpy.Environment()
    guiches = simpy.Resource(env, capacity=num_guiches)
    tempos_fila = []
    estatisticas = {"atendidos": 0, "desistentes": 0}

    env.process(gerar_clientes(env, guiches, tempo_atendimento_medio, tempo_maximo_espera, tempos_fila, estatisticas, total_clientes))
    env.run(until=tempo_funcionamento)
    tempos = [t[0] for t in tempos_fila]
    filas = [t[1] for t in tempos_fila]

    return tempos, filas, estatisticas

def plotar_grafico(tempos, filas, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tempos, y=filas, mode="lines+markers"))
    fig.update_layout(
        xaxis_title="Tempo (minutos)",
        yaxis_title="Número de clientes na fila",
        title=titulo,
        xaxis=dict(range=[0, max(tempos) if tempos else 480]),
        yaxis=dict(range=[0, max(filas) + 5 if filas else 20]),
    )
    st.plotly_chart(fig, use_container_width=True)

# Criação das abas para os três cenários
tabs = st.tabs(["Parâmetros Originais", "Solução Escolhida", "Simulação Customizável"])

# Aba 1: Cenário Original
with tabs[0]:
    st.header("📍 Situação Atual - Parâmetros Originais")
    st.markdown("""
    - **Guichês disponíveis**: 3 (mas apenas 2 usados simultaneamente)
    - **Tempo médio de atendimento**: 10 minutos
    - **Tempo máximo de espera tolerado**: 10 minutos
    - **Total de clientes por dia**: 120
    """)

    tempos, filas, stats = rodar_simulacao(
        taxa_chegada=120 / 480,
        tempo_atendimento_medio=10,
        num_guiches=2,
        tempo_funcionamento=480,
        tempo_maximo_espera=10,
        total_clientes=120
    )
    plotar_grafico(tempos, filas, "Fila ao longo do tempo - Situação Atual")
    st.write(f"Clientes atendidos: {stats['atendidos']} | Clientes desistentes: {stats['desistentes']}")

# Aba 2: Solução com sistema de apoio
with tabs[1]:
    st.header("🚀 Solução com Sistema de Apoio")
    st.markdown("""
    Melhorias com suporte tecnológico:
    - **Redução no tempo de atendimento para 6 minutos**
    - **Utilização de todos os 3 guichês simultaneamente**
    - **Demais parâmetros mantidos para fins comparativos**
    """)

    tempos, filas, stats = rodar_simulacao(
        taxa_chegada=120 / 480,
        tempo_atendimento_medio=6,
        num_guiches=3,
        tempo_funcionamento=480,
        tempo_maximo_espera=10,
        total_clientes=120
    )
    plotar_grafico(tempos, filas, "Fila com Sistema de Apoio")
    st.write(f"Clientes atendidos: {stats['atendidos']} | Clientes desistentes: {stats['desistentes']}")

# Aba 3: Parâmetros personalizáveis
with tabs[2]:
    st.header("⚙️ Simulação com Parâmetros Personalizados")
    st.markdown("""
    Experimente diferentes cenários alterando os parâmetros abaixo.
    O número total de clientes é sempre fixado em **120 por dia**.
    """)

    taxa_chegada = st.slider("Taxa de Chegada (clientes/minuto)", 0.1, 0.5, 120 / 480, 0.01)
    tempo_atendimento_medio = st.slider("Tempo de Atendimento Médio (min)", 5, 60, 10, 1)
    num_guiches = st.slider("Número de Guichês Ativos", 1, 10, 2)
    tempo_funcionamento = st.slider("Duração da Simulação (min)", 60, 480, 480, 10)
    tempo_maximo_espera = st.slider("Tempo Máximo de Espera (min)", 1, 30, 10, 1)

    tempos, filas, stats = rodar_simulacao(
        taxa_chegada=taxa_chegada,
        tempo_atendimento_medio=tempo_atendimento_medio,
        num_guiches=num_guiches,
        tempo_funcionamento=tempo_funcionamento,
        tempo_maximo_espera=tempo_maximo_espera,
        total_clientes=120
    )
    plotar_grafico(tempos, filas, "Fila com Parâmetros Personalizados")
    st.write(f"Clientes atendidos: {stats['atendidos']} | Clientes desistentes: {stats['desistentes']}")
