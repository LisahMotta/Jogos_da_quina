import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from inteligencia import gerar_jogos_inteligentes
from gerador import gerar_jogos

app = Flask(__name__)

# ================================
# 🗄️ PostgreSQL
# ================================
DATABASE_URL = os.environ.get("DATABASE_URL")

_historico_mem = []  # fallback em memória


def get_db():
    if not DATABASE_URL:
        return None
    import psycopg2
    url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)


def init_db():
    conn = get_db()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id        SERIAL PRIMARY KEY,
                numeros   INTEGER[],
                modo      VARCHAR(10) DEFAULT 'normal',
                criado_em TIMESTAMP  DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        print("Banco inicializado.")
    except Exception as e:
        conn.rollback()
        # Race condition entre workers — tabela já existe, seguro continuar
        print(f"Aviso init_db (ignorado): {e}")
    finally:
        conn.close()


def salvar_jogos(jogos, modo):
    conn = get_db()
    if not conn:
        _historico_mem.extend(jogos)
        return
    try:
        cur = conn.cursor()
        for jogo in jogos:
            cur.execute(
                "INSERT INTO historico (numeros, modo) VALUES (%s, %s)",
                (jogo, modo)
            )
        conn.commit()
        cur.close()
    finally:
        conn.close()


def buscar_historico():
    conn = get_db()
    if not conn:
        return list(_historico_mem)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT numeros FROM historico ORDER BY criado_em DESC LIMIT 200"
        )
        rows = cur.fetchall()
        cur.close()
        return [list(row[0]) for row in rows]
    finally:
        conn.close()


def limpar_historico_db():
    conn = get_db()
    if not conn:
        _historico_mem.clear()
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM historico")
        conn.commit()
        cur.close()
    finally:
        conn.close()


init_db()


# ================================
# 📁 PWA na raiz
# ================================
@app.route("/sw.js")
def service_worker():
    resp = send_from_directory("static", "sw.js",
                               mimetype="application/javascript")
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json",
                               mimetype="application/manifest+json")


# ================================
# 🏠 Página principal
# ================================
@app.route("/")
def index():
    return render_template("index.html")


# ================================
# 🎯 Gerar jogos
# ================================
@app.route("/gerar", methods=["POST"])
def gerar():
    try:
        dados = request.get_json(force=True, silent=True) or {}
        qtd = min(int(dados.get("quantidade", 5)), 20)
        modo = dados.get("modo", "ia")

        historico = buscar_historico()

        if modo == "ia":
            jogos = gerar_jogos_inteligentes(
                qtd, resultados_passados=historico if historico else None
            )
        else:
            jogos = gerar_jogos(qtd)

        salvar_jogos(jogos, modo)
        return jsonify(jogos)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ================================
# 📋 Histórico
# ================================
@app.route("/historico", methods=["GET"])
def get_historico():
    return jsonify(buscar_historico())


@app.route("/historico", methods=["DELETE"])
def limpar():
    limpar_historico_db()
    return jsonify({"mensagem": "Histórico limpo."})


# ================================
# ❤️ Health check
# ================================
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ================================
# ▶️ Iniciar
# ================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port,
            debug=os.environ.get("FLASK_DEBUG") == "1")
