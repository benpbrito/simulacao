from flask import Flask, render_template, request, jsonify
import simpy
import random

app = Flask(__name__)

def simular_fila(taxa_chegada, tempo_atendimento, num_guiches, tempo_tolerancia):
    total_tempo = 480  # 8 horas (em minutos)
    intervalo_coleta = 30  # em minutos
    tempos = list(range(0, total_tempo + 1, intervalo_coleta))

    stats = {
        "clientes_chegando": [],
        "clientes_atendidos": [],
        "clientes_desistentes": [],
        "media_espera": [],
        "total_chegaram": 0,
        "total_atendidos": 0,
        "total_desistentes": 0,
    }

    chegadas_por_minuto = []

    def cliente(env, nome, guiche, tempo_atendimento, tempo_tolerancia, registro):
        chegada = env.now
        with guiche.request() as req:
            resultado = yield req | env.timeout(tempo_tolerancia)
            if req in resultado:
                # Foi atendido
                espera = env.now - chegada
                registro["atendidos"] += 1
                registro["esperas"].append(espera)
                yield env.timeout(tempo_atendimento)
            else:
                # Desistiu
                registro["desistentes"] += 1

    def chegada_clientes(env, taxa_chegada, guiche, tempo_atendimento, tempo_tolerancia, registro):
        while env.now < total_tempo:
            yield env.timeout(random.expovariate(taxa_chegada / 60.0))  # taxa por minuto
            registro["chegaram"] += 1
            env.process(cliente(
                env,
                f"Cliente{registro['chegaram']}",
                guiche,
                tempo_atendimento,
                tempo_tolerancia,
                registro
            ))

    for t in tempos:
        env = simpy.Environment()
        guiche = simpy.Resource(env, capacity=num_guiches)

        registro = {
            "chegaram": 0,
            "atendidos": 0,
            "desistentes": 0,
            "esperas": []
        }

        env.process(chegada_clientes(env, taxa_chegada, guiche, tempo_atendimento, tempo_tolerancia, registro))
        env.run(until=intervalo_coleta)

        stats["clientes_chegando"].append(registro["chegaram"])
        stats["clientes_atendidos"].append(registro["atendidos"])
        stats["clientes_desistentes"].append(registro["desistentes"])
        media_espera = round(sum(registro["esperas"]) / len(registro["esperas"]), 2) if registro["esperas"] else 0
        stats["media_espera"].append(media_espera)

        stats["total_chegaram"] += registro["chegaram"]
        stats["total_atendidos"] += registro["atendidos"]
        stats["total_desistentes"] += registro["desistentes"]

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
    tempo_desistencia = float(data.get("tempoDesistencia", 4))  # agora é tempo!

    stats, tempos = simular_fila(taxa_chegada, tempo_atendimento, num_guiches, tempo_desistencia)
    return jsonify({"stats": stats, "tempos": tempos})

if __name__ == "__main__":
    app.run(debug=False)
