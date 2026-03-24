from flask import Flask, render_template, request, jsonify
from inteligencia import gerar_jogos_inteligentes
from gerador import gerar_jogos

app = Flask(__name__)

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
    dados = request.get_json()

    qtd = int(dados.get("quantidade", 5))
    modo = dados.get("modo", "ia")

    if modo == "ia":
        jogos = gerar_jogos_inteligentes(qtd)
    else:
        jogos = gerar_jogos(qtd)

    return jsonify(jogos)


# ================================
# ▶️ Rodar app
# ================================
if __name__ == "__main__":
    app.run(debug=True)