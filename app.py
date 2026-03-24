from flask import Flask, render_template, request, jsonify
from inteligencia import gerar_jogos_inteligentes
from gerador import gerar_jogos

app = Flask(__name__)

# Histórico de jogos gerados (em memória)
historico = []


# ================================
# 🏠 Página principal
# ================================
@app.route("/")
def index():
    return render_template("index.html")


# ================================
# 🎯 Gerar jogos (com modo)
# ================================
@app.route("/gerar", methods=["POST"])
def gerar():
    try:
        dados = request.get_json(force=True, silent=True) or {}

        qtd = int(dados.get("quantidade", 5))
        modo = dados.get("modo", "ia")

        if modo == "ia":
            jogos = gerar_jogos_inteligentes(qtd, resultados_passados=historico if historico else None)
        else:
            jogos = gerar_jogos(qtd)

        historico.extend(jogos)

        return jsonify(jogos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ================================
# 📋 Retornar histórico
# ================================
@app.route("/historico", methods=["GET"])
def get_historico():
    return jsonify(historico)


# ================================
# 🗑️ Limpar histórico
# ================================
@app.route("/historico", methods=["DELETE"])
def limpar_historico():
    historico.clear()
    return jsonify({"mensagem": "Histórico limpo com sucesso."})


# ================================
# ▶️ Rodar app
# ================================
if __name__ == "__main__":
    app.run(debug=True)
