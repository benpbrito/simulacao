import streamlit as st
import simpy
import random
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Simulação de Fila", page_icon="📈", layout="wide")

custom_css = """
<style>
h1, h2, h3 {
    color: #2E86C1;
}
.stSlider > div {
    background: #f0f2f6;
    padding: 8px;
    border-radius: 10px;
}
.stButton > button {
    background-color: #2E86C1;
    color: white;
    font-weight: bold;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def atendimento_cliente(env, guiches, tempos_fila, tempo_atendimento_medio, taxa_desistencia):
    chegada = env.now
    with guiches.request() as request:
        resultado = yield request | env.timeout(random.expovariate(taxa_desistencia))

        if request in resultado:
            espera = env.now - chegada
            tempos_fila.append((env.now, len(guiches.queue)))
            yield env.timeout(random.expovariate(1.0 / tempo_atendimento_medio))
        else:
            tempos_fila.append((env.now, len(guiches.queue)))

def gerar_clientes(env, guiches, taxa_chegada, tempo_atendimento_medio, taxa_desistencia, tempos_fila):
    cliente_id = 0
    while True:
        yield env.timeout(random.expovariate(taxa_chegada))
        cliente_id += 1
        env.process(atendimento_cliente(env, guiches, tempos_fila, tempo_atendimento_medio, taxa_desistencia))

def rodar_simulacao(taxa_chegada, tempo_atendimento_medio, num_guiches, tempo_funcionamento, taxa_desistencia, modo_progressivo=False, placeholder_grafico=None, tempo_real_segundos=0.1):
    env = simpy.Environment()
    guiches = simpy.Resource(env, capacity=num_guiches)
    tempos_fila = []

    env.process(gerar_clientes(env, guiches, taxa_chegada, tempo_atendimento_medio, taxa_desistencia, tempos_fila))

    if modo_progressivo:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines+markers"))
        fig.update_layout(
            xaxis_title="Tempo (minutos)",
            yaxis_title="Número de clientes na fila",
            title="Simulação Progressiva da Fila",
            xaxis=dict(range=[0, tempo_funcionamento]),
            yaxis=dict(range=[0, 20]),
        )

        tempos = []
        filas = []

        if placeholder_grafico:
            placeholder_grafico.plotly_chart(fig)

        last_minute = 0

        while env.now < tempo_funcionamento:
            env.step()

            if env.now - last_minute >= 1:
                last_minute = env.now

                fila_atual = len(guiches.queue)
                tempos.append(env.now)
                filas.append(fila_atual)

                fig.data[0].x = tempos
                fig.data[0].y = filas

                if placeholder_grafico:
                    placeholder_grafico.plotly_chart(fig, use_container_width=True)

                print(f"[DEBUG] Tempo: {env.now:.2f} min | Fila: {fila_atual} clientes")

                time.sleep(tempo_real_segundos)

        return tempos, filas

    else:
        env.run(until=tempo_funcionamento)

        tempos = [t[0] for t in tempos_fila]
        filas = [t[1] for t in tempos_fila]

        return tempos, filas

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

st.title("📈 Simulação de Otimização de Filas")

tab1, tab2, tab3 = st.tabs(["Padrão", "Ideal", "Personalizado"])

taxa_chegada_padrao = 120 / 480
tempo_atendimento_medio_padrao = 10
num_guiches_padrao = 2
tempo_funcionamento_padrao = 480
taxa_desistencia_padrao = 0.15

taxa_chegada_ideal = 100 / 480
tempo_atendimento_medio_ideal = 8
num_guiches_ideal = 3
taxa_desistencia_ideal = 0.05

with tab1:
    st.header("Fila - Cenário Padrão")
    st.markdown("""
    **Descrição:**  
    Neste cenário padrão, a taxa de chegada de clientes é moderada, o número de guichês é limitado (2 guichês) 
    e a taxa de desistência é relativamente alta (15%).  
    Este é um cenário comum para empresas que ainda não otimizaram seu processo de atendimento.
    """)
    tempos, filas = rodar_simulacao(
        taxa_chegada_padrao,
        tempo_atendimento_medio_padrao,
        num_guiches_padrao,
        tempo_funcionamento_padrao,
        taxa_desistencia_padrao,
        modo_progressivo=False
    )
    plotar_grafico(tempos, filas, "Fila - Parâmetros Padrão")

with tab2:
    st.header("Fila - Cenário Ideal")
    st.markdown("""
    **Descrição:**  
    Neste cenário ideal, otimizamos o atendimento reduzindo o tempo médio de atendimento, aumentando o número de guichês 
    e diminuindo drasticamente a taxa de desistência dos clientes.  
    Este é um exemplo de uma operação bem gerida.
    """)
    tempos, filas = rodar_simulacao(
        taxa_chegada_ideal,
        tempo_atendimento_medio_ideal,
        num_guiches_ideal,
        tempo_funcionamento_padrao,
        taxa_desistencia_ideal,
        modo_progressivo=False
    )
    plotar_grafico(tempos, filas, "Fila - Parâmetros Ideais")


with tab3:
    st.header("Fila - Cenário Personalizado")
    placeholder3 = st.empty()

    with st.form(key="form_parametros"):
        taxa_chegada_personalizada = st.slider("Taxa de chegada (clientes/hora)", 5, 30, 15) / 60
        tempo_atendimento_medio_personalizado = st.slider("Tempo médio de atendimento (minutos)", 5, 20, 10)
        num_guiches_personalizado = st.slider("Número de guichês disponíveis", 1, 5, 2)
        taxa_desistencia_personalizada = st.slider("Taxa de desistência (%)", 0, 50, 15) / 100
        tempo_real_segundos = st.slider("Velocidade de Simulação (segundos para 1 minuto)", 0.05, 1.0, 0.1)

        submit_button = st.form_submit_button(label="🎬 Rodar Simulação Personalizada")

    if submit_button:
        rodar_simulacao(
            taxa_chegada_personalizada,
            tempo_atendimento_medio_personalizado,
            num_guiches_personalizado,
            tempo_funcionamento_padrao,
            taxa_desistencia_personalizada,
            modo_progressivo=True,
            placeholder_grafico=placeholder3,
            tempo_real_segundos=tempo_real_segundos
        )

        st.success("✅ Simulação finalizada!")
