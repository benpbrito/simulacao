from flask import Flask, render_template, request, jsonify
import simpy
import random

app = Flask(__name__)

def simular_fila(taxa_chegada, tempo_atendimento, num_guiches, tempo_tolerancia):
    total_tempo = 480  # em minutos
    intervalo_coleta = 30

    stats = {
        "clientes_chegando": [],
        "clientes_atendidos": [],
        "clientes_desistentes": [],
        "media_espera": [],
        "total_chegaram": 0,
        "total_atendidos": 0,
        "total_desistentes": 0,
    }

    registro = {
        "chegaram": 0,
        "atendidos": 0,
        "desistentes": 0,
        "esperas": []
    }

    historico = []

    def cliente(env, nome, guiche, tempo_atendimento, tempo_tolerancia):
        chegada = env.now
        with guiche.request() as req:
            resultado = yield req | env.timeout(tempo_tolerancia)
            if req in resultado:
                espera = env.now - chegada
                registro["atendidos"] += 1
                registro["esperas"].append(espera)
                yield env.timeout(tempo_atendimento)
            else:
                registro["desistentes"] += 1

    def chegada_clientes(env):
        while env.now < total_tempo:
            yield env.timeout(random.expovariate(taxa_chegada / 60.0))
            registro["chegaram"] += 1
            env.process(cliente(env, f"Cliente{registro['chegaram']}", guiche, tempo_atendimento, tempo_tolerancia))

    def coleta_dados(env):
        while env.now <= total_tempo:
            yield env.timeout(intervalo_coleta)
            historico.append({
                "chegaram": registro["chegaram"],
                "atendidos": registro["atendidos"],
                "desistentes": registro["desistentes"],
                "esperas": list(registro["esperas"]),
            })

    env = simpy.Environment()
    guiche = simpy.Resource(env, capacity=num_guiches)

    env.process(chegada_clientes(env))
    env.process(coleta_dados(env))

    # Roda simulação principal
    env.run(until=total_tempo)

    # Espera todos os clientes serem atendidos ou desistirem
    while registro["chegaram"] > registro["atendidos"] + registro["desistentes"]:
        env.run(until=env.now + 1)

    # Coleta final
    historico.append({
        "chegaram": registro["chegaram"],
        "atendidos": registro["atendidos"],
        "desistentes": registro["desistentes"],
        "esperas": list(registro["esperas"]),
    })

    # Processar estatísticas finais
    tempos = list(range(intervalo_coleta, total_tempo + 1, intervalo_coleta))
    if len(historico) > len(tempos):  # garante que inclua a coleta final
        tempos.append(env.now)

    prev_cheg = prev_atend = prev_desist = 0
    prev_esperas = []

    for h in historico:
        cheg = h["chegaram"] - prev_cheg
        atend = h["atendidos"] - prev_atend
        desist = h["desistentes"] - prev_desist
        esperas = h["esperas"][len(prev_esperas):]

        stats["clientes_chegando"].append(cheg)
        stats["clientes_atendidos"].append(atend)
        stats["clientes_desistentes"].append(desist)
        media = round(sum(esperas) / len(esperas), 2) if esperas else 0
        stats["media_espera"].append(media)

        stats["total_chegaram"] += cheg
        stats["total_atendidos"] += atend
        stats["total_desistentes"] += desist

        prev_cheg = h["chegaram"]
        prev_atend = h["atendidos"]
        prev_desist = h["desistentes"]
        prev_esperas = h["esperas"]

    # Confirma consistência
    assert stats["total_chegaram"] == stats["total_atendidos"] + stats["total_desistentes"], \
        f"Inconsistência: {stats['total_chegaram']} ≠ {stats['total_atendidos']} + {stats['total_desistentes']}"

    return stats, tempos


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simular", methods=["POST"])
def simular():
    data = request.json
    taxa_chegada = float(data.get("taxaChegada", 30))
    tempo_atendimento = float(data.get("tempoAtendimento", 10))
    num_guiches = int(data.get("guiches", 2))
    tempo_desistencia = float(data.get("tempoDesistencia", 4))

    stats, tempos = simular_fila(taxa_chegada, tempo_atendimento, num_guiches, tempo_desistencia)
    return jsonify({"stats": stats, "tempos": tempos})

if __name__ == "__main__":
    app.run(debug=False)
