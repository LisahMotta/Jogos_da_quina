import random
from collections import Counter

grupos = {
    "A": list(range(1, 11)),
    "B": list(range(11, 21)),
    "C": list(range(21, 31)),
    "D": list(range(31, 41)),
    "E": list(range(41, 51)),
    "F": list(range(51, 61)),
    "G": list(range(61, 71)),
    "H": list(range(71, 81)),
}

padroes = [
    ["A", "C", "E", "G", "H"],
    ["A", "B", "D", "F", "H"],
    ["B", "C", "D", "E", "F"],
    ["A", "D", "E", "G", "H"],
]

def analisar_frequencia(resultados):
    todos = [n for jogo in resultados for n in jogo]
    return Counter(todos)

def escolher_numero(grupo, frequencia=None):
    if not frequencia:
        return random.choice(grupo)

    pesos = [frequencia.get(n, 1) for n in grupo]
    return random.choices(grupo, weights=pesos, k=1)[0]

def escolher_padrao():
    return random.choice(padroes)

def gerar_jogo_inteligente(frequencia=None):
    padrao = escolher_padrao()
    jogo = []

    for letra in padrao:
        grupo = grupos[letra]
        numero = escolher_numero(grupo, frequencia)
        jogo.append(numero)

    return sorted(jogo)

def validar_jogo(jogo):
    pares = sum(1 for n in jogo if n % 2 == 0)
    return pares in [2, 3]

def gerar_jogos_inteligentes(qtd, resultados_passados=None):
    jogos = []

    frequencia = None
    if resultados_passados:
        frequencia = analisar_frequencia(resultados_passados)

    while len(jogos) < qtd:
        jogo = gerar_jogo_inteligente(frequencia)

        if validar_jogo(jogo) and jogo not in jogos:
            jogos.append(jogo)

    return jogos