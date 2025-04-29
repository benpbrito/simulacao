import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Configurações
RANDOM_SEED = 42
NUM_GUICHE = 2
TEMPO_ATENDIMENTO_MEDIO = 10  # minutos
TAXA_CHEGADA = 120 / (8 * 60)  # 120 clientes em 8 horas (em clientes por minuto)
TEMPO_DESISTENCIA = 25  # minutos (tempo máximo que um cliente espera antes de desistir)
HORAS_FUNCIONAMENTO = 8  # horas
MINUTOS_FUNCIONAMENTO = HORAS_FUNCIONAMENTO * 60

# Variáveis para coleta de dados
tempos_espera = []
clientes_desistiram = 0
clientes_atendidos = 0
eventos_tempo = []  # (tempo, número de clientes no sistema)

# Processo de atendimento
def atendimento_cliente(env, cliente_id, guiches):
    global clientes_desistiram, clientes_atendidos
    chegada = env.now
    with guiches.request() as pedido:
        resultado = yield pedido | env.timeout(TEMPO_DESISTENCIA)
        if pedido in resultado:
            espera = env.now - chegada
            tempos_espera.append(espera)
            clientes_atendidos += 1
            yield env.timeout(random.expovariate(1 / TEMPO_ATENDIMENTO_MEDIO))
        else:
            clientes_desistiram += 1

# Processo de chegada de clientes
def chegada_clientes(env, guiches):
    cliente_id = 0
    while True:
        yield env.timeout(random.expovariate(TAXA_CHEGADA))
        cliente_id += 1
        env.process(atendimento_cliente(env, cliente_id, guiches))
        eventos_tempo.append((env.now, len(guiches.queue)))

# Função principal
def simular():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    guiches = simpy.Resource(env, capacity=NUM_GUICHE)
    env.process(chegada_clientes(env, guiches))
    env.run(until=MINUTOS_FUNCIONAMENTO)

# Executa a simulação
simular()

# Resultados
print(f"Tempo médio de espera: {statistics.mean(tempos_espera):.2f} minutos")
print(f"Clientes atendidos: {clientes_atendidos}")
print(f"Clientes que desistiram: {clientes_desistiram}")

# Plotar gráfico
tempos, filas = zip(*eventos_tempo)
plt.figure(figsize=(10, 5))
plt.plot(tempos, filas, label="Número de clientes na fila")
plt.xlabel("Tempo (minutos)")
plt.ylabel("Tamanho da fila")
plt.title("Tamanho da fila ao longo do tempo")
plt.legend()
plt.grid(True)
plt.show()
import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Configurações
RANDOM_SEED = 42
NUM_GUICHE = 2
TEMPO_ATENDIMENTO_MEDIO = 10  # minutos
TAXA_CHEGADA = 120 / (8 * 60)  # 120 clientes em 8 horas (em clientes por minuto)
TEMPO_DESISTENCIA = 25  # minutos (tempo máximo que um cliente espera antes de desistir)
HORAS_FUNCIONAMENTO = 8  # horas
MINUTOS_FUNCIONAMENTO = HORAS_FUNCIONAMENTO * 60

# Variáveis para coleta de dados
tempos_espera = []
clientes_desistiram = 0
clientes_atendidos = 0
eventos_tempo = []  # (tempo, número de clientes no sistema)

# Processo de atendimento
def atendimento_cliente(env, cliente_id, guiches):
    global clientes_desistiram, clientes_atendidos
    chegada = env.now
    with guiches.request() as pedido:
        resultado = yield pedido | env.timeout(TEMPO_DESISTENCIA)
        if pedido in resultado:
            espera = env.now - chegada
            tempos_espera.append(espera)
            clientes_atendidos += 1
            yield env.timeout(random.expovariate(1 / TEMPO_ATENDIMENTO_MEDIO))
        else:
            clientes_desistiram += 1

# Processo de chegada de clientes
def chegada_clientes(env, guiches):
    cliente_id = 0
    while True:
        yield env.timeout(random.expovariate(TAXA_CHEGADA))
        cliente_id += 1
        env.process(atendimento_cliente(env, cliente_id, guiches))
        eventos_tempo.append((env.now, len(guiches.queue)))

# Função principal
def simular():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    guiches = simpy.Resource(env, capacity=NUM_GUICHE)
    env.process(chegada_clientes(env, guiches))
    env.run(until=MINUTOS_FUNCIONAMENTO)

# Executa a simulação
simular()

# Resultados
print(f"Tempo médio de espera: {statistics.mean(tempos_espera):.2f} minutos")
print(f"Clientes atendidos: {clientes_atendidos}")
print(f"Clientes que desistiram: {clientes_desistiram}")

# Plotar gráfico
tempos, filas = zip(*eventos_tempo)
plt.figure(figsize=(10, 5))
plt.plot(tempos, filas, label="Número de clientes na fila")
plt.xlabel("Tempo (minutos)")
plt.ylabel("Tamanho da fila")
plt.title("Tamanho da fila ao longo do tempo")
plt.legend()
plt.grid(True)
plt.show()
