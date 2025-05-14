from flask import Flask, render_template, request, jsonify
import simpy
import random

app = Flask(__name__)

def simular_fila(taxa_chegada, tempo_atendimento, num_guiches, taxa_desistencia):
    total_tempo = 480  # 8h em minutos
    tempos = list(range(0, total_tempo + 1, 30))  # de 30 em 30 min
    
    stats = {
        "clientes_chegando": [],
        "clientes_atendidos": [],
        "clientes_desistentes": [],
        "media_espera": [],
        "total_chegaram": 0,
        "total_atendidos": 0,
        "total_desistentes": 0,
    }
    
    for t in tempos:
        # Chegadas no intervalo - adiciona flutuação leve
        cheg = int(taxa_chegada * 0.5 * (1 + random.uniform(-0.2, 0.2)))
        if cheg < 0:
            cheg = 0
        
        # Clientes desistentes - arredonda para inteiro
        desist = int(round(cheg * taxa_desistencia))
        if desist > cheg:
            desist = cheg
        
        # Clientes atendidos = resto dos que chegaram
        atend = cheg - desist
        
        # Tempo médio de espera flutuante (não afetará a soma)
        espera = max(0, tempo_atendimento * (random.uniform(0.8, 1.2)))
        
        stats["clientes_chegando"].append(cheg)
        stats["clientes_desistentes"].append(desist)
        stats["clientes_atendidos"].append(atend)
        stats["media_espera"].append(round(espera, 2))
        
        stats["total_chegaram"] += cheg
        stats["total_desistentes"] += desist
        stats["total_atendidos"] += atend
    
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
    taxa_desistencia = float(data.get("taxaDesistencia", 0.15))
    
    stats, tempos = simular_fila(taxa_chegada, tempo_atendimento, num_guiches, taxa_desistencia)
    response = {
        "stats": stats,
        "tempos": tempos
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
